from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.events import DescendantBlur

from ..text_inputs import TextInput
from .flags import Flags
from .regex_input import RegexInput, ValidRegex


class ExpressionContainer(Container):
    BINDINGS = [
        Binding("ctrl+g", "global", "Global Toggle"),
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets for the container."""
        yield RegexInput(
            placeholder="Regular Expression", validators=ValidRegex(), id="regex-input"
        )
        yield Flags(id="flags")
        yield TextInput(self.app.text, id="text-input")  # type: ignore

    @on(DescendantBlur, control="#text-input")
    def hide_cursor(self, event: DescendantBlur):
        """Hide the input TextArea cursor with another widget is focused."""
        text_input: TextInput = event.control  # type: ignore
        text_input.hide_cursor()

    def action_global(self) -> None:
        self.app.global_match = not self.app.global_match  # type: ignore
