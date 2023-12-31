import re
from dataclasses import dataclass
from pathlib import Path

from textual import on, work
from textual.binding import Binding
from textual.message import Message
from textual.widgets import TextArea
from textual_fspicker import FileOpen

from ..expression.flags import FLAG_PATTERN
from .custom_text_area import RegexTextArea


class TextInput(RegexTextArea):
    """A custom `TextArea` with regular expression match highlighting."""

    BINDINGS = [
        Binding("ctrl+l", "load_file", "Load File"),
        Binding("ctrl+r", "reset", "Reset Text"),
    ]

    HIGHLIGHT_NAME = "match"

    @dataclass
    class Clicked(Message):
        """Posted when the user clicks a flag to toggle it."""

        letter: str  # re shortcode letter for the clicked Flag.

    @dataclass
    class NewFile(Message):
        """Posted when a new file should be loaded."""

        path: Path

    @dataclass
    class MatchesFound(Message):
        """Posted when successful matches are found."""

        count: int

    @work(exclusive=True)
    async def action_load_file(self) -> None:
        """Load a text file into `TextInput`."""

        def load_file(path: Path | None) -> None:
            """Load a file into the main text area.

            Args:
                path: File path.
            """
            if path is None:
                return
            self.post_message(self.NewFile(path))

        await self.app.push_screen(
            FileOpen(".", title="Load Text File"),
            callback=load_file,
            wait_for_dismiss=True,
        )

    def action_reset(self) -> None:
        """Clear the text area."""
        self.clear()

    @on(TextArea.Changed)
    def update(self) -> None:
        """Update matches and highlighting."""
        if not self.regex or not re.sub(FLAG_PATTERN, "", self.regex):
            self.reset_highlighting()
            self.post_message(self.MatchesFound(0))
            return
        pattern = re.compile(self.regex)
        matches = pattern.finditer(self.text)
        nodes = self.matches_to_faux_nodes(matches)
        self.apply_highlighting(nodes, self.global_match)
        self.post_message(self.MatchesFound(len(nodes)))
