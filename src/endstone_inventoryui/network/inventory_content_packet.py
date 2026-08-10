from bedrock_protocol.packets.minecraft_packet_ids import MinecraftPacketIds
from bedrock_protocol.packets.packet.packet_base import Packet
from bedrock_protocol.packets.types import FullContainerName
from bstream import BinaryStream, ReadOnlyBinaryStream

from endstone_inventoryui.network.item_stack_wrapper import ItemStackWrapper


class InventoryContentPacket(Packet):

    def __init__(self,
                 container_id: int = 0,
                 items: list[ItemStackWrapper] | None = None,
                 container_name: FullContainerName | None = None,
                 storage: ItemStackWrapper | None = None
                 ):
        super().__init__()
        self.container_id = container_id
        self.items = items or []
        self.container_name = container_name or FullContainerName()
        self.storage = storage or ItemStackWrapper()

    def get_packet_id(self) -> MinecraftPacketIds:
        return MinecraftPacketIds.InventoryContent

    def get_packet_name(self) -> str:
        return "InventoryContentPacket"

    def write(self, stream: BinaryStream) -> None:
        stream.write_unsigned_varint(self.container_id)
        stream.write_unsigned_varint(len(self.items))
        for item in self.items:
            item.write(stream)
        self.container_name.write(stream)
        self.storage.write(stream)

    def read(self, stream: ReadOnlyBinaryStream) -> None:
        self.container_id = stream.get_unsigned_varint()
        pass
