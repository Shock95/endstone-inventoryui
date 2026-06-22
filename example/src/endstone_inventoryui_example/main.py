from endstone import Player
from endstone.inventory import ItemStack
from endstone.command import CommandSender, Command
from endstone.plugin import Plugin

from endstone_inventoryui import *


class Main(Plugin):
    prefix = "InventoryUI Example"
    api_version = "0.10"
    load = "POSTWORLD"
    commands = {
        "chestmenu": {
            "description": "Opens chest menu",
            "usages": ["/chestmenu"],
        }
    }

    def __init__(self):
        super().__init__()
        self.menu = Menu(MenuType.DOUBLE_CHEST, "chest menu")
        self.menu.set_listener(self.on_click)

    def on_enable(self):
        inventory = self.menu.inventory
        inventory.add_item(ItemStack("minecraft:diamond_sword"))
        inventory.add_item(ItemStack("minecraft:diamond_axe"))
        inventory.add_item(ItemStack("minecraft:diamond_pickaxe"))

    def on_command(self, sender: CommandSender, command: Command, _):
        match command.name:
            case "chestmenu":
                if isinstance(sender, Player):
                    self.menu.send_to(sender)
        return True

    def on_click(self, tr: MenuTransaction) -> MenuTransactionResult:
        if tr.item_clicked.type.id == "minecraft:air":
            return tr.proceed()
        return tr.discard()