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


class MenuTransaction:
    def __init__(
        self,
        player: Player,
        slot: int,
        item_clicked: ItemStack,
        item_clicked_with: ItemStack,
        action_type: ItemStackRequestActionType,
        source: ItemStackRequestSlotInfo,
        destination: ItemStackRequestSlotInfo,
    ):
        self._player = player
        self._slot = slot
        self._item_clicked = item_clicked
        self._item_clicked_with = item_clicked_with
        self._action_type = action_type
        self._source = source
        self._destination = destination

    @property
    def player(self) -> Player:
        return self._player

    @property
    def slot(self) -> int:
        return self._slot

    @property
    def item_clicked(self) -> ItemStack:
        return self._item_clicked

    @property
    def item_clicked_with(self) -> ItemStack:
        return self._item_clicked_with

    @property
    def action_type(self) -> ItemStackRequestActionType:
        return self._action_type

    @property
    def source(self) -> ItemStackRequestSlotInfo:
        return self._source

    @property
    def destination(self) -> ItemStackRequestSlotInfo:
        return self._destination

    def proceed(self) -> MenuTransactionResult:
        return MenuTransactionResult(MenuTransactionResultType.CONTINUE)

    def discard(self) -> MenuTransactionResult:
        return MenuTransactionResult(MenuTransactionResultType.DISCARD)