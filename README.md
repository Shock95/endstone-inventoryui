# endstone-inventoryui

Virtual inventory plugin for Endstone

## API

### MenuType

Enum for menu container types:

- `MenuType.CHEST` — single chest (27 slots)
- `MenuType.DOUBLE_CHEST` — double chest (54 slots)
- `MenuType.DISPENSER` — dispenser (9 slots)
- `MenuType.HOPPER` — hopper (5 slots)

### Menu

```python
Menu(type: MenuType, name: str = "")
```

**Properties:**

- `inventory` — the `MenuInventory` instance for this menu. Implements an API similar to Endstone's `Inventory`.
- `name` — display name shown at the top of the menu
- `type` — the `MenuType` used to create this menu

**Methods:**

- `set_name(name: str)` — set the display name
- `set_listener(listener)` — set the click callback (see [MenuTransaction](#menutransaction))
- `set_open_listener(listener)` — callback when a player opens the menu: `(player: Player) -> None`
- `set_close_listener(listener)` — callback when a player closes the menu: `(player: Player) -> None`
- `send_to(player: Player)` — display the menu to a player. If the player already has a menu open, this menu is queued and shown after the current one closes.
- `close(player: Player) -> bool` — close this menu for a player
- `close_all()` — close this menu for all players currently viewing it
- `get_viewers() -> list[Player]` — list players who currently have this menu open

### MenuTransaction

**Properties:**

- `player` — the player who clicked
- `slot` — virtual inventory slot index
- `item_clicked` — item in the virtual slot before the action
- `item_clicked_with` — item in the other slot involved (player inventory or cursor)
- `action_type` — the underlying `ItemStackRequestActionType`
- `source` — source slot info from the request
- `destination` — destination slot info from the request

**Methods:**

- `proceed() -> MenuTransactionResult` — allow the transaction to proceed
- `discard() -> MenuTransactionResult` — discard transaction

## Usage

```python
from endstone import Player
from endstone.inventory import ItemStack
from endstone_inventoryui import Menu, MenuType, MenuTransaction, MenuTransactionResult

menu = Menu(MenuType.CHEST)

menu.inventory.set_item(0, ItemStack("minecraft:diamond", 1))
menu.inventory.set_item(1, ItemStack("minecraft:emerald", 1))


def on_click(tr: MenuTransaction) -> MenuTransactionResult:
    if tr.slot == 0:
        tr.player.send_message("You clicked the diamond!")
        return tr.discard()
    elif tr.slot == 1:
        tr.player.send_message("You clicked the emerald!")
        return tr.discard()

    return tr.proceed()


menu.set_listener(on_click)
menu.send_to(player)
```

See the [example plugin](./example) for a full project.
