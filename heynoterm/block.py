from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widgets import Static
from heynoterm.components import LanguageList, MathResult, TextAreaComponent
from textual.css.query import NoMatches
from heynoterm.state import dm, Block, Language as LanguageType
from textual.containers import Horizontal


class BlockComponent(Static):
    """A widget to display a box around text. with a divider at top"""

    text = reactive("World")
    language = reactive("python")
    index = reactive(0)

    def compose(self) -> ComposeResult:
        """Compose the widget."""
        text_component = TextAreaComponent(
            self.text, name=self.text, id=f"TextAreaComponent_{self.index}"
        )
        text_component.register_language("javascript", "javascript")
        text_component.language = "python" if self.language == "math" else self.language
        text_component.math = self.language == "math"
        # theme="dracula" or "monokai" %2 == 0
        text_component.theme = "monokai" if self.index % 2 == 0 else "dracula"
        text_component.index = self.index
        # yield text_component
        with Horizontal(id=f"Horizontal_{self.index}"):
            if self.language == "math":
                math_res = MathResult()
                # yield Horizontal(
                #         text_component, math_res, id=f"Horizontal_{self.index}"
                #     )
                yield text_component
                yield math_res
            else:
                yield text_component

        # yield Rule(line_style="thick", id="rule1")

    def on_text_area_component_remove_block(
        self, event: TextAreaComponent.RemoveBlock
    ) -> None:
        print("remove parent")
        self.remove()
        dm.remove_block(index=self.index)

    async def on_text_area_component_change_language_list(
        self, event: TextAreaComponent.ChangeLanguageList
    ) -> None:
        try:
            # it will raise an error if it doesn't exist
            self.query_one("LanguageList").query_one("RadioSet").focus()

            return
        except NoMatches:
            pass

        language_list = LanguageList(id=f"LanguageList_{self.index}")
        language_list.language = self.language
        await self.mount(language_list)

        self.refresh()
        language_list.query_one("RadioSet").focus()

    def on_text_area_component_math_result_message(
        self, event: TextAreaComponent.MathResultMessage
    ) -> None:
        try:
            math_result_component = self.query_one("MathResult")
            math_result_component.results = event.results
            self.refresh()
        except NoMatches:
            pass

    async def on_language_list_language_changed(
        self, event: LanguageList.LanguageChanged
    ) -> None:
        print("language changed")
        print(event.language)
        self.query_one("LanguageList").remove()

        self.action_change_language(language=LanguageType(event.language))

    def update_math_result_component(self) -> None:
        if self.language != "math":
            try:
                math_result_component = self.query_one("MathResult")
                math_result_component.remove()
            except NoMatches:
                pass
            return
        try:
            math_result_component = self.query_one("MathResult")
            math_result_component.results = {}
            return
        except NoMatches:
            pass
        math_result_component = MathResult()
        container = self.query_one("Horizontal")
        container.mount(math_result_component)
        self.refresh()

    def action_change_language(self, language: LanguageType) -> None:
        self.language = language.value
        text_area = self.query_one("TextAreaComponent")
        text_area.language = "python" if self.language == "math" else self.language
        text_area.math = self.language == "math"
        self.update_math_result_component()

        # update state
        dm.update_block(self.index, Block(text=text_area.text, language=self.language))
        text_area.refresh()
        self.refresh()
