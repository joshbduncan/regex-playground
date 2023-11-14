from dataclasses import dataclass


@dataclass
class ReNode:
    """A custom Node object for easy highlighting while using a `RegexTextArea`."""

    start_point: tuple[int, int]
    end_point: tuple[int, int]
