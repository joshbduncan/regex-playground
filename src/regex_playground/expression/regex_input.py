import re

from textual import on
from textual.binding import Binding
from textual.message import Message
from textual.validation import ValidationResult, Validator
from textual.widgets import Input


class ValidRegex(Validator):
    """Custom regular expression validator."""

    def validate(self, value: str) -> ValidationResult:
        """Check if `value` is a valid regular expression."""
        try:
            re.compile(value)
            return self.success()
        except re.error as e:
            return self.failure(e.msg)


class RegexInput(Input):
    """A custom input for a regular expression."""

    BINDINGS = [
        Binding("ctrl+x", "reset", "Reset Expression"),
    ]

    class InputChanged(Message):
        """Posted when the RegEx input is changed."""

        def __init__(self, expression: str) -> None:
            self.expression = expression
            super().__init__()

    @on(Input.Changed)
    def update_input(self, event: Input.Changed) -> None:
        """Update application on validated user input."""
        if event.validation_result and not event.validation_result.is_valid:
            self.tooltip = event.validation_result.failure_descriptions[-1]
            self.app.post_message(self.InputChanged(expression=""))
            return
        self.tooltip = None
        self.app.post_message(self.InputChanged(expression=self.value))

    def action_reset(self) -> None:
        self.value = ""
