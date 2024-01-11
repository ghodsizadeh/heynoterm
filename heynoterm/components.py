from textual.app import ComposeResult
from textual.events import Key
from textual.reactive import reactive
from textual.widgets import Static, TextArea, RadioSet, RadioButton
from textual import log, work
from textual.message import Message
from textual.css.query import NoMatches
from textual.widgets.text_area import Selection
from rich.console import RenderableType


from heynoterm.math_evaluator import MathBlockEvaluator
from heynoterm.state import dm, Block, Language as LanguageType
from heynoterm.config import has_ai


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

    async def on_text_area_changed(self, event: TextArea.Changed):
        """Save the text on key press on a file."""

        text = event.text_area.text

        dm.update_block(
            self.index,
            Block(text=text, language="math" if self.math else self.language),
        )
        if self.math:
            print("math")
            evaluator = MathBlockEvaluator()
            evaluator.process_block(text)
            self.post_message(self.MathResultMessage(results=evaluator.results))

    @work(exclusive=True)
    async def update_text_with_ai(self):
        if has_ai():
            from heynoterm.llm import stream_output

            input_text = self.text[:-3]
            self.text = input_text
            self.text += "\n"
            async for output in stream_output(input_text):
                if output:
                    print("output", output)
                    self.text += output
                    self.refresh()

    async def _on_key(self, event: Key) -> None:
        await super()._on_key(event)
        ai_hook = "+++"  # noqa
        if event.character == "+":  # and has_ai() and self.text.endswith(ai_hook):
            self.update_text_with_ai()
        # from heynoterm.llm import stream_output
        # from asyncio import sleep
        # input_text = self.text[:-len(ai_hook)]
        # self.text = input_text
        # for i in 'abcdefghijklmnopqrstuvwxyz':
        #     self.text += i
        #     print('i', i)
        #     await self.refresh()
        #     await sleep(0.1)

        # for output in stream_output(input_text):
        #     if output:
        #         self.text += output

        # check if it has +++

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

    results = reactive([])

    def render(self) -> RenderableType:
        if not self.results:
            return "Results will be displayed here"
        # return '\n'.join(self.results)
        return "\n".join(f"{i+1} {res}" for i, res in enumerate(self.results))
        # return ",".join(f"{key} = {value}" for key, value in self.results.items())
