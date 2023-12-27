from textual.app import ComposeResult, RenderResult
from textual.reactive import reactive
from textual.widgets import Button, Static, TextArea, Rule
from textual.widget import Widget
from textual import events
from textual import log
from textual.message import Message

from heynoterm.state import dm, Block


class TextAreaComponent(TextArea):
    """
    A widget to display a box around text.
    That could save the text as state and update it when needed.

    """

    name = reactive("World")
    index = reactive(0)

    BINDINGS = [
        ("ctrl+d", "remove_block", "Remove Block"),
        ("ctrl+l", 'push_screen("lg")', "Select Language"),
    ]

    class RemoveBlock(Message):
        """A message to remove a block."""

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
        yield Button("Change language", variant="primary", id="change_language")

        yield Rule(line_style="thick", id="rule1")

    # def on_remove_block(self, event: TextAreaComponent.RemoveBlock) -> None:
    #     print("remove parent")
    #     self.remove()
    def on_text_area_component_remove_block(
        self, event: TextAreaComponent.RemoveBlock
    ) -> None:
        print("remove parent")
        self.remove()
        dm.remove_block(index=self.index)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "change_language":
            self.action_change_language()
            text_area = self.query_one("TextAreaComponent")
            text_area.language = self.language
            # update state
            dm.update_block(
                self.index, Block(text=text_area.text, language=self.language)
            )
            text_area.refresh()

    def action_change_language(self) -> None:
        if self.language == "python":
            self.language = "markdown"
        else:
            self.language = "python"
        self.refresh()
