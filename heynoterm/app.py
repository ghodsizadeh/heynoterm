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
        ("ctrl+n", "add_block", "New Block"),
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
        # Determine insertion point – by default append at the end, but if
        # a TextArea inside a Block is currently focused we insert *after* its
        # parent block so the workflow feels natural (Ctrl+N -> new block
        # below the current one).

        # ------------------------------------------------------------------
        #   1. Detect current block / index
        # ------------------------------------------------------------------
        focused_widget = self.focused
        insert_index = self.count  # default – append
        container = self.query_one("#blocks")

        if focused_widget is not None:
            # Walk up the widget tree to find the surrounding BlockComponent.
            for ancestor in focused_widget.ancestors_with_self:
                if isinstance(ancestor, BlockComponent):
                    insert_index = ancestor.index + 1
                    break

        # ------------------------------------------------------------------
        #   2. Build new block widget & update indices afterwards
        # ------------------------------------------------------------------
        new = BlockComponent()
        new.text = ""
        new.index = insert_index

        dm.add_block(
            block=Block(text=new.text, language=new.language), index=insert_index
        )

        # Mount in the correct position.
        if insert_index >= len(container.children):
            container.mount(new)
        else:
            # Mount *after* the block at (insert_index -1) because indices are
            # 0-based and we want the new block **below** the current one.
            try:
                target_widget = list(container.children)[insert_index - 1]
                container.mount(new, after=target_widget)
            except IndexError:
                # Fallback – append if index calculation failed for some reason.
                container.mount(new)

        # ------------------------------------------------------------------
        #   3. Re-index existing widgets to maintain consistent IDs
        # ------------------------------------------------------------------
        for i, block_widget in enumerate(container.children):
            if isinstance(block_widget, BlockComponent):
                block_widget.index = i

        self.count = len(container.children)

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

    # ---------------------------------------------------------------------
    #   Help / command palette
    # ---------------------------------------------------------------------

    def _build_help_text(self) -> str:
        """Collect key bindings from the application and widgets.

        Returns a ready-to-render *plain* text block listing every binding in
        the format "<key> – <description>".
        """

        lines: list[str] = []

        def _extend(label: str, bindings: list[tuple[str, str, str]]):
            if not bindings:
                return
            lines.append(f"{label}:")
            for key, _action, description in bindings:
                lines.append(f"  {key:<10} {description}")
            lines.append("")

        # App-level bindings
        _extend("Global", self.BINDINGS)

        # Widget-specific – currently only TextAreaComponent has custom ones.
        from heynoterm.components import TextAreaComponent  # local import

        _extend("Inside Text Area", TextAreaComponent.BINDINGS)

        return "\n".join(lines)

    def action_show_help(self) -> None:
        """Toggle an on-screen help overlay (Ctrl+/)."""

        from textual.widgets import Static  # imported here to avoid circular deps

        existing_help = self.query("#help_modal").first()
        if existing_help is not None:
            existing_help.remove()
            return

        help_text = self._build_help_text()

        class HelpModal(Static):
            BINDINGS = [("escape", "close", "Close")]

            def action_close(self):  # noqa: D401 – Textual naming convention
                self.remove()

        modal = HelpModal(help_text, id="help_modal")
        # Give it a simple style via CSS classes – this keeps the code short.
        modal.styles.border = ("round", "white")
        modal.styles.background = "black"
        modal.styles.padding = (1, 2)
        modal.styles.dock = "top"
        modal.styles.height = "auto"

        self.mount(modal)
        modal.scroll_visible()
        modal.focus()


def main() -> None:
    """Run the app."""
    app = HeyNoteApp()
    app.run()


if __name__ == "__main__":
    main()
