from ctypes import c_int16

from bedrock_protocol.packets.types import ItemData
from endstone._internal.endstone_python import ItemStack, ItemMeta
from rapidnbt import CompoundTag, ListTag

enchant_map = {
    "protection": 0,
    "fire_protection": 1,
    "feather_falling": 2,
    "blast_protection": 3,
    "projectile_protection": 4,
    "thorns": 5,
    "respiration": 6,
    "depth_strider": 7,
    "aqua_affinity": 8,
    "sharpness": 9,
    "smite": 10,
    "bane_of_arthropods": 11,
    "knockback": 12,
    "fire_aspect": 13,
    "looting": 14,
    "efficiency": 15,
    "silk_touch": 16,
    "unbreaking": 17,
    "fortune": 18,
    "power": 19,
    "punch": 20,
    "flame": 21,
    "infinity": 22,
    "luck_of_the_sea": 23,
    "lure": 24,
    "frost_walker": 25,
    "mending": 26,
    "binding": 27,
    "vanishing": 28,
    "impaling": 29,
    "riptide": 30,
    "loyalty": 31,
    "channeling": 32,
    "multishot": 33,
    "piercing": 34,
    "quick_charge": 35,
    "soul_speed": 36,
    "swift_sneak": 37,
    "wind_burst": 38,
    "density": 39,
    "breach": 40,
}

cached_items: dict[str, ItemData] = {}


def is_air(item_stack: ItemStack) -> bool:
    return item_stack.type.id == "minecraft:air"


def clone_item(item_stack: ItemStack) -> ItemStack:
    new_item = ItemStack(item_stack.type.id, item_stack.amount, item_stack.data)
    new_item.set_item_meta(item_stack.item_meta.clone())
    return new_item


def all_item_data() -> dict[str, ItemData]:
    return cached_items


def add_item_data(item_id: str, data: ItemData) -> None:
    cached_items[item_id] = data


def get_item_data(item_id: str) -> ItemData | None:
    return cached_items.get(item_id)


def get_enchant_type(enchant: str):
    global enchant_map
    return enchant_map.get(enchant, 42)  # 42 = InvalidEnchantment


def build_tag(item_meta: ItemMeta) -> CompoundTag:
    """Build the NBT compound tag for item metadata"""
    tag = CompoundTag()
    if item_meta.has_display_name or item_meta.has_lore:
        display_tag = CompoundTag()
        if item_meta.has_display_name:
            display_tag.set("Name", item_meta.display_name)
        if item_meta.has_lore:
            lore_list = ListTag()
            for lore_line in item_meta.lore:
                lore_list.append(lore_line)
            display_tag.set("Lore", lore_list)
        tag.set("display", display_tag)

    if item_meta.has_enchants:
        ench_list = ListTag()
        for enchant, level in item_meta.enchants.items():
            ench_tag = CompoundTag()
            ench_tag.set("id", c_int16(get_enchant_type(enchant)))
            ench_tag.set("lvl", c_int16(level))
            ench_list.append(ench_tag)
        tag.set("ench", ench_list)

    if item_meta.has_repair_cost:
        tag.set("RepairCost", item_meta.repair_cost)

    if item_meta.is_unbreakable:
        tag.set("Unbreakable", 1)
    return tag
