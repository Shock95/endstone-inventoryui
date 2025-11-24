from bedrock_protocol.packets.packet import BlockActorDataPacket, ContainerOpenPacket
from bedrock_protocol.packets.types import BlockPos, NetworkBlockPosition
from endstone import Player
from rapidnbt import CompoundTag

from endstone_inventoryui.menu import Menu
from endstone_inventoryui.menu.graphic.graphic import Graphic
from endstone_inventoryui.util.utils import east, west, send_block


class BlockPairGraphic(Graphic):
    menu: Menu
    pos: tuple[BlockPos, BlockPos]

    def __init__(self, menu: Menu, pos: BlockPos):
        self.menu = menu
        if (pos.x & 1) == 1:
            self.pos = (pos, east(pos))
        else:
            self.pos = (pos, west(pos))

    def send(self, player: Player):
        for p in self.pos:
            send_block(player, self.menu.type.block_id, p)

    def send_data(self, player: Player):
        for p in self.pos:
            tag = CompoundTag()
            tag.set("id", self.menu.type.block_actor_id)
            tag.set("CustomName", self.menu.name)
            pk = BlockActorDataPacket(NetworkBlockPosition(p.x, p.y, p.z), tag)
            player.send_packet(pk.get_packet_id(), pk.serialize())

    def open(self, player: Player):
        from endstone_inventoryui.manager import Session
        pos, _ = self.pos
        net_pos = NetworkBlockPosition(pos.x, pos.y, pos.z)
        pk = ContainerOpenPacket(Session.CONTAINER_ID, self.menu.type.container_type, net_pos)
        player.send_packet(pk.get_packet_id(), pk.serialize())

    def remove(self, player: Player):
        for p in self.pos:
            block = player.dimension.get_block_at(p.x, p.y, p.z)
            send_block(player, block.type, p)
