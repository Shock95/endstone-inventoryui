from typing import overload, Callable

from endstone._internal.endstone_python import ItemStack

from endstone_inventoryui.util.item_utils import clone_item


class UIInventory:
    """
    Inventory used for menus

    Based on Endstone's inventory interface
    """

    def __init__(self, size: int = 36, max_stack_size: int = 64,
                 slot_updated: Callable[[int], None] | None = None):
        self._size = size
        self._max_stack_size = max_stack_size
        self._slots: list[ItemStack | None] = [None] * size
        self._slot_updated = slot_updated

    def _notify_slot_update(self, index: int) -> None:
        """Calls the slot_updated callback if one is registered."""
        if self._slot_updated is not None:
            self._slot_updated(index)

    @property
    def size(self) -> int:
        """Returns the size of the inventory"""
        return self._size

    @property
    def max_stack_size(self) -> int:
        """Returns the maximum stack size for an ItemStack in this inventory."""
        return self._max_stack_size

    def get_item(self, index: int) -> ItemStack:
        """Returns the ItemStack found in the slot at the given index"""
        if not 0 <= index < self._size:
            raise IndexError(f"Slot index {index} out of range")
        item = self._slots[index]
        if item is None:
            return ItemStack("minecraft:air")
        return item

    def set_item(self, index: int, item: ItemStack) -> None:
        """Stores the ItemStack at the given index of the inventory."""
        if not 0 <= index < self._size:
            raise IndexError(f"Slot index {index} out of range")
        self._slots[index] = item
        self._notify_slot_update(index)

    def add_item(self, *args: ItemStack) -> dict[int, ItemStack]:
        """
        Stores the given ItemStacks in the inventory.
        Tries to fill existing stacks and empty slots.
        Returns what couldn't be stored.
        """
        leftover = {}
        for i, item in enumerate(args):
            if item is None or item.amount <= 0:
                continue
            remaining = clone_item(item)

            for slot_idx in range(self._size):
                if remaining.amount <= 0:
                    break
                slot_item = self._slots[slot_idx]
                if slot_item is not None and slot_item.is_similar(remaining):
                    max_add = min(remaining.amount,
                                  min(self._max_stack_size, slot_item.max_stack_size) - slot_item.amount)
                    if max_add > 0:
                        slot_item.amount += max_add
                        remaining.amount -= max_add
                        self._notify_slot_update(slot_idx)

            for slot_idx in range(self._size):
                if remaining.amount <= 0:
                    break
                if self._slots[slot_idx] is None:
                    max_add = min(remaining.amount,
                                  min(self._max_stack_size, remaining.max_stack_size))
                    new_item = clone_item(remaining)
                    new_item.amount = max_add
                    self._slots[slot_idx] = new_item
                    remaining.amount -= max_add
                    self._notify_slot_update(slot_idx)
            if remaining.amount > 0:
                leftover[i] = remaining
        return leftover

    def remove_item(self, *args: ItemStack) -> dict[int, ItemStack]:
        """
        Removes the given ItemStacks from the inventory.
        Returns what couldn't be removed.
        """
        leftover = {}
        for i, item in enumerate(args):
            if item is None or item.amount <= 0:
                continue
            to_remove = item.amount
            for slot_idx in range(self._size):
                if to_remove <= 0:
                    break
                slot_item = self._slots[slot_idx]
                if slot_item is not None and slot_item.is_similar(item):
                    removed = min(to_remove, slot_item.amount)
                    slot_item.amount -= removed
                    to_remove -= removed
                    if slot_item.amount <= 0:
                        self._slots[slot_idx] = None
                    self._notify_slot_update(slot_idx)
            if to_remove > 0:
                leftover_item = clone_item(item)
                leftover_item.amount = to_remove
                leftover[i] = leftover_item
        return leftover

    @property
    def contents(self) -> list[ItemStack]:
        """Returns all ItemStacks from the inventory"""
        return self._slots.copy()

    @contents.setter
    def contents(self, items: list[ItemStack]) -> None:
        for i in range(self._size):
            old_item = self._slots[i]
            new_item = items[i] if i < len(items) else None
            self._slots[i] = new_item
            if old_item != new_item:
                self._notify_slot_update(i)

    @overload
    def contains(self, item: ItemStack, amount: int) -> bool:
        ...

    @overload
    def contains(self, item: ItemStack) -> bool:
        ...

    @overload
    def contains(self, type: str) -> bool:
        ...

    def contains(self, item, amount: int = None) -> bool:
        if isinstance(item, str):
            # Check by type
            return any(s is not None and s.type == item for s in self._slots)
        elif isinstance(item, ItemStack):
            if amount is not None:
                # Count exact matches
                count = sum(1 for s in self._slots if s is not None and s == item)
                return count >= amount
            else:
                return any(s is not None and s == item for s in self._slots)
        return False

    @overload
    def contains_at_least(self, item: ItemStack, amount: int) -> bool:
        ...

    @overload
    def contains_at_least(self, type: str, amount: int) -> bool:
        ...

    def contains_at_least(self, item, amount: int) -> bool:
        if isinstance(item, str):
            total = sum(s.amount for s in self._slots if s is not None and s.type == item)
            return total >= amount
        elif isinstance(item, ItemStack):
            total = sum(s.amount for s in self._slots if s is not None and s.is_similar(item))
            return total >= amount
        return False

    @overload
    def all(self, item: ItemStack) -> dict[int, ItemStack]:
        ...

    @overload
    def all(self, type: str) -> dict[int, ItemStack]:
        ...

    def all(self, item) -> dict[int, ItemStack]:
        result = {}
        if isinstance(item, str):
            for i, s in enumerate(self._slots):
                if s is not None and s.type == item:
                    result[i] = s
        elif isinstance(item, ItemStack):
            for i, s in enumerate(self._slots):
                if s is not None and s == item:
                    result[i] = s
        return result

    @overload
    def first(self, item: ItemStack) -> int:
        ...

    @overload
    def first(self, type: str) -> int:
        ...

    def first(self, item) -> int:
        if isinstance(item, str):
            for i, s in enumerate(self._slots):
                if s is not None and s.type == item:
                    return i
        elif isinstance(item, ItemStack):
            for i, s in enumerate(self._slots):
                if s is not None and s == item:
                    return i
        return -1

    @property
    def first_empty(self) -> int:
        """Returns the first empty Slot."""
        for i, s in enumerate(self._slots):
            if s is None:
                return i
        return -1

    @property
    def is_empty(self) -> bool:
        """Check whether this inventory is empty."""
        return all(s is None for s in self._slots)

    @overload
    def remove(self, item: ItemStack) -> None:
        ...

    @overload
    def remove(self, type: str) -> None:
        ...

    def remove(self, item) -> None:
        if isinstance(item, str):
            for i, s in enumerate(self._slots):
                if s is not None and s.type == item:
                    self._slots[i] = None
                    self._notify_slot_update(i)
        elif isinstance(item, ItemStack):
            for i, s in enumerate(self._slots):
                if s is not None and s == item:
                    self._slots[i] = None
                    self._notify_slot_update(i)

    @overload
    def clear(self, index: int) -> None:
        ...

    @overload
    def clear(self) -> None:
        ...

    def clear(self, index: int = None) -> None:
        if index is not None:
            if 0 <= index < self._size:
                if self._slots[index] is not None:
                    self._slots[index] = None
                    self._notify_slot_update(index)
        else:
            for i in range(self._size):
                if self._slots[i] is not None:
                    self._slots[i] = None
                    self._notify_slot_update(i)

    def __len__(self) -> int:
        return self._size

    def __getitem__(self, index: int) -> ItemStack:
        return self.get_item(index)

    def __setitem__(self, index: int, item: ItemStack) -> None:
        self.set_item(index, item)

    def __contains__(self, item) -> bool:
        return self.contains(item)
