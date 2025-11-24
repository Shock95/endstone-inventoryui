from typing import Optional, Callable

from endstone import Player
from endstone._internal.endstone_python import ItemStack

from endstone_inventoryui.manager.player_manager import find_session, create_session, get_all_sessions
from endstone_inventoryui.menu.inventory import UIInventory
from endstone_inventoryui.menu.menu_type import MenuType


class Menu:

    def __init__(self, type: MenuType, name: str = ""):
        self.name = name
        self.type = type
        self._inventory: UIInventory = UIInventory(type.container_size,
                                                   slot_updated=self._on_slot_changed)
        self.listener: Optional[Callable[[Player, int, ItemStack, UIInventory], None]] = None
        self.open_listener: Optional[Callable[[Player], None]] = None
        self.close_listener: Optional[Callable[[Player], None]] = None

    @property
    def inventory(self):
        return self._inventory

    def set_name(self, name: str):
        """
        Set the display name of the menu.

        Args:
            name: The new display name to show at the top of the menu.
        """
        self.name = name

    def set_listener(self, listener: Callable[[Player, int, ItemStack, UIInventory], None]):
        self.listener = listener

    def set_open_listener(self, listener: Callable[[Player], None]):
        """
        Set the callback for menu open events.

        Args:
            listener: A function called when a player opens this menu.
        """

        self.open_listener = listener

    def set_close_listener(self, listener: Callable[[Player], None]):
        """
        Set the callback for menu close events.

        Args:
            listener: A function called when a player closes this menu.
        """
        self.close_listener = listener

    def send_to(self, player: Player):
        """
        Display this menu to a player.

        If the player already has a menu open, this menu is queued and will
        be shown after the current menu is closed. Otherwise, a new session
        is created and the menu is displayed immediately.

        Args:
            player: The player to show the menu to.
        """
        existing_session = find_session(player)
        if existing_session is not None:
            existing_session.pending.append(self)
        else:
            session = create_session(player)
            session.menu = self
            session.send_menu()

    def close(self, player: Player) -> bool:
        """
        Close this specific menu for a player.

        Only closes the menu if it matches the player's currently open menu
        and the session is not already in a closing state.
        """
        from endstone_inventoryui.manager import Session
        session = find_session(player)
        if session is not None:
            if session.menu == self and session.state != Session.State.CLOSING:
                session.close()
                return True
        return False

    def _on_slot_changed(self, slot: int) -> None:
        from endstone_inventoryui.manager import Session
        sessions = get_all_sessions()
        for session in sessions:
            if session.menu is not self:
                return
            if session.state != Session.State.OPEN:
                return
            session.update_slot(slot)
