from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widgets import Static, TextArea, RadioSet, RadioButton
from textual import events, log
from textual.message import Message
from textual.css.query import NoMatches
from textual.widgets.text_area import Selection
from rich.console import RenderableType


from heynoterm.math_evaluator import MathBlockEvaluator
from heynoterm.state import dm, Block, Language as LanguageType


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

    BINDINGS = [
        ("ctrl+d", "remove_block", "Remove Block"),
        ("ctrl+l", "change_language", "Change Language"),
        ("ctrl+n", "next_block", "Next Block"),
        ("ctrl+b", "previous_block", "Previous Block"),
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

    async def _on_key(self, event: events.Key) -> None:
        """Save the text on key press on a file."""
        await super()._on_key(event)
        key = event.key if event.is_printable else ""

        # with open(f"{self.name}.txt", "w") as f:
        #     f.write(self.text)
        text = self.text
        print("key", event.key, self.text[-1:], key, text[-1:])

        dm.update_block(
            self.index,
            Block(text=text, language="math" if self.math else self.language),
        )
        if self.math:
            print("math")
            evaluator = MathBlockEvaluator()
            results = evaluator.process_block(text)
            for i, result in enumerate(results):
                print(i, result)
            print(evaluator.variables)
            self.post_message(self.MathResultMessage(results=evaluator.variables))

    def action_split_block(self) -> None:
        """Split the block into two blocks."""
        print("split block")
        # for now select text before cursor
        self.selection = Selection((0, 0), self.get_cursor_word_right_location())
        # get text before cursor and after cursor
        before_text = self.selected_text
        after_text = self.text[len(before_text) :]
        print(before_text, after_text)
        # TODO: remove block and add two blocks

    def action_next_block(self) -> None:
        """Move focus to next text area"""
        try:
            q = self.screen.query_one(f"#TextAreaComponent_{self.index + 1}")
            q.focus()
        except NoMatches:
            pass

    def action_previous_block(self) -> None:
        """Move focus to previous text area"""
        try:
            q = self.screen.query_one(f"#TextAreaComponent_{self.index - 1}")
            q.focus()
        except NoMatches:
            pass

    def action_change_language(self) -> None:
        print("change language")
        self.post_message(self.ChangeLanguageList())

    def action_remove_block(self) -> None:
        """Called to remove a timer."""

        q = self.query()
        log(q)
        for i in q:
            log(i)
        print(q)
        print("remove child")
        self.post_message(self.RemoveBlock())
        print("remove after child")
        # dm.remove_block(index=self.index)


class LanguageList(Static):
    language = reactive("x")

    def compose(self) -> ComposeResult:
        with RadioSet(id="language_list"):
            for language in LanguageType:
                print(
                    "xx", self.language, language.value, language.value == self.language
                )
                yield RadioButton(
                    language.value,
                    value=language.value == self.language,
                    id=language.name,
                )

    async def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        print(event.pressed.value, "was pressed")
        print(event.pressed.label, "was pressed")
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

    results = reactive({})

    def render(self) -> RenderableType:
        if not self.results:
            return "Results will be displayed here"
        return ",".join(f"{key} = {value}" for key, value in self.results.items())
