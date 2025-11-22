from enum import Enum


class MenuType(Enum):
    CHEST = 0
    DOUBLE_CHEST = 1
    HOPPER = 2

    def is_pair(self) -> bool:
        match self:
            case MenuType.CHEST:
                return False
            case MenuType.DOUBLE_CHEST:
                return True
            case MenuType.HOPPER:
                return False

    def get_block_id(self) -> str:
        match self:
            case MenuType.CHEST | MenuType.DOUBLE_CHEST:
                return "minecraft:chest"
            case MenuType.HOPPER:
                return "minecraft:hopper"

    def get_container_type(self) -> int:
        match self:
            case MenuType.CHEST | MenuType.DOUBLE_CHEST:
                return 0x0
            case MenuType.HOPPER:
                return 0x8

    def get_block_actor_id(self):
        match self:
            case MenuType.CHEST | MenuType.DOUBLE_CHEST:
                return "Chest"
            case MenuType.HOPPER:
                return "Hopper"

    def get_container_size(self) -> int:
        match self:
            case MenuType.CHEST:
                return 27
            case MenuType.DOUBLE_CHEST:
                return 54
            case MenuType.HOPPER:
                return 5
