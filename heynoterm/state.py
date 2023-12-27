from dataclasses import dataclass, field
from typing import List, Optional
from pathlib import Path
import json
from enum import Enum


class Language(Enum):
    PYTHON = "python"
    MARKDOWN = "markdown"
    MATH = "math"


@dataclass
class Block:
    text: str
    language: str = Language.PYTHON.name

    def to_terminal(self, index: int) -> str:
        from heynoterm.block import BlockComponent

        new_block = BlockComponent()
        new_block.text = self.text
        new_block.language = self.language
        new_block.index = index
        return new_block


@dataclass
class AppState:
    blocks: List[Block] = field(default_factory=list)

    def to_json(self) -> str:
        return json.dumps(
            {"blocks": [block.__dict__ for block in self.blocks]}, indent=4
        )

    @staticmethod
    def from_json(data: str) -> "AppState":
        json_data = json.loads(data)
        blocks = [Block(**block) for block in json_data.get("blocks", [])]
        return AppState(blocks=blocks)


class DataManager:
    """
    A class to manage the data of the app.
    To load, save and update the data.
    """

    def __init__(self, path: Optional[Path] = None) -> None:
        """
        Initialize the data manager.
        With a default path for all OS.
        to save the data.
        """
        if path is None:
            self.path = Path.home() / ".heynoterm.json"
        else:
            self.path = path
        self.state: AppState = AppState()
        self.load()

    def load(self) -> None:
        """Load the data from the path."""
        if self.path.exists():
            with open(self.path, "r") as f:
                try:
                    self.state = AppState.from_json(f.read())
                except json.JSONDecodeError:
                    self.save()
        else:
            self.save()

    def save(self) -> None:
        """Save the data to the path."""
        with open(self.path, "w") as f:
            f.write(self.state.to_json())

    def add_block(
        self, block: Optional[Block] = None, index: Optional[int] = None
    ) -> None:
        """Add a block to the state."""
        if block is None:
            block = Block(text="", language=Language.MARKDOWN.value)
        if index is not None:
            self.state.blocks.insert(index, block)
        else:
            self.state.blocks.append(block)
        self.save()

    def remove_block(self, index: int) -> None:
        """Remove a block from the state."""
        self.state.blocks.pop(index)
        self.save()

    def update_block(self, index: int, block: Block) -> None:
        """Update a block in the state."""
        self.state.blocks[index] = block
        self.save()


dm = DataManager()
