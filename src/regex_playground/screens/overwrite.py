from pathlib import Path

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Center, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label


class OverwriteModal(ModalScreen[bool]):
    """File overwrite modal screen."""

    BINDINGS = [
        Binding("escape", "dismiss_modal", show=False),
    ]

    def __init__(self, path: Path, *args, **kwargs) -> None:
        self.path = path
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        """Compose the content of the modal dialog."""
        with Vertical():
            with Center():
                yield Label("Overwrite File")
            yield Label(
                f"File {self.path.name} already exist. Overwrite it?",
                id="message",
            )
            with Horizontal():
                yield Button("Overwrite", variant="error", id="overwrite")
                yield Button("Cancel", variant="primary", id="cancel")

    def on_mount(self) -> None:
        """Focus the cancel button."""
        self.query_one("#cancel", Button).focus()

    @on(Button.Pressed)
    def action_dismiss_modal(self, event: Button.Pressed | None = None) -> None:
        """Dismiss the modal."""
        if event and event.button.id == "overwrite":
            self.dismiss(True)
        else:
            self.dismiss(False)
