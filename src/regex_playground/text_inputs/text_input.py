import re
from dataclasses import dataclass

from textual import on
from textual.events import Mount
from textual.widgets import TextArea

from ..expression.flags import FLAG_PATTERN


@dataclass
class ReNode:
    """A custom Node object for easy highlighting while using a TextArea."""

    start_point: tuple[int, int]
    end_point: tuple[int, int | None]


class TextInput(TextArea):
    HIGHLIGHT_NAME = "heading"

    @on(Mount)
    def hide_cursor(self) -> None:
        """Hack to hide the TextArea cursor when the widget is mounted."""
        self._cursor_blink_visible = False
        cursor_row, _ = self.cursor_location
        self.refresh_lines(cursor_row)

    def reset_highlighting(self) -> None:
        """Reset all TextArea highlighting."""
        highlights = self._highlights
        highlights.clear()
        self.refresh()

    def apply_highlighting(self, regex_str: str, global_match: bool) -> None:
        """Apply highlighting to RegEx matches inside of the TextArea.

        Args:
            regex_str: RegEx string.
            global_match: Should all matches be highlighted.
        """

        def convert_match_to_faux_node(match: re.Match[str]) -> ReNode:
            """Convert RegEx matches to "faux" nodes for highlighting.

            Args:
                match: A regular expression match object.

            Returns:
                A ReNode.
            """
            start = match.start()
            end = match.end()

            start_row = text.count("\n", 0, start)
            end_row = start_row + text.count("\n", start, end)
            start_offset = text[0:start][::-1].find("\n")
            end_offset = text[start:end][::-1].find("\n")

            start_col: int
            end_col: int | None
            start_col, end_col = match.span()

            if start_offset >= 0:
                start_col = start_offset

            if start_row == end_row:
                end_col = start_col + (end - start)
            else:
                if end_offset >= 0:
                    end_col = end_offset
                if end_col == 0:
                    end_row -= 1
                    end_col = None

            return ReNode(
                start_point=(start_row, start_col), end_point=(end_row, end_col)
            )

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
            node = convert_match_to_faux_node(match=match)
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
