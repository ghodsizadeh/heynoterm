from dataclasses import dataclass, field
from typing import List, Optional
from pathlib import Path
import json
from enum import Enum
import os


class Language(Enum):
    PYTHON = "python"
    MARKDOWN = "markdown"
    MATH = "math"


@dataclass
class Block:
    """Represents a single block of text displayed in the UI.

    Parameters
    ----------
    text:
        Raw text contained in the block.
    language:
        The language (or *kind*) of the block – for example *python*, *markdown*
        or *math*.  Defaults to the lower-case value of ``Language.PYTHON`` so
        that we are consistent across the code-base.  Previously we used
        ``Language.PYTHON.name`` (i.e. the **upper-case** *PYTHON*), which was
        inconsistent with the rest of the application that expects lower-case
        values coming from ``Enum.value``.  This subtle mismatch could easily
        lead to bugs when adding new features, therefore we standardise on
        ``Enum.value`` here.
    """

    text: str
    language: str = Language.PYTHON.value

    def to_terminal(self, index: int):  # noqa: ANN001 – keeps import-loop at bay
        """Convert the block to its Textual UI representation.

        The Textual components live in :pyfile:`heynoterm.block` which imports
        :pyfile:`heynoterm.state`, causing a circular dependency.  To avoid that
        we perform the import lazily inside the method.

        Parameters
        ----------
        index:
            Position of the block in the list – required so the widget can set
            a stable *id* and react correctly to focus events.
        """

        # Lazy import to prevent a circular import between *state* and *block*.
        from heynoterm.block import BlockComponent  # pylint: disable=import-outside-toplevel

        new_block = BlockComponent()
        new_block.text = self.text
        new_block.language = self.language
        new_block.index = index
        return new_block


@dataclass
class AppState:
    blocks: List[Block] = field(default_factory=list)

    def to_json(self) -> str:
        """Serialise the current state as a formatted JSON string."""

        # We cannot directly use ``dataclasses.asdict`` on the *AppState*
        # instance because that would recursively serialise *self* as well.
        # Therefore we only serialise the blocks and keep the output 100%
        # backward-compatible with the previous implementation.
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
        If `path` is provided, use that.
        Otherwise, check HEYNOTERM_STATE_PATH env var; if set, use that.
        Else default to ~/.heynoterm.json.
        """
        if path is not None:
            self.path = path
        else:
            env_path = os.getenv("HEYNOTERM_STATE_PATH")
            if env_path:
                self.path = Path(env_path)
            else:
                self.path = Path.home() / ".heynoterm.json"
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
