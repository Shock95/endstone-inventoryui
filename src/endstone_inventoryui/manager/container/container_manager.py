from typing import TYPE_CHECKING

from bedrock_protocol.packets.types import ItemStackRequestSlotInfo
from bedrock_protocol.packets.types.item_stack_response import ItemStackResponse
from endstone import Player
from endstone.inventory import ItemStack
from endstone_inventoryui.network.container_ui_ids import ContainerUIIds
from endstone_inventoryui.util.item_utils import pop_item, can_stack, clone_item, is_air

from .container_adapter import ContainerAdapter, PlayerInventoryAdapter, VirtualInventoryAdapter, CursorAdapter
from .transaction_container import TransactionContainer
from .item_stack_response_builder import ItemStackResponseBuilder
from .item_stack_tracker import ItemStackTracker

if TYPE_CHECKING:
    from endstone_inventoryui import MenuInventory


class ContainerManager:

    def __init__(self, player: Player, inventory: "MenuInventory"):
        self.player = player
        self.tracker = ItemStackTracker()
        self.player_container = TransactionContainer(PlayerInventoryAdapter(player))
        self.virtual_container = TransactionContainer(VirtualInventoryAdapter(inventory))
        self.cursor_container = TransactionContainer(CursorAdapter())
        self._response_builder: ItemStackResponseBuilder | None = None
        self._modified_player_slots: set[int] = set()

    def begin_request(self, request_id: int) -> None:
        self._response_builder = ItemStackResponseBuilder(request_id, self.tracker, self)

    @staticmethod
    def _is_player_container(container_enum: int) -> bool:
        return container_enum in (
            ContainerUIIds.INVENTORY,
            ContainerUIIds.HOTBAR,
            ContainerUIIds.COMBINED_HOTBAR_AND_INVENTORY,
        )

    def track_request_slot(self, slot_info: ItemStackRequestSlotInfo) -> None:
        self.tracker.seed_from_request(slot_info)
        if self._is_player_container(slot_info.container.container_enum):
            self._modified_player_slots.add(slot_info.slot)
        if self._response_builder is not None:
            self._response_builder.add_slot(slot_info.container.container_enum, slot_info.slot)

    def get_container_adapter_and_slot(self, slot_info: ItemStackRequestSlotInfo) -> tuple[ContainerAdapter, int] | None:
        container_type = slot_info.container.container_enum
        slot = slot_info.slot
        if container_type == ContainerUIIds.LEVEL_ENTITY:
            return self.virtual_container, slot
        elif container_type == ContainerUIIds.CURSOR:
            return self.cursor_container, slot
        elif container_type in (ContainerUIIds.INVENTORY, ContainerUIIds.HOTBAR, ContainerUIIds.COMBINED_HOTBAR_AND_INVENTORY):
            return self.player_container, slot
        raise ValueError(f"Unsupported container type: {container_type}")

    def get_item_at(self, container_enum: int, slot: int) -> ItemStack | None:
        if container_enum == ContainerUIIds.LEVEL_ENTITY:
            return self.virtual_container.actual.get(slot)
        if container_enum == ContainerUIIds.CURSOR:
            return self.cursor_container.actual.get(slot)
        if container_enum in (ContainerUIIds.INVENTORY, ContainerUIIds.HOTBAR, ContainerUIIds.COMBINED_HOTBAR_AND_INVENTORY):
            return self.player_container.actual.get(slot)
        raise ValueError(f"Unsupported container type: {container_enum}")

    def assign_virtual_slot(self, slot: int, item: ItemStack | None) -> int:
        return self.tracker.assign_slot(ContainerUIIds.LEVEL_ENTITY, slot, item)

    def transfer_items(self, source: ItemStackRequestSlotInfo, destination: ItemStackRequestSlotInfo, count: int):
        self.track_request_slot(source)
        self.track_request_slot(destination)
        removed = self.remove_item_from_slot(source, count)
        self.add_item_to_slot(destination, removed, count)

    def remove_item_from_slot(self, slot_info: ItemStackRequestSlotInfo, count: int) -> ItemStack:
        self.track_request_slot(slot_info)
        container, slot = self.get_container_adapter_and_slot(slot_info)
        if count < 1:
            raise ValueError("item count is less than 1")

        item: ItemStack = container.get(slot)
        if item is None or item.amount < count:
            raise ValueError("item is None or existing item < count")

        removed, remainder = pop_item(item, count)

        if remainder is None or is_air(remainder):
            container.set(slot, None)
        else:
            container.set(slot, remainder)

        return removed

    def add_item_to_slot(self, slot_info: ItemStackRequestSlotInfo, item: ItemStack, count: int):
        self.track_request_slot(slot_info)
        if item is None or is_air(item):
            raise ValueError("item is None or existing item < count")

        container, slot = self.get_container_adapter_and_slot(slot_info)
        if count < 1:
            return

        existing_item : ItemStack = container.get(slot) or ItemStack("minecraft:air")

        if existing_item is None or is_air(existing_item):
            container.set(slot, clone_item(item))
            return

        if not can_stack(existing_item, item):
            raise ValueError("cannot stack items")

        merged = clone_item(existing_item)
        merged.amount += item.amount

        container.set(slot, merged)

    def handle_swap(self, slot1: ItemStackRequestSlotInfo, slot2: ItemStackRequestSlotInfo):
        self.track_request_slot(slot1)
        self.track_request_slot(slot2)
        c1, s1 = self.get_container_adapter_and_slot(slot1)
        c2, s2 = self.get_container_adapter_and_slot(slot2)

        item1 = c1.get(s1)
        item2 = c2.get(s2)
        c1.set(s1, item2)
        c2.set(s2, item1)

    def handle_drop(self, source: ItemStackRequestSlotInfo, count: int):
        self.track_request_slot(source)
        dropped = self.remove_item_from_slot(source, count)
        if is_air(dropped):
            raise ValueError("cannot drop empty item stack")
        if dropped.amount > dropped.max_stack_size:
            raise ValueError("cannot drop item stack larger than max stack size")

        self.player.dimension.drop_item(self.player.location, dropped)

    def commit_transaction(self) -> ItemStackResponse:
        self.player_container.commit()
        self.virtual_container.commit()
        self.cursor_container.commit()

        if self._response_builder is None:
            raise RuntimeError("No active item stack request")

        for container_enum, slots in self._response_builder.changed_slots().items():
            for slot in slots.values():
                item = self.get_item_at(container_enum, slot)
                self.tracker.assign_slot(container_enum, slot, item)

        response = self._response_builder.build()
        self._response_builder = None
        return response

    def discard_transaction(self) -> None:
        self.player_container.discard()
        self.virtual_container.discard()
        self.cursor_container.discard()
        self._response_builder = None

    def sync_player_inventory(self) -> None:
        if not self._modified_player_slots:
            return
        inventory = self.player.inventory
        for slot in self._modified_player_slots:
            item = inventory.get_item(slot)
            inventory.clear(slot)
            if item is not None and not is_air(item):
                inventory.set_item(slot, clone_item(item))
        self._modified_player_slots.clear()
        self.tracker.clear_player_slots()
