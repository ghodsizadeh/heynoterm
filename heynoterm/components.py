"""Collection of Textual widgets used throughout *HeyNoterm*."""

import logging

from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widgets import Static, TextArea, RadioSet, RadioButton

# ``textual.log`` was used previously for simple debugging – replaced by the
# *logging* module, therefore the import is no longer required.
from textual.message import Message
from textual.css.query import NoMatches
from textual.widgets.text_area import Selection
from rich.console import RenderableType


from heynoterm.math_evaluator import MathBlockEvaluator
from heynoterm.state import dm, Block, Language as LanguageType

# ----------------------------------------------------------------------------
# Logging setup
# ----------------------------------------------------------------------------

logger = logging.getLogger(__name__)


# self.refresh()


class TextAreaComponent(TextArea):
    """
    A widget to display a box around text.
    That could save the text as state and update it when needed.

    """

    name = reactive("World")
    index = reactive(0)
    math = reactive(False)
    math_result = reactive({})

    # Key bindings focused on intuitiveness:
    #   - Ctrl+J / Ctrl+K    : move between blocks (commonly used in many TUIs)
    #   - Ctrl+D             : delete current block (unchanged)
    #   - Ctrl+L             : open language selection
    #   - Ctrl+A             : select all text (TextArea default)
    #   - Ctrl+Z             : experimental – split block
    BINDINGS = [
        ("ctrl+d", "remove_block", "Remove Block"),
        ("ctrl+l", "change_language", "Change Language"),
        ("ctrl+j", "next_block", "Next Block"),
        ("ctrl+k", "previous_block", "Previous Block"),
        ("ctrl+a", "select_all", "Select All"),
        ("ctrl+z", "split_block", "Split Block"),
    ]

    class RemoveBlock(Message):
        """A message to remove a block."""

        pass

    class ChangeLanguageList(Message):
        """A message to change language."""

        pass

    class MathResultMessage(Message):
        """A message to change language."""

        def __init__(self, results: dict) -> None:
            self.results = results
            super().__init__()

    async def on_text_area_changed(self, event: TextArea.Changed):
        """Save the text on key press on a file."""

        text = event.text_area.text

        dm.update_block(
            self.index,
            Block(text=text, language="math" if self.math else self.language),
        )
        if self.math:
            logger.debug("TextArea %s – math mode", self.index)
            evaluator = MathBlockEvaluator()
            evaluator.process_block(text)
            self.post_message(self.MathResultMessage(results=evaluator.results))

    def action_split_block(self) -> None:
        """Split the block into two blocks."""
        logger.debug("TextArea %s – split block requested", self.index)
        # for now select text before cursor
        self.selection = Selection((0, 0), self.get_cursor_word_right_location())
        # get text before cursor and after cursor
        before_text = self.selected_text
        after_text = self.text[len(before_text) :]
        logger.debug(
            "TextArea %s – before: %s after: %s", self.index, before_text, after_text
        )
        # TODO: remove block and add two blocks

    def action_next_block(self) -> None:
        """Move focus to the *next* text-area (Ctrl+J)."""

        try:
            self.screen.query_one(f"#TextAreaComponent_{self.index + 1}").focus()
        except NoMatches:
            # Already on the last block – nothing to do.
            logger.debug("TextArea %s – next_block: already last", self.index)

    def action_previous_block(self) -> None:
        """Move focus to the *previous* text-area (Ctrl+K)."""

        if self.index == 0:
            logger.debug("TextArea %s – previous_block: already first", self.index)
            return

        try:
            self.screen.query_one(f"#TextAreaComponent_{self.index - 1}").focus()
        except NoMatches:
            # Shouldn’t happen – indices might be out of sync.
            logger.warning(
                "TextArea %s – previous_block: NoMatches for index %s",
                self.index,
                self.index - 1,
            )

    def action_change_language(self) -> None:
        logger.debug("TextArea %s – show language list", self.index)
        self.post_message(self.ChangeLanguageList())

    def action_remove_block(self) -> None:
        """Called to remove a timer."""

        # Emit detailed information about children for debugging purposes.
        for child in self.query():
            logger.debug("TextArea %s – child: %s", self.index, child)

        logger.debug("TextArea %s – remove block", self.index)
        self.post_message(self.RemoveBlock())
        logger.debug("TextArea %s – block removed signal posted", self.index)
        # dm.remove_block(index=self.index)


class LanguageList(Static):
    language = reactive("x")

    def compose(self) -> ComposeResult:
        with RadioSet(id="language_list"):
            for language in LanguageType:
                logger.debug(
                    "LanguageList – comparing %s with current %s",
                    language.value,
                    self.language,
                )
                yield RadioButton(
                    language.value,
                    value=language.value == self.language,
                    id=language.name,
                )

    async def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        logger.debug(
            "LanguageList – %s selected (label %s)",
            event.pressed.value,
            event.pressed.label,
        )
        self.post_message(self.LanguageChanged(str(event.pressed.label).lower()))

    class LanguageChanged(Message):
        """A message to change language."""

        def __init__(self, language: str) -> None:
            super().__init__()

            self.language = language


class MathResult(Static):
    """
    A widget to display the result of a math evaluation.
    Which came from a dictionary of variables.
    """

    results = reactive([])

    def render(self) -> RenderableType:
        if not self.results:
            return "Results will be displayed here"

        return "\n".join(
            f"{f'{res:.5f}' if isinstance(res, float) else res}"
            for i, res in enumerate(self.results)
        )
