from bedrock_protocol.packets.packet import BlockActorDataPacket, ContainerOpenPacket
from bedrock_protocol.packets.types import BlockPos, NetworkBlockPosition
from endstone import Player
from rapidnbt import CompoundTag

from endstone_inventoryui.menu import Menu
from endstone_inventoryui.menu.graphic.graphic import Graphic
from endstone_inventoryui.util.utils import send_block


class BlockGraphic(Graphic):
    menu: Menu
    pos: BlockPos

    def __init__(self, menu: Menu, pos: BlockPos):
        self.menu = menu
        self.pos = pos

    def send(self, player: Player):
        send_block(player, self.menu.type.get_block_id(), self.pos)

    def send_data(self, player: Player):
        tag = CompoundTag()
        pos = self.pos
        tag.set("id", self.menu.type.get_block_actor_id())
        tag.set("CustomName", self.menu.name)
        pk = BlockActorDataPacket(NetworkBlockPosition(pos.x, pos.y, pos.z), tag)
        player.send_packet(pk.get_packet_id(), pk.serialize())

    def open(self, player: Player):
        from endstone_inventoryui.manager import Session
        pos = NetworkBlockPosition(self.pos.x, self.pos.y, self.pos.z)
        pk = ContainerOpenPacket(Session.CONTAINER_ID, self.menu.type.get_container_type(), pos)
        player.send_packet(pk.get_packet_id(), pk.serialize())

    def remove(self, player: Player):
        block = player.dimension.get_block_at(self.pos.x, self.pos.y, self.pos.z)
        send_block(player, block.type, self.pos)
