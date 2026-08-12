from bedrock_protocol.packets.types import ItemData
from bstream import BinaryStream
from endstone.inventory import ItemStack
from endstone_inventoryui.util import item_utils
from endstone_inventoryui.util.nbt_serializer import write_nbt


class ItemStackWrapper:
    stack_id: int
    item_stack: ItemStack
    data: ItemData

    def __init__(self, stack_id: int = 0, item_stack: ItemStack | None = None):
        from endstone_inventoryui.util.item_utils import get_item_data
        self.stack_id: int = stack_id
        self.item_stack: ItemStack = item_stack or ItemStack("minecraft:air")
        data = get_item_data(self.item_stack.type.id)
        if data is None:
            raise ValueError(f"ItemStackWrapper: ItemData not found for {self.item_stack.type.id}")
        self.data: ItemData = data

    def write_extra_data(self, stream: BinaryStream):
        """Writes the extra data buffer (NBT + canPlaceOn + canDestroy)"""
        tag = self.item_stack.nbt
        is_tag_empty = len(tag) == 0
        if not is_tag_empty:
            stream.write_signed_short(-1)  # nbt length
            stream.write_byte(1)  # nbt version?
            stream.write_raw_bytes(write_nbt(tag))
        else:
            stream.write_signed_short(0)  # no nbt

        stream.write_unsigned_int(0)  # canPlaceOn count
        stream.write_unsigned_int(0)  # canDestroy count

    def write(self, stream: BinaryStream):
        is_air = item_utils.is_air(self.item_stack)
        has_net_id = self.stack_id != 0

        stream.write_signed_short(self.data.item_id)
        stream.write_unsigned_short(self.item_stack.amount)
        stream.write_unsigned_varint(self.item_stack.data)

        stream.write_bool(has_net_id)
        if has_net_id:
            stream.write_varint(self.stack_id)

        stream.write_unsigned_varint(0)  # BlockRuntimeID
        if is_air:
            stream.write_unsigned_varint(0)
            return

        user_data = BinaryStream()
        self.write_extra_data(user_data)
        stream.write_bytes(user_data.get_and_release_data())