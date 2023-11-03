import re

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.reactive import reactive
from textual.widgets import Static

FLAG_PATTERN = re.compile(r"\(\?[a,i,L,m,s,u,x]*?\)")


class Flag(Static):
    """A custom Static element with status coloring."""

    status: reactive[bool] = reactive(False)

    def __init__(self, long_name: str, short_name: str, letter: str) -> None:
        """Initialize a Flag (Static) widget.

        Args:
            long_name: RegEx flag long name.
            short_name: RegEx flag short name.
            letter: RegEx flag inline letter.
        """
        self.long_name = long_name
        self.short_name = short_name
        self.letter = letter
        super().__init__(self.long_name, id=self.long_name.replace(".", "-"))
        self.tooltip = f"(?{self.letter})"

    def watch_status(self, _: str, new_status: str):
        """Update the styling (classes) on status change."""
        self.remove_class(f"-{'inactive' if new_status else 'active'}")
        self.add_class(f"-{'active' if new_status else 'inactive'}")


class Flags(Horizontal):
    """A custom container to RegEx flag labels."""

    RE_FLAGS = [
        Flag(long_name="re.ASCII", short_name="re.A", letter="a"),
        Flag(long_name="re.IGNORECASE", short_name="re.I", letter="i"),
        Flag(long_name="re.MULTILINE", short_name="re.M", letter="m"),
        Flag(long_name="re.DOTALL", short_name="re.S", letter="s"),
        Flag(long_name="re.UNICODE", short_name="re.U", letter="u"),
    ]  # https://docs.python.org/3/library/re.html#flags

    def compose(self) -> ComposeResult:
        """Create child widgets for the container."""
        yield Static("Flags:", id="flags-label")
        for flag in self.RE_FLAGS:  # noqa: UP028
            yield flag

    def update_flags(self, regex_str: str) -> None:
        """Update status for each flag.

        Args:
            regex_str: RegEx string.
        """
        matched_flags = FLAG_PATTERN.match(regex_str)
        flags = self.query(Flag)
        for flag in flags:
            if matched_flags is None or flag.letter not in matched_flags.group():
                flag.status = False
                continue
            if flag.letter in matched_flags.group():
                flag.status = True
