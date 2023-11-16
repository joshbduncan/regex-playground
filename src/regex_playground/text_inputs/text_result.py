import re
from dataclasses import dataclass

from textual import on, work
from textual.binding import Binding
from textual.events import Key
from textual.message import Message
from textual_fspicker import FileSave

from ..expression.flags import FLAG_PATTERN
from ..screens.overwrite import OverwriteModal
from .custom_text_area import RegexTextArea


class TextResult(RegexTextArea):
    """A custom `TextArea` with disabled input."""

    BINDINGS = [
        Binding("ctrl+r", "load_as_input", "Reset As Input", priority=True),
        Binding("ctrl+s", "save", "Save Result", priority=True),
    ]

    HIGHLIGHT_NAME = "sub"

    @dataclass
    class ResetInputWithResult(Message):
        """Posted when the user request to reset the input text to the result text."""

        text: str

    @on(Key)
    def block_keys(self, event: Key) -> None:
        """Block all key input within this TextArea."""
        event.prevent_default()

    def update(
        self,
        match_text: str,
        regex_str: str,
        sub_str: str,
        global_match: bool,
    ) -> None:
        """Apply substitutions and update highlighting with
        new regular expression strings.

        Args:
            match_text: Original text to match on.
            regex_str: Regular expression string.
            sub_str: Expression string to use for substitution.
            global_match: Should all matches be highlighted.
        """
        if not regex_str or not sub_str or not re.sub(FLAG_PATTERN, "", regex_str):
            self.load_text(match_text)
            return
        pattern = re.compile(regex_str)
        new_text = pattern.sub(sub_str, match_text, count=0 if global_match else 1)
        self.load_text(new_text)
        matches = pattern.finditer(match_text)
        nodes = self.matches_to_faux_nodes(matches, sub_str)
        self.apply_highlighting(nodes, global_match)

    def action_load_as_input(self) -> None:
        """Set the input text to the current result text."""
        self.post_message(self.ResetInputWithResult(self.text))

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
