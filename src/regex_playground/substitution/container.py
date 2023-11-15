from textual import on
from textual.app import ComposeResult
from textual.containers import Container
from textual.events import DescendantBlur

from ..text_inputs import TextResult
from .substitution_input import SubstitutionInput, ValidSubstitutionRegex


class SubstitutionContainer(Container):
    """A custom container for the `SubstitutionInput` and `TextResult` elements."""

    def compose(self) -> ComposeResult:
        """Create child widgets for the container."""
        yield SubstitutionInput(
            placeholder="Substitution Expression",
            validators=ValidSubstitutionRegex(app=self.app),
            id="substitution-input",
        )
        yield TextResult("", id="text-result")

    @on(DescendantBlur, "#text-result")
    def hide_cursor(self, event: DescendantBlur):
        """Hide the input TextArea cursor when in blur state."""
        event.widget.hide_cursor()  # type: ignore[attr-defined]
