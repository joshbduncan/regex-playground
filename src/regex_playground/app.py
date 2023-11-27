import webbrowser
from pathlib import Path

from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.notifications import Notification, Notify
from textual.reactive import reactive
from textual.validation import ValidationResult
from textual.widgets import Footer, Header, Input, Rule, TextArea

from .expression import ExpressionContainer, Flags, RegexInput
from .expression.flags import FLAG_PATTERN, Flag
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
        Binding("ctrl+g", "global_match", "Global Toggle"),
    ]

    regex: reactive[str] = reactive("", init=False)
    substitution: reactive[str] = reactive("", init=False)
    global_match: reactive[bool] = reactive(True, init=False)

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the application."""

        self._initial_text: str = ""
        self._initial_notifications: list[Notification] = []
        super().__init__(*args, **kwargs)

    #########################
    # TUI SETUP AND STARTUP #
    #########################

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

    def on_mount(self) -> None:
        """Load text into the app."""
        if self._initial_text:
            text_input = self.query_one("#text-input", TextInput)
            text_result = self.query_one("#text-result", TextResult)
            text_input.load_text(self._initial_text)
            text_result.load_text(self._initial_text, True)

    def on_ready(self) -> None:
        """Set focus on the expression input and post any notifications."""
        regex_input = self.query_one("#regex-input", RegexInput)
        regex_input.focus()
        for notification in self._initial_notifications:
            self.post_message(Notify(notification))

    #################
    # WATCH METHODS #
    #################

    def watch_regex(self, _: str, new_value: str) -> None:
        """Regular expression string updated."""
        self.log(f"regular expression updated: {new_value=}")
        flags = self.query_one("#flags", Flags)
        text_input = self.query_one("#text-input", TextInput)
        text_result = self.query_one("#text-result", TextResult)
        flags.regex = text_input.regex = text_result.regex = new_value

    def watch_substitution(self, _: str, new_value: str) -> None:
        """Regular expression substitution string updated."""
        self.log(f"substitution expression updated: {new_value=}")
        text_result = self.query_one("#text-result", TextResult)
        text_result.substitution = new_value

    def watch_global_match(self, _: bool, new_value: bool) -> None:
        """Global match toggled."""
        self.log(f"global match updated: {new_value=}")
        text_input = self.query_one("#text-input", TextInput)
        text_result = self.query_one("#text-result", TextResult)
        text_input.global_match = text_result.global_match = new_value

    ############################
    # EXPRESSION INPUT METHODS #
    ############################

    @on(Input.Changed, "#regex-input")
    @on(Input.Changed, "#substitution-input")
    def process_expression_inputs(self, event: Input.Changed) -> None:
        """Update the regular expression strings or alert if not valid."""
        regex_input = self.query_one("#regex-input", RegexInput)
        substitution_input = self.query_one("#substitution-input", SubstitutionInput)

        #  Fir proper tui updates, I have to validate both inputs on a change to either
        widget = event.control
        if widget.id == "regex-input":
            self.regex = self.process_input_validation_result(
                widget, event.validation_result
            )
            self.substitution = self.process_input_validation_result(
                substitution_input,
                substitution_input.validate(substitution_input.value),
            )
        else:
            self.substitution = self.process_input_validation_result(
                widget, event.validation_result
            )
            self.regex = self.process_input_validation_result(
                regex_input,
                regex_input.validate(regex_input.value),
            )

    @staticmethod
    def process_input_validation_result(
        widget: Input, validation_result: ValidationResult | None
    ) -> str:
        value = widget.value or ""
        tooltip = None
        if validation_result and not validation_result.is_valid:
            tooltip = validation_result.failure_descriptions[-1]
            value = ""
        widget.tooltip = tooltip
        return value

    ###########################
    # TEXT AREA INPUT METHODS #
    ###########################

    def load_text(self, text: str, notification: Notification | None = None) -> None:
        """Load text into the application.

        Args:
            text: Text to load.
            notification: Message to display in an alert toast. Defaults to None.
        """
        if self.app._running:
            text_input = self.query_one("#text-input", TextInput)
            text_result = self.query_one("#text-result", TextResult)
            if text == text_input.text:
                return
            text_input.load_text(text)
            text_result.load_text(text, True)

            text_input.update()
            text_result.update()

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

    @on(TextInput.NewFile)
    def load_file_from_tui(self, message: TextInput.NewFile) -> None:
        self.load_file(message.path)

    @on(TextArea.Changed, "#text-input")
    def update_text_result_with_changes(self, event: TextArea.Changed) -> None:
        """Update `TextResult` text with changes from `TextInput`."""
        text_result = self.query_one("#text-result", TextResult)
        text_result.load_text(event.control.text, True)

    ##################################
    # REGEX AND HIGHLIGHTING METHODS #
    ##################################

    @on(Flag.Clicked)
    def clicked_flag(self, message: Flag.Clicked) -> None:
        """Update the regex string and ui when a flag is clicked"""
        flag_letter = message.letter
        regex_input = self.query_one("#regex-input", RegexInput)
        current_value = regex_input.value
        current_flags = FLAG_PATTERN.match(current_value)
        if current_flags:
            flags = current_flags.groups()[0]
            updated_flags = (
                flags.replace(flag_letter, "")
                if flag_letter in flags
                else flags + flag_letter
            )
            new_value = (
                FLAG_PATTERN.sub(f"(?{updated_flags})", current_value)
                if updated_flags
                else FLAG_PATTERN.sub("", current_value)
            )
        else:
            new_value = f"(?{flag_letter}){current_value}"
        regex_input.value = new_value
        regex_input.action_end()

    @on(TextResult.ResetInputWithResult)
    def reset_input_with_result(self, message: TextResult.ResetInputWithResult) -> None:
        """Reset the contents of `TextInput` with the contents of `TextResult`."""
        notification = Notification(
            "Result text was successfully loaded.",
            "Input Text Updated",
        )
        self.load_text(message.text, notification)

    #############################
    # KEYBINDING ACTION METHODS #
    #############################

    def action_global_match(self) -> None:
        """Toggle regular expression global match."""
        self.global_match = not self.global_match

    def action_visit(self, url: str) -> None:
        """Visit a web URL."""
        webbrowser.open(url)

    def action_about(self) -> None:
        """Show about modal."""
        self.push_screen(AboutModal())

    def action_help(self) -> None:
        """Show help modal."""
        self.push_screen(HelpModal())
