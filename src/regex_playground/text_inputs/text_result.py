import re
from pathlib import Path

from textual import on, work
from textual.binding import Binding
from textual.events import Key
from textual.message import Message
from textual.widgets import TextArea

from ..expression.flags import FLAG_PATTERN
from ..screens import SaveModal
from .theme import THEME


class TextResult(TextArea):
    """A custom `TextArea` with disabled input."""

    BINDINGS = [
        Binding("ctrl+r", "load_as_input", "Reset As Input", priority=True),
        Binding("ctrl+s", "save", "Save Result", priority=True),
    ]

    HIGHLIGHT_NAME = "match"

    class ResetInputWithResult(Message):
        """Posted when the user request to reset the input text to the result text."""

        text_area: TextArea
        """The `text_area` that sent this message."""

        def __init__(self, text_area: TextArea) -> None:
            self.text_area = text_area
            super().__init__()

        @property
        def control(self) -> TextArea:
            """The `TextArea` that sent this message."""
            return self.text_area

    def on_mount(self) -> None:
        """Actions to take when the widget is mounted within the app."""
        self.setup_theme()

    def setup_theme(self) -> None:
        """Register the app theme and make active."""
        self.register_theme(THEME)
        self.theme = "regex_playground"

    @on(Key)
    def block_keys(self, event: Key) -> None:
        """Block all key input within this TextArea."""
        event.prevent_default()

    def make_substitutions(
        self, text: str, regex_str: str, sub_str: str, global_match: bool
    ) -> None:
        """Apply RegEx substitutions to the contained text.

        Args:
            text: Text to match on.
            regex_str: RegEx string.
            sub_str: RegEx substitution string.
            global_match: Should all matches by substituted.
        """
        pattern = re.compile(regex_str)

        if not regex_str or not sub_str or not re.sub(FLAG_PATTERN, "", regex_str):
            self.load_text(text)
            return

        new_text = pattern.sub(sub_str, text, count=0 if global_match else 1)
        self.load_text(new_text)

    def action_load_as_input(self) -> None:
        """Set the input text to the current result text."""
        self.post_message(self.ResetInputWithResult(self))

    @work(exclusive=True)
    async def action_save(self) -> None:
        """Show `SaveModal` screen for saving the result TextArea to a file."""
        text = self.text

        def save_file(path: Path | None) -> None:
            """Save the result TextArea to a file.

            Args:
                path: File path.
            """
            if path is None:
                return
            try:
                if str(path).startswith("~"):
                    path = Path.expanduser(path)
                with open(path, "x") as f:
                    f.write(text)
                self.notify(f"{path}", title="File Saved", severity="information")
            except OSError as e:
                self.notify(f"{e}", title="Error Saving File", severity="warning")

        await self.app.push_screen(
            SaveModal(), callback=save_file, wait_for_dismiss=True
        )
