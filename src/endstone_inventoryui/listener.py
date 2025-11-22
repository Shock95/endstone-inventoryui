from bedrock_protocol.packets import MinecraftPacketIds
from bedrock_protocol.packets.enums import ItemStackRequestActionType
from bedrock_protocol.packets.packet import ContainerClosePacket, ItemRegistryPacket, ItemStackRequestPacket
from endstone._internal.endstone_python import PacketSendEvent
from endstone.event import event_handler, EventPriority, PlayerQuitEvent, PacketReceiveEvent
from endstone.plugin import Plugin

from .manager import Session
from .manager.player_manager import find_session, close_session
from .network.network_stack_latency_packet import NetworkStackLatencyPacket
from .util.item_utils import all_item_data, add_item_data


class EventListener:
    def __init__(self, plugin: Plugin):
        self._plugin = plugin

    @event_handler(priority=EventPriority.NORMAL)
    def on_packet_receive(self, event: PacketReceiveEvent):
        packet_id = event.packet_id
        player = event.player
        if player is None:
            return
        if packet_id == MinecraftPacketIds.Ping:
            session = find_session(player)
            if session is not None:
                pk = NetworkStackLatencyPacket()
                pk.deserialize(event.payload)
                if session.ack_timestamp == pk.timestamp:
                    match session.state:
                        case Session.State.GRAPHIC_SENT:
                            session.update_state(Session.State.GRAPHIC_RECEIVED)
                        case Session.State.GRAPHIC_DATA_SENT:
                            session.update_state(Session.State.GRAPHIC_DATA_RECEIVED)
                        case Session.State.OPENING:
                            if session.open_attempts >= Session.MAX_OPEN_ATTEMPTS:
                                # close session after max open attempts
                                session.close()
                                return
                            session.open_attempts += 1
                            session.open()

        elif packet_id == MinecraftPacketIds.ContainerClose:
            session = find_session(player)
            if session is not None:
                pk = ContainerClosePacket()
                pk.deserialize(event.payload)
                # if pk.container_id == 0xFF and pk.container_type == 0xF7 and pk.is_server_side == False:
                #    if session.state != Session.State.OPENING:
                #        return
                #    if session.open_attempts >= Session.MAX_OPEN_ATTEMPTS:
                #        return
                #    session.open_attempts += 1
                #    session.open()
                #    return

                if pk.container_id == Session.CONTAINER_ID:
                    if session.menu.close_listener is not None:
                        session.menu.close_listener(player)
                    if session.pending:
                        if session.state != Session.State.CLOSING:
                            session.close()
                        session.menu = session.pending.popleft()
                        session.send_menu()
                    else:
                        close_session(player)

        elif packet_id == MinecraftPacketIds.PacketViolationWarning:
            session = find_session(player)
            if session is not None:
                if session.state == Session.State.OPENING:
                    session.update_state(Session.State.OPEN)
                    if session.menu.open_listener is not None:
                        session.menu.open_listener(player)

        elif packet_id == MinecraftPacketIds.ItemStackRequest:
            session = find_session(player)
            if session is not None and session.state == Session.State.OPEN:
                menu = session.menu
                pk = ItemStackRequestPacket()
                pk.deserialize(event.payload)
                for req_data in pk.request.request_data:
                    for action in req_data.request_actions:
                        if action.action_type == ItemStackRequestActionType.Take or action.action_type == ItemStackRequestActionType.Place:
                            slot = action.action_data.source.slot
                            if menu.listener is not None:
                                item_clicked = menu.inventory.get_item(slot)
                                menu.listener(player, slot, item_clicked, menu.inventory)
                                return

    @event_handler
    def on_packet_send(self, event: PacketSendEvent):
        if event.packet_id == MinecraftPacketIds.ItemRegistryPacket and len(all_item_data()) == 0:
            pk = ItemRegistryPacket()
            pk.deserialize(event.payload)
            for item in pk.item_registry:
                add_item_data(item.item_name, item)

    @event_handler
    def on_player_quit(self, event: PlayerQuitEvent):
        close_session(event.player)
