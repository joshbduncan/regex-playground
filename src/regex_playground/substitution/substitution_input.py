import re

from textual import on
from textual.app import App
from textual.binding import Binding
from textual.message import Message
from textual.validation import ValidationResult, Validator
from textual.widgets import Input


class ValidSubstitutionRegex(Validator):
    """Custom regular expression substitution validator."""

    def __init__(self, app: App[int]) -> None:
        self.app = app
        super().__init__()

    def validate(self, value: str) -> ValidationResult:
        """Check if `value` is a valid regular expression substitution."""
        try:
            pattern = re.compile(self.app.regex)  # type: ignore
            pattern.sub(value, "")
            return self.success()
        except (re.error, IndexError) as e:
            err = e.msg if hasattr(e, "msg") else str(e)
            return self.failure(err)


class SubstitutionInput(Input):
    """A custom input for a regular expression substitution."""

    BINDINGS = [
        Binding("ctrl+x", "reset", "Reset Substitution"),
    ]

    class InputChanged(Message):
        """Posted when the RegEx substitution input is changed."""

        def __init__(self, expression: str) -> None:
            self.expression = expression
            super().__init__()

    @on(Input.Changed)
    def update_input(self, event: Input.Changed) -> None:
        """Update application on validated user input."""
        if event.validation_result and not event.validation_result.is_valid:
            self.app.post_message(self.InputChanged(expression=""))
            self.tooltip = event.validation_result.failure_descriptions[-1]
            return
        self.tooltip = None
        self.app.post_message(self.InputChanged(expression=self.value))

    def action_reset(self) -> None:
        self.value = ""
