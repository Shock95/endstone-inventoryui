from typing import TYPE_CHECKING

from bedrock_protocol.packets.types import FullContainerName
from bedrock_protocol.packets.types.item_stack_response import (
    ItemStackResponse,
    ItemStackResponseContainerInfo,
    ItemStackResponseSlotInfo,
)
from endstone.inventory import ItemStack

from endstone_inventoryui.util.item_utils import is_air

from .item_stack_tracker import ItemStackTracker

if TYPE_CHECKING:
    from .container_manager import ContainerManager


class ItemStackResponseBuilder:
    def __init__(self, request_id: int, tracker: ItemStackTracker, container_manager: "ContainerManager"):
        self._request_id = request_id
        self._tracker = tracker
        self._container_manager = container_manager
        self._changed_slots: dict[int, dict[int, int]] = {}

    def add_slot(self, container_enum: int, slot: int) -> None:
        self._changed_slots.setdefault(container_enum, {})[slot] = slot

    @staticmethod
    def _get_custom_name(item: ItemStack | None) -> str:
        if item is None or is_air(item):
            return ""
        item_meta = item.item_meta
        if item_meta is not None and item_meta.has_display_name:
            return item_meta.display_name
        return ""

    @staticmethod
    def _get_durability_correction(item: ItemStack | None) -> int:
        if item is None or is_air(item):
            return 0
        return item.data

    def build(self) -> ItemStackResponse:
        container_infos: list[ItemStackResponseContainerInfo] = []

        for container_enum, slots in self._changed_slots.items():
            slot_infos: list[ItemStackResponseSlotInfo] = []
            for slot in slots.values():
                item = self._container_manager.get_item_at(container_enum, slot)
                stack_id = self._tracker.get_stack_id(container_enum, slot)
                custom_name = self._get_custom_name(item)
                slot_infos.append(ItemStackResponseSlotInfo(
                    slot=slot,
                    hotbar_slot=slot,
                    count=0 if item is None or is_air(item) else item.amount,
                    item_stack_id=stack_id,
                    custom_name=custom_name,
                    filtered_custom_name=custom_name,
                    durability_correction=self._get_durability_correction(item),
                ))

            container_infos.append(ItemStackResponseContainerInfo(
                container=FullContainerName(container_enum),
                slots=slot_infos,
            ))

        return ItemStackResponse(
            result=ItemStackResponse.RESULT_OK,
            request_id=self._request_id,
            container_infos=container_infos,
        )

    def changed_slots(self) -> dict[int, dict[int, int]]:
        return self._changed_slots

    @classmethod
    def build_error(cls, request_id: int) -> ItemStackResponse:
        return ItemStackResponse(
            result=ItemStackResponse.RESULT_ERROR,
            request_id=request_id,
        )
