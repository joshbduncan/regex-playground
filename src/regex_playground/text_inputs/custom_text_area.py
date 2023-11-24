import re
from collections.abc import Iterator

from textual.reactive import reactive
from textual.widgets import TextArea

from ..renode import ReNode
from .theme import THEME


class RegexTextArea(TextArea):
    """A custom `TextArea` widget with regular expression/substitution highlighting."""

    HIGHLIGHT_NAME: str = ""

    regex: reactive[str] = reactive("", init=False)
    global_match: reactive[bool] = reactive(True, init=False)

    def on_mount(self) -> None:
        """Actions to take when the widget is mounted within the app."""
        self.setup_theme()
        self.hide_cursor()

    def watch_regex(self, _: str, new_value: str) -> None:
        """Regular expression string updated."""
        self.update()

    def watch_global_match(self, _: str, new_value: str) -> None:
        """Regular expression string updated."""
        self.update()

    def setup_theme(self) -> None:
        """Register the custom text area theme and make it active."""
        self.register_theme(THEME)
        self.theme = "regex_playground"

    def hide_cursor(self) -> None:
        """Hack to hide the TextArea cursor when the widget is mounted."""
        self._cursor_blink_visible = False
        cursor_row, _ = self.cursor_location
        self.refresh_lines(cursor_row)

    def update(self) -> None:
        """Update matches and highlighting (define in subclass)."""
        pass

    def apply_highlighting(self, nodes: list[ReNode], global_match: bool) -> None:
        """Apply highlighting to regular expression matches inside of the TextArea.

        Args:
            nodes: Text area nodes to highlight.
            global_match: Should all matches be highlighted.
        """
        highlights = self._highlights
        highlights.clear()

        counter = 0
        for node in nodes:
            if not global_match and counter >= 1:
                break
            counter += 1

            node_start_row, node_start_column = node.start_point
            node_end_row, node_end_column = node.end_point

            self.log(f"highlighting {node=}")

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
        """Reset all highlighting."""
        highlights = self._highlights
        highlights.clear()
        self.refresh()

    def matches_to_faux_nodes(
        self, matches: Iterator[re.Match[str]], sub_str: str | None = None
    ) -> list[ReNode]:
        """Convert regular expression matches to "faux" nodes for highlighting.

        Args:
            matches: Regular expression matches for this text area.
            sub_str: Expression string to use for substitution.

        Returns:
            List of faux-nodes.
        """
        nodes: list[ReNode] = []

        offset = 0
        len_diff = 0
        for match in matches:
            start, end = match.span()

            if sub_str is not None:
                new_text = match.expand(sub_str)
                len_diff = len(new_text) - (end - start)
                start += offset
                end += offset + len_diff
                offset += len_diff

            start_col = start
            end_col = end

            start_row = self.text.count("\n", 0, start)
            end_row = start_row + self.text.count("\n", start, end)

            start_offset = self.text[0:start][::-1].find("\n")
            end_offset = self.text[start:end][::-1].find("\n")

            if start_offset >= 0:
                start_col = start_offset

            if start_row == end_row:
                end_col = start_col + (end - start)
            else:
                if end_offset >= 0:
                    end_col = end_offset
                if end_col == 0:
                    end_row -= 1

            node = ReNode(
                start_point=(start_row, start_col), end_point=(end_row, end_col)
            )
            nodes.append(node)

        return nodes
