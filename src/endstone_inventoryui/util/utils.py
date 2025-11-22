import math
import random

from bedrock_protocol.packets.packet import UpdateBlockPacket
from bedrock_protocol.packets.types import BlockPos, NetworkBlockPosition
from endstone import Player, Server

from endstone_inventoryui.network.network_stack_latency_packet import NetworkStackLatencyPacket

server: Server | None = None


def send_ack_packet(player: Player) -> int:
    """
    Sends a ping packet the client is expected to respond to

    :param player: Player
    :returns: Timestamp value expected to be sent by the player
    """
    timestamp = random.randint(1, 32767)
    pk = NetworkStackLatencyPacket(timestamp, True)
    player.send_packet(pk.get_packet_id(), pk.serialize())
    return timestamp * 1_000_000


def send_block(player: Player, name: str, pos: BlockPos):
    block_data = player.server.create_block_data(name)
    pk = UpdateBlockPacket(NetworkBlockPosition(pos.x, pos.y, pos.z), block_data.runtime_id, 0b0010, 0)
    player.send_packet(pk.get_packet_id(), pk.serialize())


def get_block_behind(player: Player, distance: int = 1) -> BlockPos:
    location = player.location
    yaw = location.yaw

    behind_yaw = yaw + 180
    yaw_rad = math.radians(behind_yaw)
    x = -math.sin(yaw_rad) * distance
    z = math.cos(yaw_rad) * distance

    behind_x = location.x + x
    behind_y = location.y + 1
    behind_z = location.z + z

    return BlockPos(math.floor(behind_x), math.floor(behind_y), math.floor(behind_z))


def west(pos: BlockPos) -> BlockPos:
    return BlockPos(pos.x - 1, pos.y, pos.z)


def east(pos: BlockPos) -> BlockPos:
    return BlockPos(pos.x + 1, pos.y, pos.z)
