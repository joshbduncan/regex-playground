from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.events import DescendantBlur
from textual.message import Message

from ..text_inputs import TextInput
from .flags import Flags
from .regex_input import RegexInput, ValidRegex


class ExpressionContainer(Container):
    """A custom container for the `RegexInput`, `Flags`, and `TextInput` elements."""

    BINDINGS = [
        Binding("ctrl+g", "global", "Global Toggle"),
    ]

    class GlobalMatchToggled(Message):
        """Posted when the global match feature is toggled."""

    def compose(self) -> ComposeResult:
        """Create child widgets for the container."""
        yield RegexInput(
            placeholder="Regular Expression", validators=ValidRegex(), id="regex-input"
        )
        yield Flags(id="flags")
        yield TextInput(id="text-input")

    @on(DescendantBlur, control="#text-input")
    def hide_cursor(self, event: DescendantBlur):
        """Hide the input TextArea cursor with another widget is focused."""
        text_input: TextInput = event.control  # type: ignore
        text_input.hide_cursor()

    def action_global(self) -> None:
        self.post_message(self.GlobalMatchToggled())
