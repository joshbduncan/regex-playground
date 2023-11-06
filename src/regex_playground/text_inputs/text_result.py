import re
from pathlib import Path

from textual import on, work
from textual.binding import Binding
from textual.events import Key
from textual.widgets import TextArea

from ..expression.flags import FLAG_PATTERN
from ..screens import SaveModal


class TextResult(TextArea):
    HIGHLIGHT_NAME = "heading"

    BINDINGS = [
        Binding("ctrl+s", "save", "Save Result", priority=True),
    ]

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
