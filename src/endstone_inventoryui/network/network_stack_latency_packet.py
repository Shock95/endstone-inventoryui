from bedrock_protocol.packets.minecraft_packet_ids import MinecraftPacketIds
from bedrock_protocol.packets.packet.packet_base import Packet
from bstream import BinaryStream, ReadOnlyBinaryStream


class NetworkStackLatencyPacket(Packet):
    timestamp: int
    from_server: bool

    def __init__(self, timestamp: int = 0, from_server: bool = False):
        super().__init__()
        self.timestamp = timestamp
        self.from_server = from_server

    def get_packet_id(self) -> MinecraftPacketIds:
        return MinecraftPacketIds.Ping

    def get_packet_name(self) -> str:
        return "NetworkStackLatencyPacket"

    def write(self, stream: BinaryStream) -> None:
        stream.write_unsigned_int64(self.timestamp)
        stream.write_bool(self.from_server)

    def read(self, stream: ReadOnlyBinaryStream) -> None:
        self.timestamp = stream.get_unsigned_int64()
        self.from_server = stream.get_bool()
