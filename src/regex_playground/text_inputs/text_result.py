import re

from textual import on
from textual.events import Key
from textual.widgets import TextArea

from ..expression.flags import FLAG_PATTERN


class TextResult(TextArea):
    HIGHLIGHT_NAME = "heading"

    @on(Key)
    def block_keys(self, event: Key) -> None:
        """Block all key input within this TextArea."""
        event.prevent_default()

    def make_substitutions(self, text: str, regex_str: str, sub_str: str) -> None:
        """Apply RegEx substitutions to the contained text.

        Args:
            text: Text to match on.
            regex_str: RegEx string.
            sub_str: RegEx substitution string.
        """
        pattern = re.compile(regex_str)

        if not regex_str or not sub_str or not re.sub(FLAG_PATTERN, "", regex_str):
            self.load_text(text)
            return

        new_text = pattern.sub(sub_str, text)
        self.load_text(new_text)
