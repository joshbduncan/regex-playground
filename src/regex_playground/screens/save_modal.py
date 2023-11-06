from pathlib import Path

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Grid
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label


class SaveModal(ModalScreen[Path | None]):
    """Save As modal screen."""

    BINDINGS = [
        Binding("escape", "dismiss_modal", show=False),
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets for the container."""
        yield Grid(
            Label("Save As", id="title"),
            Input(placeholder="Save Path", id="path-input"),
            Button("Save", variant="primary", id="save"),
            Button("Cancel", variant="error", id="cancel"),
            id="dialog",
        )

    @on(Input.Submitted, "#path-input")
    @on(Button.Pressed, "#save")
    def action_return_path(self) -> None:
        """Return the user supplied path on modal submission."""
        path_input = self.query_one("#path-input", Input)
        if not path_input.value:
            return
        self.dismiss(Path(path_input.value))

    @on(Button.Pressed, "#cancel")
    def action_dismiss_modal(self) -> None:
        """Dismiss the modal."""
        self.dismiss(None)
