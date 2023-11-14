import re

from textual.binding import Binding

from ..expression.flags import FLAG_PATTERN
from .custom_text_area import RegexTextArea


class TextInput(RegexTextArea):
    """A custom `TextArea` with regular expression match highlighting."""

    BINDINGS = [
        Binding("ctrl+r", "reset", "Reset Text"),
    ]

    HIGHLIGHT_NAME = "match"

    def action_reset(self) -> None:
        """Clear the text area."""
        self.clear()

    def update(self, regex_str: str, global_match: bool) -> None:
        """Update matches and highlighting with a new regular expression string.

        Args:
            regex_str: Regular expression string.
            global_match: Should all matches be highlighted.
        """
        if not regex_str or not re.sub(FLAG_PATTERN, "", regex_str):
            self.reset_highlighting()
            return
        pattern = re.compile(regex_str)
        matches = pattern.finditer(self.text)
        nodes = self.matches_to_faux_nodes(matches)
        self.apply_highlighting(nodes, global_match)
