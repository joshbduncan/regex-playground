import re

from textual.app import App
from textual.binding import Binding
from textual.validation import ValidationResult, Validator
from textual.widgets import Input


class ValidSubstitutionRegex(Validator):
    """Custom regular expression substitution string validator."""

    def __init__(self, app: App) -> None:  # type: ignore
        self.app = app
        super().__init__()

    def validate(self, value: str) -> ValidationResult:
        """Check if `value` is a valid regular expression substitution."""
        try:
            pattern = re.compile(self.app.regex)  # type: ignore[attr-defined]
            pattern.sub(value, "")
            return self.success()
        except (re.error, IndexError) as e:
            err = e.msg if hasattr(e, "msg") else str(e)
            return self.failure(err)


class SubstitutionInput(Input):
    """A custom input for a regular expression substitution string."""

    BINDINGS = [
        Binding("ctrl+x", "reset", "Reset Substitution"),
    ]

    @property
    def is_valid(self) -> bool:
        """Is the current value a valid regular expression substitution."""
        validation_result = self.validate(self.value)
        if validation_result and not validation_result.is_valid:
            return False
        return True

    def action_reset(self) -> None:
        """Reset the input."""
        self.value = ""
