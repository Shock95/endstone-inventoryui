from dataclasses import dataclass
from enum import Enum
from bedrock_protocol.packets.enums import ItemStackRequestActionType
from bedrock_protocol.packets.types import ItemStackRequestSlotInfo
from endstone import Player
from endstone.inventory import ItemStack

class MenuTransactionResultType(Enum):
    CONTINUE = "continue"
    DISCARD = "discard"


@dataclass(frozen=True)
class MenuTransactionResult:
    type: MenuTransactionResultType

    @property
    def should_continue(self) -> bool:
        return self.type == MenuTransactionResultType.CONTINUE

    @property
    def should_discard(self) -> bool:
        return self.type == MenuTransactionResultType.DISCARD


@dataclass(frozen=True)
class MenuTransaction:
    player: Player
    slot: int
    item_clicked: ItemStack
    item_clicked_with: ItemStack
    action_type: ItemStackRequestActionType
    source: ItemStackRequestSlotInfo
    destination: ItemStackRequestSlotInfo

    def proceed(self) -> MenuTransactionResult:
        return MenuTransactionResult(MenuTransactionResultType.CONTINUE)

    def discard(self) -> MenuTransactionResult:
        return MenuTransactionResult(MenuTransactionResultType.DISCARD)