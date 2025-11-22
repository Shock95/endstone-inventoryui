from endstone.plugin import Plugin

from endstone_inventoryui.listener import EventListener


class InventoryUIPlugin(Plugin):
    prefix = "InventoryUI"
    api_version = "0.6"
    load = "POSTWORLD"

    def on_enable(self) -> None:
        self.register_events(EventListener(self))
