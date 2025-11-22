from endstone import Player
from endstone._internal.endstone_python import ItemStack
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

    chest_menu = Menu(MenuType.DOUBLE_CHEST, "chest menu")

    def on_command(self, sender: CommandSender, command: Command, _):
        match command.name:
            case "chestmenu":
                if isinstance(sender, Player):
                    inventory = self.chest_menu.inventory
                    self.chest_menu.set_listener(self.on_click)

                    inventory.add_item(ItemStack("minecraft:diamond_sword"))
                    inventory.add_item(ItemStack("minecraft:diamond_axe"))
                    inventory.add_item(ItemStack("minecraft:diamond_pickaxe"))
                    inventory.add_item(ItemStack("minecraft:hopper"))

                    ench_item = ItemStack("minecraft:diamond_sword")
                    meta = ench_item.item_meta
                    meta.add_enchant("sharpness", 5)
                    ench_item.set_item_meta(meta)
                    inventory.set_item(5, ench_item)

                    self.chest_menu.send_to(sender)
        return True

    def on_click(self, player: Player, slot: int, item: ItemStack, inventory: UIInventory):
        print(f"{player.name} clicked on slot {slot} ({item.type.id})")
        if slot == 3:
            menu = Menu(MenuType.HOPPER, "hopper menu")
            menu.inventory.set_item(0, ItemStack("minecraft:diamond_sword"))
            menu.inventory.set_item(1, ItemStack("minecraft:diamond_axe"))
            menu.inventory.set_item(2, ItemStack("minecraft:diamond_pickaxe"))
            self.chest_menu.close(player)
            menu.send_to(player)
            return
