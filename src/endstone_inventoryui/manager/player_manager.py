from typing import TYPE_CHECKING
from uuid import UUID

from endstone import Player

if TYPE_CHECKING:
    from endstone_inventoryui.manager import Session

sessions: dict[UUID, 'Session'] = {}


def find_session(player: Player) -> 'Session|None':
    global sessions
    if player.unique_id in sessions:
        return sessions[player.unique_id]
    return None


def create_session(player: Player) -> 'Session':
    from endstone_inventoryui.manager import Session  # Import here at runtime

    global sessions
    session = Session(player=player)
    sessions[player.unique_id] = session
    return session


def close_session(player: Player):
    global sessions
    if player.unique_id in sessions:
        session = sessions[player.unique_id]
        if session.menu is not None:
            session.menu._remove_session(session)
        del sessions[player.unique_id]
