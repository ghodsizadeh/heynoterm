from textual.app import ComposeResult, RenderResult
from textual.reactive import reactive
from textual.widgets import Static, TextArea, RadioSet, RadioButton
from textual.widget import Widget
from textual import events
from textual import log
from textual.message import Message
from textual.css.query import NoMatches

from heynoterm.state import dm, Block, Language as LanguageType


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

        # self.refresh()


class TextAreaComponent(TextArea):
    """
    A widget to display a box around text.
    That could save the text as state and update it when needed.

    """

    name = reactive("World")
    index = reactive(0)

    BINDINGS = [
        ("ctrl+d", "remove_block", "Remove Block"),
        ("ctrl+l", "change_language", "Change Language"),
        ("ctrl+n", "next_block", "Next Block"),
        ("ctrl+b", "previous_block", "Previous Block"),
        ("ctrl+a", "select_all", "Select All"),
    ]

    class RemoveBlock(Message):
        """A message to remove a block."""

        pass

    class ChangeLanguageList(Message):
        """A message to change language."""

        pass

    def _on_key(self, event: events.Key) -> None:
        """Save the text on key press on a file."""
        print("key")
        # with open(f"{self.name}.txt", "w") as f:
        #     f.write(self.text)
        dm.update_block(self.index, Block(text=self.text, language=self.language))

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


class TextAreaLang(Widget):
    """A widget that displays language of a text area."""

    langs: str = reactive("python")

    def on_click(self) -> None:
        print("click")
        self.langs = "javascript"
        # self.refresh()

    def change_lang(self, lang: str):
        self.langs = lang
        self.refresh()

    def render(self) -> RenderResult:
        return f"W language: {self.langs}"
