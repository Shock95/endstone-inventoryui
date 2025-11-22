# endstone-inventoryui

Read-only Inventory UI plugin for Endstone

## API

### MenuType

Enum for menu container types:
- `MenuType.CHEST` - Single chest (27 slots)
- `MenuType.DOUBLE_CHEST` - Double chest (54 slots)
- `MenuType.HOPPER` - Hopper (5 slots)

### Menu

```python
Menu(type: MenuType, name: str = "")
```

**Properties:**
- `inventory` - The `UIInventory` instance (similar to Endstone Inventory)

**Methods:**
- `set_name(name: str)` - Set display name
- `set_listener(listener)` - Slot interact callback: `(player: Player, slot: int, item: ItemStack, inventory: UIInventory) -> None`
- `set_open_listener(listener)` - Set menu open callback: `(player: Player) -> None`
- `set_close_listener(listener)` - Set menu close callback: `(player: Player) -> None`
- `send_to(player: Player)` - Display menu to player
- `close(player: Player) -> bool` - Close this menu for player

## Usage
Check out the [example plugin](./example)