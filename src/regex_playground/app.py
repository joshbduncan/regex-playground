import webbrowser
from pathlib import Path

from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.notifications import Notification, Notify
from textual.reactive import reactive
from textual.widgets import Footer, Header, Rule, TextArea

from .expression import ExpressionContainer, Flags, RegexInput
from .screens import AboutModal, HelpModal
from .substitution import SubstitutionContainer, SubstitutionInput
from .text_inputs import TextInput, TextResult


class RegexPlayground(App[int]):
    """The main application class."""

    TITLE = "Python RegEx Playground"
    CSS_PATH = Path(__file__).parent.joinpath("style.tcss")
    BINDINGS = [
        Binding("f1", "help", "Help"),
        Binding("f2", "about", "About"),
        Binding("ctrl+q", "app.quit", "Quit"),
    ]

    text: reactive[str] = reactive("", init=False)
    regex: reactive[str] = reactive("", init=False)
    substitution: reactive[str] = reactive("", init=False)
    global_match: reactive[bool] = reactive(True, init=False)

    def __init__(self, *args, **kwargs):
        """Initialise the application."""

        self._initial_text: str = ""
        self._initial_notifications: list[Notification] = []
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        """Compose the main screen.

        Returns:
            The result of composing the screen.
        """
        yield Header()
        yield ExpressionContainer(id="expression-container")
        yield Rule(line_style="thick")
        yield SubstitutionContainer(id="substitution-container")
        yield Footer()

    def load_text(self, text: str, notification: Notification | None = None) -> None:
        """Load text into the application.

        Args:
            text: Text to load.
            notification: Message to display in an alert toast. Defaults to None.
        """
        if self.app._running:
            text_input = self.query_one("#text-input", TextInput)
            if text == text_input.text:
                return
            text_input.load_text(text)
            if notification:
                self.post_message(Notify(notification))
        else:
            self._initial_text = text
            if notification:
                self._initial_notifications.append(notification)

    def load_file(self, file: str | Path) -> None:
        """Load a text file into the application.

        Args:
            file: File path.
        """
        if isinstance(file, str):
            file = Path(file)
        text = file.read_text()
        notification = Notification(
            f"Text from {file.name} was loaded successfully.",
            "Input Text Updated",
        )
        self.load_text(text, notification)

    def on_mount(self) -> None:
        """Actions to take when the widget is mounted within the app."""
        if self._initial_text:
            text_input = self.query_one("#text-input", TextInput)
            text_result = self.query_one("#text-result", TextResult)
            text_input.load_text(self._initial_text)
            text_result.load_text(self._initial_text)

    def on_ready(self) -> None:
        """Set focus on the expression input."""
        self.query_one("#regex-input", RegexInput).focus()
        for notification in self._initial_notifications:
            self.post_message(Notify(notification))

    @on(ExpressionContainer.GlobalMatchToggled)
    def update_global_toggle(self) -> None:
        self.global_match = not self.global_match

    def watch_global_match(self) -> None:
        """Update application after a change to `global match` reactive attribute."""
        self.watch_regex()

    @on(RegexInput.InputChanged)
    def update_regex_string(self, message: RegexInput.InputChanged) -> None:
        """Update `regex` reactive attribute on user input."""
        self.regex = message.expression

    @on(TextArea.Changed, "#text-input")
    @on(SubstitutionInput.Changed, "#substitution-input")
    def validate_regex_inputs(self) -> bool:
        """Ensure both regex input strings are valid before performing the substitution."""
        regex_input = self.query_one("#regex-input", RegexInput)
        substitution_input = self.query_one("#substitution-input", SubstitutionInput)
        regex_input_validation_result = regex_input.validate(regex_input.value)
        substitution_validation_result = substitution_input.validate(
            substitution_input.value
        )
        if regex_input_validation_result and not regex_input_validation_result.is_valid:
            return False
        if (
            substitution_validation_result
            and not substitution_validation_result.is_valid
        ):
            return False
        return True

    @on(TextArea.Changed, "#text-input")
    def watch_regex(self) -> None:
        """Update application after a change to `regex` reactive attribute."""
        flags = self.query_one("#flags", Flags)
        flags.update_flags(regex_str=self.regex)
        text_input = self.query_one("#text-input", TextInput)
        text_result = self.query_one("#text-result", TextResult)

        text_input.apply_highlighting(
            regex_str=self.regex, global_match=self.global_match
        )

        if not self.validate_regex_inputs():
            text_result.reset_highlighting()
            text_result.load_text(text_input.text)
            return
        text_result.make_substitutions(
            text=text_input.text,
            regex_str=self.regex,
            sub_str=self.substitution,
            global_match=self.global_match,
        )

    @on(TextArea.Changed, "#text-input")
    def update_text_result_text(self, event: TextArea.Changed) -> None:
        """Update the result TextArea when the input TextArea changes."""
        text_result = self.query_one("#text-result", TextResult)
        text_result.load_text(event.control.text)

    @on(SubstitutionInput.InputChanged)
    def update_substitution_string(
        self, message: SubstitutionInput.InputChanged
    ) -> None:
        """Update `substitution` reactive attribute on user input."""
        self.substitution = message.expression

    @on(TextArea.Changed, "#text-input")
    def watch_substitution(self) -> None:
        """Update application after a change to `substitution` reactive attribute."""
        text_input = self.query_one("#text-input", TextInput)
        text_result = self.query_one("#text-result", TextResult)
        text_result.make_substitutions(
            text=text_input.text,
            regex_str=self.regex,
            sub_str=self.substitution,
            global_match=self.global_match,
        )

    @on(TextResult.ResetInputWithResult)
    def reset_input_with_result(self, message: TextResult.ResetInputWithResult) -> None:
        """Reset contents of `TextInput` with contents of `TextResult`."""
        notification = Notification(
            "Result text was successfully loaded.",
            "Input Text Updated",
        )
        self.load_text(message.control.text, notification)

    def action_visit(self, url: str) -> None:
        """Visit a web URL."""
        webbrowser.open(url)

    def action_about(self) -> None:
        """Show about modal."""
        self.push_screen(AboutModal())

    def action_help(self) -> None:
        """Show help modal."""
        self.push_screen(HelpModal())


if __name__ == "__main__":
    app = RegexPlayground()
    app.run()
