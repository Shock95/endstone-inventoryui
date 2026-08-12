from endstone.inventory import ItemStack
from bedrock_protocol.packets.types import ItemData

cached_items: dict[str, ItemData] = {}

def is_air(item_stack: ItemStack) -> bool:
    return item_stack.type.id == "minecraft:air"


def clone_item(item_stack: ItemStack) -> ItemStack:
    new_item = ItemStack(item_stack.type.id, item_stack.amount, item_stack.data)
    if item_stack.item_meta is not None:
        new_item.set_item_meta(item_stack.item_meta.clone())
    return new_item


def pop_item(item_stack: ItemStack, count: int) -> tuple[ItemStack, ItemStack | None]:
    if count < 1:
        raise ValueError("count must be > 0")

    if count > item_stack.amount:
        raise ValueError(f"Cannot pop {count} items from stack of {item_stack.amount}")

    removed = clone_item(item_stack)
    removed.amount = count
    remaining = item_stack.amount - count
    if remaining == 0:
        return removed, None
    remainder = clone_item(item_stack)
    remainder.amount = remaining
    return removed, remainder


def can_stack(item1: ItemStack, item2: ItemStack) -> bool:
    return item1.is_similar(item2)


def all_item_data() -> dict[str, ItemData]:
    return cached_items


def add_item_data(item_id: str, data: ItemData) -> None:
    cached_items[item_id] = data


def get_item_data(item_id: str) -> ItemData | None:
    return cached_items.get(item_id)
