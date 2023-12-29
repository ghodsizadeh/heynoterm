from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer
from textual.reactive import reactive
from textual.widgets import Footer, Header
from heynoterm.state import AppState

from heynoterm.block import BlockComponent
from heynoterm.state import dm, Block


class HeyNoteApp(App):
    """A Textual app to manage stopwatches."""

    CSS_PATH = "heynoterm.tcss"

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
        state: AppState = dm.state
        blocks = [b.to_terminal(index=i) for i, b in enumerate(state.blocks)]
        self.count = len(blocks)
        yield ScrollableContainer(*blocks, id="blocks")

    def action_add_block(self) -> None:
        """An action to add a text block."""
        new: BlockComponent = BlockComponent()
        new.text = f"Hello {self.count}"
        new.index = self.count
        self.count += 1

        self.query_one("#blocks").mount(new)
        dm.add_block(block=Block(text=new.text, language=new.language))
        new.scroll_visible()
        new.focus()

    def action_remove_stopwatch(self) -> None:
        """Called to remove a timer."""
        timers = self.query("TextAreaBox")
        if timers:
            timers.last().remove()
            dm.remove_block(index=self.count - 1)
        self.count -= 1

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark  # type: ignore


def main() -> None:
    """Run the app."""
    app = HeyNoteApp()
    app.run()


if __name__ == "__main__":
    main()
