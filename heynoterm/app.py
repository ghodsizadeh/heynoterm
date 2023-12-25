from time import monotonic
from typing import Any, Coroutine

from textual.app import App, ComposeResult, RenderResult
from textual.containers import ScrollableContainer
from textual.events import Click
from textual.reactive import reactive
from textual.widgets import Button, Footer, Header, Static, TextArea, Rule
from textual.widget import Widget
from textual import events


class TextAreaComponent(TextArea):
    """
    A widget to display a box around text.
    That could save the text as state and update it when needed.

    """

    name = reactive("World")

    def on_change(self) -> None:
        print('before')
        self.app.update_print_x(f"Saved {self.name}.txt")
        print('after')


    def _on_key(self, event: events.Key) -> None:
        """Save the text on key press on a file."""
        print('key')
        with open(f"{self.name}.txt", "w") as f:
            f.write(self.text)

class TextAreaLang(Widget):
    """ A widget that displays language of a text area."""
    langs: str = reactive("python")

    def on_click(selfca) -> None:
        print('click')
        self.langs = "javascript"
        # self.refresh()
    def change_lang(self, lang:str):
        self.langs = lang
        self.refresh()
    def render(self) -> RenderResult:
        return f"W language: {self.langs}"


class TextAreaBox(Static):
    """A widget to display a box around text. with a divider at top"""


    text = reactive("World")
    language = reactive("python")

    def compose(self) -> ComposeResult:
        """Compose the widget."""
        text_component = TextAreaComponent(self.text, name=self.text)
        text_component.register_language('javascript', 'javascript')
        text_component.language = self.language
        text_component.styles.background = "darkblue"
        yield text_component
        tal =  TextAreaLang(id="TextAreaLang")
        tal.langs = self.language
        yield Button("Change language", variant="primary", id="change_language")

        yield Rule(line_style="thick", id="rule1")





    def action_add_x(self):
        self.text += "xxx"
        
    def on_button_pressed(self, event: Button.Pressed) -> None:

        if event.button.id == "change_language":
            self.action_change_language()
            # self.query_one("TextAreaLang").change_lang(self.language)
            text_area = self.query_one("TextAreaComponent")
            text_area.language = self.language
            text_area.refresh()
            # self.query_one("TextAreaComponent").refresh()
    def action_change_language(self) -> None:
        if self.language == "python":
            self.language = "markdown"
        else:
            self.language = "python"
        self.refresh()



class HeyNoteApp(App):
    """A Textual app to manage stopwatches."""

    CSS_PATH = "stopwatch.tcss"

    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        # ("a", "add_block", "Add"),
        ("ctrl+a", "add_block", "Add A"),
        ("r", "remove_stopwatch", "Remove"),
    ]
    count = reactive(0)

    def compose(self) -> ComposeResult:
        """Called to add widgets to the app."""
        yield Header()
        yield Footer()
        yield ScrollableContainer(TextAreaBox("abs"), id="blocks")
    
    def update_print_x(self, text):
        print(text,'pppp')
        with open(f"ali.txt", "w") as f:
            f.write("xx",text)

    def action_add_block(self) -> None:
        """An action to add a text block."""
        self.count += 1
        new = TextAreaBox()
        new.text = f"Hello {self.count}"
        if self.count % 2 == 0:
            new.styles.background = "blue"
        new.styles.background = "red"
        self.query_one("#blocks").mount(new)
        new.scroll_visible()
        new.focus()

    def action_remove_stopwatch(self) -> None:
        """Called to remove a timer."""
        timers = self.query("TextAreaBox")
        self.count -= 1
        if timers:
            timers.last().remove()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark


if __name__ == "__main__":
    app = HeyNoteApp()
    app.run()
