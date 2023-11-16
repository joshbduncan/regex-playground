import re
from dataclasses import dataclass

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Label

FLAG_PATTERN = re.compile(r"\(\?([a,i,L,m,s,u,x]*?)\)")


class Flag(Label, can_focus=True):  # type: ignore[call-arg]
    """A custom button with status coloring."""

    BINDINGS = [Binding("enter", "press", "Press Button", show=False)]

    status: reactive[bool] = reactive(False)

    @dataclass
    class Clicked(Message):
        """Posted when the user clicks a flag to toggle it."""

        letter: str  # re shortcode letter for the clicked Flag.

    def __init__(self, long_name: str, short_name: str, letter: str) -> None:
        """Initialize a Flag (Label) widget.

        Args:
            long_name: Regular expression flag long name.
            short_name: Regular expression flag short name.
            letter: Regular expression flag inline letter.
        """
        self.long_name = long_name
        self.short_name = short_name
        self.letter = letter
        super().__init__(
            f"{self.long_name} ({self.letter})", id=self.long_name.replace(".", "-")
        )

    def on_click(self) -> None:
        """A `Flag` was clicked."""
        self.post_message(self.Clicked(self.letter))

    def action_press(self) -> None:
        """Activate a press of the button."""
        self.post_message(self.Clicked(self.letter))

    def watch_status(self, _: str, new_status: str):
        """Update the styling (classes) on status change."""
        self.remove_class(f"-{'inactive' if new_status else 'active'}")
        self.add_class(f"-{'active' if new_status else 'inactive'}")


class Flags(Horizontal):
    """A custom container for the regular expression flag labels."""

    RE_FLAGS = {
        "re.ASCII": Flag(long_name="re.ASCII", short_name="re.A", letter="a"),
        "re.IGNORECASE": Flag(long_name="re.IGNORECASE", short_name="re.I", letter="i"),
        "re.MULTILINE": Flag(long_name="re.MULTILINE", short_name="re.M", letter="m"),
        "re.DOTALL": Flag(long_name="re.DOTALL", short_name="re.S", letter="s"),
        "re.UNICODE": Flag(long_name="re.UNICODE", short_name="re.U", letter="u"),
    }  # https://docs.python.org/3/library/re.html#flags

    def compose(self) -> ComposeResult:
        """Create child widgets for the container."""
        yield Label("🚩 Flags:", id="flags-label")
        yield from self.RE_FLAGS.values()

    def update(self, regex_str: str) -> None:
        """Update status for each flag.

        Args:
            regex_str: Regular expression string.
        """
        matched_flags = FLAG_PATTERN.match(regex_str)
        for flag in self.RE_FLAGS.values():
            if matched_flags is None or flag.letter not in matched_flags.group():
                flag.status = False
                continue
            if flag.letter in matched_flags.group():
                flag.status = True
