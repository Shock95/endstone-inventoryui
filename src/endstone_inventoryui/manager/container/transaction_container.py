from endstone.inventory import ItemStack

from endstone_inventoryui.manager.container.container_adapter import ContainerAdapter
from endstone_inventoryui.util.item_utils import is_air, clone_item


class TransactionContainer:
    def __init__(self, actual: ContainerAdapter):
        self.actual = actual
        self.changed_slots: dict[int, ItemStack | None] = {}

    def get(self, slot: int) -> ItemStack | None:
        if slot in self.changed_slots:
            item = self.changed_slots[slot]
        else:
            item = self.actual.get(slot)

        if item is None or is_air(item):
            return item

        return clone_item(item)

    def set(self, slot: int, item: ItemStack | None) -> None:
        if item is None or is_air(item):
            self.changed_slots[slot] = None
        else:
            self.changed_slots[slot] = clone_item(item)

    def commit(self) -> None:
        for slot, item in self.changed_slots.items():
            self.actual.set(slot, item)
        self.changed_slots.clear()

    def discard(self) -> None:
        self.changed_slots.clear()
