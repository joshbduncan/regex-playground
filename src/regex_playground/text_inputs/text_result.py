import re
from dataclasses import dataclass

from textual import on, work
from textual.binding import Binding
from textual.events import Key
from textual.message import Message
from textual.reactive import reactive
from textual_fspicker import FileSave

from ..expression.flags import FLAG_PATTERN
from ..screens.overwrite import OverwriteModal
from .custom_text_area import RegexTextArea


class TextResult(RegexTextArea):
    """A custom `TextArea` with disabled input."""

    BINDINGS = [
        Binding("ctrl+r", "load_as_input", "Reset As Input", priority=True),
        Binding("ctrl+x", "copy", "Copy Result", priority=True),
        Binding("ctrl+s", "save", "Save Result", priority=True),
    ]

    HIGHLIGHT_NAME = "sub"

    match_text: reactive[str] = reactive("", init=False)
    substitution: reactive[str] = reactive("", init=False)

    @dataclass
    class ResetInputWithResult(Message):
        """Posted when the user request to reset the input text to the result text."""

        text: str

    @on(Key)
    def block_keys(self, event: Key) -> None:
        """Block all key input within this TextArea."""
        event.prevent_default()

    def load_text(self, text: str, update_match_text: bool = False) -> None:
        """Load text into the TextArea and set the match text.

        Args:
            text: The text to load into the TextArea.
            update_match_text: Should the match text be updated?
        """
        if update_match_text:
            self.match_text = text
        super().load_text(text)

    def watch_match_text(self) -> None:
        """Match text updated."""
        self.update()

    def watch_substitution(self, _: str, new_value: str) -> None:
        """Regular expression substitution string updated."""
        self.update()

    def update(self) -> None:
        """Apply substitutions and update highlighting."""
        if (
            not self.regex
            or not self.substitution
            or not re.sub(FLAG_PATTERN, "", self.regex)
        ):
            self.load_text(self.match_text, True)
            return
        pattern = re.compile(self.regex)
        new_text = pattern.sub(
            self.substitution, self.match_text, count=0 if self.global_match else 1
        )
        self.load_text(new_text)
        matches = pattern.finditer(self.match_text)
        nodes = self.matches_to_faux_nodes(matches, self.substitution)
        self.apply_highlighting(nodes, self.global_match)

    def action_load_as_input(self) -> None:
        """Set the input text to the current result text."""
        self.post_message(self.ResetInputWithResult(self.text))

    def action_copy(self) -> None:
        """Copy the result text to the system clipboard."""
        if not self.text:
            self.notify(
                "There is no text to copy.", title="Nothing To Copy", severity="warning"
            )
            return
        self.app.copy_to_clipboard(self.text)
        self.notify(
            "Result text copied to the system clipboard.",
            title="Text Copied",
            severity="information",
        )

    @work(exclusive=True)
    async def action_save(self) -> None:
        """Show `SaveModal` screen for saving the result TextArea to a file."""
        if not self.text:
            self.notify(
                "There is no text to save.", title="Nothing To Save", severity="warning"
            )
            return

        path = await self.app.push_screen(
            FileSave(".", title="Save Text As"),
            wait_for_dismiss=True,
        )

        if (
            path is None
            or path.exists()
            and not await self.app.push_screen(
                OverwriteModal(path), wait_for_dismiss=True
            )
        ):
            return

        try:
            with open(path, "w") as f:
                f.write(self.text)
            self.notify(f"{path}", title="File Saved", severity="information")
        except OSError as e:
            self.notify(f"{e}", title="Error Saving File", severity="warning")
