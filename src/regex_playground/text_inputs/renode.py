import re
from dataclasses import dataclass


@dataclass
class ReNode:
    """A custom Node object for easy highlighting while using a `TextArea`."""

    start_point: tuple[int, int]
    end_point: tuple[int, int | None]


def match_to_faux_node(text: str, match: re.Match[str], offset: int = 0) -> ReNode:
    """Convert RegEx matches to "faux" nodes for highlighting.

    Args:
        text: Text to match against.
        match: A regular expression match object.
        offset: An amount to offset a match after a substitution.

    Returns:
        A ReNode.
    """
    start, end = match.span()

    start = start + offset if offset > 0 else start
    end = end + offset if offset < 0 else end

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

    return ReNode(start_point=(start_row, start_col), end_point=(end_row, end_col))
