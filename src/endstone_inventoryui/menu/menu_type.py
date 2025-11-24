from dataclasses import dataclass
from enum import Enum


class MenuType(Enum):
    @dataclass(frozen=True)
    class Value:
        is_pair: bool
        block_id: str
        container_type: int
        block_actor_id: str
        container_size: int

    CHEST = Value(
        is_pair=False,
        block_id="minecraft:chest",
        container_type=0x0,
        block_actor_id="Chest",
        container_size=27
    )
    DOUBLE_CHEST = Value(
        is_pair=True,
        block_id="minecraft:chest",
        container_type=0x0,
        block_actor_id="Chest",
        container_size=54
    )
    HOPPER = Value(
        is_pair=False,
        block_id="minecraft:hopper",
        container_type=0x8,
        block_actor_id="Hopper",
        container_size=5
    )

    @property
    def is_pair(self) -> bool:
        return self.value.is_pair

    @property
    def block_id(self) -> str:
        """Get the Minecraft block ID for this menu type."""
        return self.value.block_id

    @property
    def container_type(self) -> int:
        """Get the container type ID for this menu type."""
        return self.value.container_type

    @property
    def block_actor_id(self) -> str:
        """Get the block actor ID for this menu type."""
        return self.value.block_actor_id

    @property
    def container_size(self) -> int:
        """Get the container size (number of slots) for this menu type."""
        return self.value.container_size
