from textual.app import ComposeResult, RenderResult
from textual.reactive import reactive
from textual.widgets import Static, TextArea, Rule, RadioSet, RadioButton
from textual.widget import Widget
from textual import events
from textual import log
from textual.message import Message

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

    def action_add_x(self) -> None:
        """An action to add a text block."""
        self.text += "X"

    def action_change_language(self) -> None:
        print("change language")
        self.post_message(self.ChangeLanguageList())

    def action_remove_block(self) -> None:
        """Called to remove a timer."""
        # self.remove()
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


class BlockComponent(Static):
    """A widget to display a box around text. with a divider at top"""

    text = reactive("World")
    language = reactive("python")
    index = reactive(0)

    def compose(self) -> ComposeResult:
        """Compose the widget."""
        text_component = TextAreaComponent(self.text, name=self.text)
        text_component.register_language("javascript", "javascript")
        text_component.language = self.language
        # theme="dracula" or "monokai" %2 == 0
        text_component.theme = "monokai" if self.index % 2 == 0 else "dracula"
        text_component.index = self.index
        yield text_component
        tal = TextAreaLang(id="TextAreaLang")
        tal.langs = self.language
        # yield Button("Change language", variant="primary", id="change_language")

        yield Rule(line_style="thick", id="rule1")

    def on_text_area_component_remove_block(
        self, event: TextAreaComponent.RemoveBlock
    ) -> None:
        print("remove parent")
        self.remove()
        dm.remove_block(index=self.index)

    async def on_text_area_component_change_language_list(
        self, event: TextAreaComponent.ChangeLanguageList
    ) -> None:
        print("change language list")
        language_list = LanguageList()
        language_list.language = self.language
        await self.mount(language_list, before="Rule")

        self.refresh()

    async def on_language_list_language_changed(
        self, event: LanguageList.LanguageChanged
    ) -> None:
        print("language changed")
        print(event.language)
        self.query_one("LanguageList").remove()
        # convert event from langagetype enum

        self.action_change_language(language=LanguageType(event.language))

    def action_change_language(self, language: LanguageType) -> None:
        self.language = language.value
        text_area = self.query_one("TextAreaComponent")
        text_area.language = self.language
        # update state
        dm.update_block(self.index, Block(text=text_area.text, language=self.language))
        text_area.refresh()
        self.refresh()
