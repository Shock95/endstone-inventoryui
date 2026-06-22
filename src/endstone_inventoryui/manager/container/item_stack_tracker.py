from bedrock_protocol.packets.types import ItemStackRequestSlotInfo
from endstone.inventory import ItemStack

from endstone_inventoryui.network.container_ui_ids import ContainerUIIds
from endstone_inventoryui.util.item_utils import is_air


class ItemStackTracker:
    def __init__(self):
        self._next_stack_id = 1
        self._stack_ids: dict[tuple[int, int], int] = {}

    def seed_from_request(self, slot_info: ItemStackRequestSlotInfo) -> None:
        key = (slot_info.container.container_enum, slot_info.slot)
        if key in self._stack_ids:
            return
        if slot_info.net_id > 0:
            self._stack_ids[key] = slot_info.net_id
            self._next_stack_id = max(self._next_stack_id, slot_info.net_id + 1)

    def assign_slot(self, container_enum: int, slot: int, item: ItemStack | None) -> int:
        if item is None or is_air(item):
            stack_id = 0
        else:
            stack_id = self._next_stack_id
            self._next_stack_id += 1
        self._stack_ids[(container_enum, slot)] = stack_id
        return stack_id

    def get_stack_id(self, container_enum: int, slot: int) -> int:
        return self._stack_ids.get((container_enum, slot), 0)

    def clear_player_slots(self) -> None:
        player_containers = (
            ContainerUIIds.INVENTORY,
            ContainerUIIds.HOTBAR,
            ContainerUIIds.COMBINED_HOTBAR_AND_INVENTORY,
        )
        self._stack_ids = {
            key: stack_id
            for key, stack_id in self._stack_ids.items()
            if key[0] not in player_containers
        }
