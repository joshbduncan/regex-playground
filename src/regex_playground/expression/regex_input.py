import re

from textual.binding import Binding
from textual.validation import ValidationResult, Validator
from textual.widgets import Input


class ValidRegex(Validator):
    """Custom regular expression string validator."""

    def validate(self, value: str) -> ValidationResult:
        """Check if `value` is a valid regular expression."""
        try:
            re.compile(value)
            return self.success()
        except re.error as e:
            return self.failure(e.msg)


class RegexInput(Input):
    """A custom input for regular expression string."""

    BINDINGS = [
        Binding("ctrl+x", "reset", "Reset Expression"),
    ]

    @property
    def is_valid(self) -> bool:
        """Is the current value a valid regular expression."""
        validation_result = self.validate(self.value)
        if validation_result and not validation_result.is_valid:
            return False
        return True

    def action_reset(self) -> None:
        """Reset the input."""
        self.value = ""
