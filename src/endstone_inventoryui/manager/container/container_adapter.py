from typing import Protocol, TYPE_CHECKING

from endstone import Player
from endstone.inventory import ItemStack

if TYPE_CHECKING:
    from endstone_inventoryui.menu.inventory import MenuInventory


class ContainerAdapter(Protocol):
    def get(self, slot: int) -> ItemStack | None: ...
    def set(self, slot: int, item: ItemStack | None) -> None: ...


class PlayerInventoryAdapter:
    def __init__(self, player: Player):
        self.player = player

    def get(self, slot: int) -> ItemStack | None:
        return self.player.inventory.get_item(slot)

    def set(self, slot: int, item: ItemStack | None) -> None:
        if item is None:
            self.player.inventory.clear(slot)
        else:
            self.player.inventory.set_item(slot, item)


class VirtualInventoryAdapter:
    def __init__(self, inventory: "MenuInventory"):
        self.inventory = inventory

    def get(self, slot: int) -> ItemStack | None:
        return self.inventory.get_item(slot)

    def set(self, slot: int, item: ItemStack | None) -> None:
        if item is None:
            self.inventory.clear(slot)
        else:
            self.inventory.set_item(slot, item)


class CursorAdapter:

    def __init__(self):
        self.cursor_item: ItemStack | None = None

    def get(self, slot: int = 0) -> ItemStack | None:
        return self.cursor_item

    def set(self, slot: int, item: ItemStack | None) -> None:
        self.cursor_item = item
