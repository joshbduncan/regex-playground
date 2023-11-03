from pathlib import Path

from textual import on
from textual.app import ComposeResult
from textual.containers import Grid
from textual.events import Key
from textual.screen import Screen
from textual.widgets import Button, Input, Label


class SaveModal(Screen[Path | None]):
    """Screen with a dialog to quit."""

    def compose(self) -> ComposeResult:
        """Create child widgets for the container."""
        yield Grid(
            Label("Where you like to save the text file?", id="title"),
            Input(placeholder="Save Path", id="path-input"),
            Button("Save", variant="primary", id="save"),
            Button("Cancel", variant="error", id="cancel"),
            id="dialog",
        )

    @on(Key)
    def limit_key_input(self, event: Key) -> None:
        """Limit allowable key input while modal is active."""
        if event.key == "enter":
            self.return_path()
        elif event.key == "escape":
            self.cancel()
        elif event.key == "ctrl+c":
            self.app.exit()
        else:
            event.prevent_default()

    @on(Button.Pressed, "#save")
    def return_path(self) -> None:
        """Return the user supplied path on modal submission."""
        path_input = self.query_one("#path-input", Input)
        if not path_input.value:
            return
        self.dismiss(Path(path_input.value))

    @on(Button.Pressed, "#cancel")
    def cancel(self) -> None:
        """Exit the modal."""
        self.dismiss(None)
