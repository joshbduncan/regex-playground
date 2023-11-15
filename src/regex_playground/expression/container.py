from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.events import DescendantBlur
from textual.widgets import Static

from ..text_inputs import TextInput
from .flags import Flags
from .regex_input import RegexInput, ValidRegex


class ExpressionContainer(Container):
    """A custom container for the `RegexInput`, `Flags`, and `TextInput` elements."""

    def compose(self) -> ComposeResult:
        """Create child widgets for the container."""
        with Horizontal(id="regex-input-container"):
            yield RegexInput(
                placeholder="Regular Expression",
                validators=ValidRegex(),
                id="regex-input",
            )
            yield Static("", id="matches-alert")
        yield Flags(id="flags")
        yield TextInput(id="text-input")

    @on(TextInput.MatchesFound)
    def updated_substitutions_alert(self, message: TextInput.MatchesFound) -> None:
        matches_alert = self.query_one("#matches-alert", Static)
        msg = f"{message.count} matches" if message.count else ""
        matches_alert.update(msg)

    @on(DescendantBlur, control="#text-input")
    def hide_cursor(self, event: DescendantBlur):
        """Hide the input TextArea cursor with another widget is focused."""
        text_input: TextInput = event.control  # type: ignore[assignment]
        text_input.hide_cursor()
