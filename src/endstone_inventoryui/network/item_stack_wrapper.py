from bedrock_protocol.packets.types import ItemData
from bstream import BinaryStream
from endstone._internal.endstone_python import ItemStack

from endstone_inventoryui.util.item_utils import build_tag
from endstone_inventoryui.util.item_utils import is_air


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
            raise ValueError(f"ItemStackWrapper: ItemData not found for {item_stack.type.id}")
        self.data: ItemData = data

    def write_header(self, stream: BinaryStream) -> bool:
        if is_air(self.item_stack):
            stream.write_varint(0)
            return False
        stream.write_varint(self.data.item_id)
        stream.write_unsigned_short(self.item_stack.amount)
        stream.write_unsigned_varint(self.item_stack.data)
        return True

    def write_footer(self, stream: BinaryStream):
        """Builds the extra data buffer (NBT + canPlaceOn + canDestroy)"""
        item_meta = self.item_stack.item_meta
        tag = build_tag(item_meta)
        if not tag.empty():
            stream.write_signed_short(-1)  # nbt length
            stream.write_byte(1)  # nbt version?
            stream.write_raw_bytes(tag.to_binary_nbt())
        else:
            stream.write_signed_short(0)  # no nbt

        stream.write_unsigned_int(0)  # canPlaceOn count
        stream.write_unsigned_int(0)  # canDestroy count

    def write(self, stream: BinaryStream):
        if self.write_header(stream):
            has_net_id = self.stack_id != 0
            stream.write_bool(has_net_id)
            if has_net_id:
                stream.write_varint(self.stack_id)

            stream.write_varint(0)  # BlockRuntimeID

            user_data = BinaryStream()
            self.write_footer(user_data)
            stream.write_bytes(user_data.copy_buffer())  # user data
