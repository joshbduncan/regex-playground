from importlib.metadata import version

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Center, Vertical
from textual.events import Mount
from textual.screen import ModalScreen
from textual.widgets import Button, Static


class AboutModal(ModalScreen[None]):
    """About modal screen."""

    BINDINGS = [
        Binding("escape", "dismiss_modal", show=False),
    ]

    def compose(self) -> ComposeResult:
        """Compose the content of the modal dialog."""
        textual_link = "https://github.com/Textualize/textual"
        author_link = "https://github.com/joshbduncan"
        message = f"""Built with [@click=app.visit('{textual_link}')]Textual[/] by [@click=app.visit('{author_link}')]Josh Duncan[/]."""

        with Vertical():
            with Center():
                yield Static(
                    f"RegEx Playground [b dim]v{version('regex_playground')}", id="app"
                )
            yield Static(message, id="message")
            with Center():
                yield Button("OK", variant="primary")

    @on(Mount)
    def set_proper_focus(self) -> None:
        """Set focus on the expression input."""
        self.query_one(Button).focus()

    @on(Button.Pressed)
    def action_dismiss_modal(self) -> None:
        """Dismiss the modal."""
        self.dismiss(None)