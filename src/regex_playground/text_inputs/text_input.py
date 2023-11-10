import re

from textual.binding import Binding
from textual.widgets import TextArea

from ..expression.flags import FLAG_PATTERN
from .renode import match_to_faux_node
from .theme import THEME


class TextInput(TextArea):
    """A custom `TextArea` with RegEx match highlighting."""

    BINDINGS = [
        Binding("ctrl+r", "reset", "Reset Text"),
    ]

    HIGHLIGHT_NAME = "match"

    def on_mount(self) -> None:
        """Actions to take when the widget is mounted within the app."""
        self.setup_theme()
        self.hide_cursor()

    def setup_theme(self) -> None:
        """Register the app theme and make it active."""
        self.register_theme(THEME)
        self.theme = "regex_playground"

    def hide_cursor(self) -> None:
        """Hack to hide the TextArea cursor when the widget is mounted."""
        self._cursor_blink_visible = False
        cursor_row, _ = self.cursor_location
        self.refresh_lines(cursor_row)

    def apply_highlighting(self, regex_str: str, global_match: bool) -> None:
        """Apply highlighting to RegEx matches inside of the TextArea.

        Args:
            regex_str: RegEx string.
            global_match: Should all matches be highlighted.
        """

        if not regex_str or not re.sub(FLAG_PATTERN, "", regex_str):
            self.reset_highlighting()
            return

        highlights = self._highlights
        highlights.clear()

        pattern = re.compile(regex_str)
        text = self.text
        matches = re.finditer(pattern, text)

        counter = 0
        for match in matches:
            if not global_match and counter >= 1:
                break
            counter += 1

            node = match_to_faux_node(text=text, match=match)
            node_start_row, node_start_column = node.start_point
            node_end_row, node_end_column = node.end_point

            if node_start_row == node_end_row:
                highlight = (node_start_column, node_end_column, self.HIGHLIGHT_NAME)
                highlights[node_start_row].append(highlight)
            else:
                # Add the first line of the node range
                highlights[node_start_row].append(
                    (node_start_column, None, self.HIGHLIGHT_NAME)
                )

                # Add the middle lines - entire row of this node is highlighted
                for node_row in range(node_start_row + 1, node_end_row):
                    highlights[node_row].append((0, None, self.HIGHLIGHT_NAME))

                # Add the last line of the node range
                highlights[node_end_row].append(
                    (0, node_end_column, self.HIGHLIGHT_NAME)
                )

        self.refresh()

    def reset_highlighting(self) -> None:
        """Reset all TextArea highlighting."""
        highlights = self._highlights
        highlights.clear()
        self.refresh()

    def action_reset(self) -> None:
        self.clear()
