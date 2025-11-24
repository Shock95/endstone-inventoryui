from collections import deque
from enum import Enum
from typing import TYPE_CHECKING

from bedrock_protocol.packets.types import BlockPos
from endstone import Player

from endstone_inventoryui.menu.graphic.block_graphic import BlockGraphic
from endstone_inventoryui.menu.graphic.block_pair_graphic import BlockPairGraphic
from endstone_inventoryui.menu.graphic.graphic import Graphic

if TYPE_CHECKING:
    from endstone_inventoryui.menu import Menu
from endstone_inventoryui.network.inventory_content_packet import InventoryContentPacket
from endstone_inventoryui.network.inventory_slot_packet import InventorySlotPacket
from endstone_inventoryui.network.item_stack_wrapper import ItemStackWrapper
from endstone_inventoryui.util.item_utils import is_air
from endstone_inventoryui.util.utils import send_ack_packet, get_block_behind


class Session:
    CONTAINER_ID: int = 200

    MAX_OPEN_ATTEMPTS: int = 10

    class State(Enum):
        NONE = 0
        GRAPHIC_SENT = 1
        GRAPHIC_RECEIVED = 2
        GRAPHIC_DATA_SENT = 3
        GRAPHIC_DATA_RECEIVED = 4
        OPENING = 5
        OPEN = 6
        CLOSING = 7

    def __init__(self, player: Player):
        self.player: Player = player
        self.menu: 'Menu | None' = None
        self.state: Session.State = self.State.NONE
        self.graphic: Graphic | None = None
        self.block_pos: list[BlockPos] = []
        self.open_attempts = 0
        self.ack_timestamp = 0
        self.pending: deque['Menu'] = deque()

    def send_menu(self):
        self.open_attempts = 0
        self.ack_timestamp = 0
        pos = get_block_behind(self.player, 2)
        self.graphic = BlockPairGraphic(self.menu, pos) if self.menu.type.is_pair else BlockGraphic(self.menu, pos)
        self.send_graphic()

    def send_graphic(self):
        self.graphic.send(self.player)
        self.state = self.State.GRAPHIC_SENT
        self.ack_timestamp = send_ack_packet(self.player)

    def send_graphic_data(self):
        self.graphic.send_data(self.player)
        self.state = self.State.GRAPHIC_DATA_SENT
        self.ack_timestamp = send_ack_packet(self.player)

    def open(self):
        self.state = self.State.OPENING
        self.graphic.open(self.player)
        self.ack_timestamp = send_ack_packet(self.player)

    def send_contents(self):
        inventory = self.menu.inventory
        pk = InventoryContentPacket(Session.CONTAINER_ID)
        for i in range(inventory.size):
            item_stack = inventory.get_item(i)
            pk.items.append(ItemStackWrapper(0 if is_air(item_stack) else i + 1, item_stack))

        self.player.send_packet(pk.get_packet_id(), pk.serialize())

    def update_slot(self, slot: int):
        item = self.menu.inventory.get_item(slot)
        pk = InventorySlotPacket(self.CONTAINER_ID, slot, item=ItemStackWrapper(0, item))
        self.player.send_packet(pk.get_packet_id(), pk.serialize())

    def close(self):
        self.state = self.State.CLOSING
        self.graphic.remove(self.player)

    def update_state(self, state: State):
        self.state = state
        match state:
            case self.State.GRAPHIC_RECEIVED:
                self.send_graphic_data()
            case self.State.GRAPHIC_DATA_RECEIVED:
                self.open()
            case self.State.OPEN:
                self.send_contents()

    def __del__(self):
        self.close()
