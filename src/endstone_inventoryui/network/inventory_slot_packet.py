from dataclasses import field, dataclass

from bedrock_protocol.packets.minecraft_packet_ids import MinecraftPacketIds
from bedrock_protocol.packets.packet.packet_base import Packet
from bedrock_protocol.packets.types import FullContainerName
from bstream import BinaryStream, ReadOnlyBinaryStream

from endstone_inventoryui.network.item_stack_wrapper import ItemStackWrapper


@dataclass
class InventorySlotPacket(Packet):
    container_id: int = 0
    slot: int = 0
    container_name: FullContainerName | None = None
    storage: ItemStackWrapper | None = None
    item: ItemStackWrapper = field(default_factory=ItemStackWrapper)

    def get_packet_id(self) -> MinecraftPacketIds:
        return MinecraftPacketIds.InventorySlot

    def get_packet_name(self) -> str:
        return "InventorySlotPacket"

    def write(self, stream: BinaryStream) -> None:
        stream.write_unsigned_varint(self.container_id)
        stream.write_unsigned_varint(self.slot)

        stream.write_bool(self.container_name is not None)
        if self.container_name is not None:
            self.container_name.write(stream)

        stream.write_bool(self.storage is not None)
        if self.storage is not None:
            self.storage.write(stream)

        self.item.write(stream)

    def read(self, stream: ReadOnlyBinaryStream) -> None:
        pass
