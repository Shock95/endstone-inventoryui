from bedrock_protocol.packets.minecraft_packet_ids import MinecraftPacketIds
from bedrock_protocol.packets.packet.packet_base import Packet
from bedrock_protocol.packets.types import FullContainerName
from bstream import BinaryStream, ReadOnlyBinaryStream

from endstone_inventoryui.network.item_stack_wrapper import ItemStackWrapper


class InventorySlotPacket(Packet):

    def __init__(self,
                 container_id: int = 0,
                 slot: int = 0,
                 container_name: FullContainerName | None = None,
                 storage: ItemStackWrapper | None = None,
                 item: ItemStackWrapper | None = None
                 ):
        super().__init__()
        self.container_id = container_id
        self.slot = slot
        self.container_name = container_name or FullContainerName()
        self.storage = storage or ItemStackWrapper()
        self.item = item or ItemStackWrapper()

    def get_packet_id(self) -> MinecraftPacketIds:
        return MinecraftPacketIds.InventorySlot

    def get_packet_name(self) -> str:
        return "InventorySlotPacket"

    def write(self, stream: BinaryStream) -> None:
        stream.write_unsigned_varint(self.container_id)
        stream.write_unsigned_varint(self.slot)
        self.container_name.write(stream)
        self.storage.write_header(stream)
        self.item.write(stream)

    def read(self, stream: ReadOnlyBinaryStream) -> None:
        pass
