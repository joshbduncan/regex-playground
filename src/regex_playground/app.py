import webbrowser
from pathlib import Path

from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.notifications import Notification, Notify
from textual.reactive import reactive
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

    text: reactive[str] = reactive("", init=False)
    regex: reactive[str] = reactive("", init=False)
    substitution: reactive[str] = reactive("", init=False)
    global_match: reactive[bool] = reactive(True, init=False)

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the application."""

        self._initial_text: str = ""
        self._initial_notifications: list[Notification] = []
        super().__init__(*args, **kwargs)

    @property
    def flags(self) -> Flags:
        """Quick access to the `Flags` widget."""
        return self.query_one("#flags", Flags)  # type: ignore[no-any-return]

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
            text_result.load_text(self._initial_text)

    def on_ready(self) -> None:
        """Set focus on the expression input and post any notifications."""
        regex_input = self.query_one("#regex-input", RegexInput)
        regex_input.focus()
        for notification in self._initial_notifications:
            self.post_message(Notify(notification))

    #################
    # WATCH METHODS #
    #################

    def watch_regex(self) -> None:
        """Regular expression string updated."""
        self.log(f"regular expression updated: {self.regex=}")
        self.flags_update()
        self.text_input_update()
        self.text_result_update()

    def watch_substitution(self) -> None:
        """Regular expression substitution string updated."""
        self.log(f"substitution expression updated: {self.substitution=}")
        self.text_result_update()

    def watch_global_match(self) -> None:
        """Global match toggled."""
        self.log(f"global match updated: {self.global_match=}")
        self.text_input_update()
        self.text_result_update()

    ############################
    # EXPRESSION INPUT METHODS #
    ############################

    @on(Input.Changed, "#regex-input")
    @on(Input.Changed, "#substitution-input")
    def process_expression_input(self, event: Input.Changed) -> None:
        """Update the regular expression strings or alert if not valid."""
        widget = event.control
        tooltip = None
        value = event.value
        if event.validation_result and not event.validation_result.is_valid:
            tooltip = event.validation_result.failure_descriptions[-1]
            value = ""
        widget.tooltip = tooltip
        if widget.id == "regex-input":
            self.regex = value
        else:
            self.substitution = value

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
            text_result.load_text(text)

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
    def update_text_areas(self, event: TextArea.Changed) -> None:
        """Update `TextResult` text, highlighting, and substitutions
        after `TextInput` changes."""
        text_result = self.query_one("#text-result", TextResult)
        text_result.load_text(event.control.text)
        self.text_input_update()
        self.text_result_update()

    ##################################
    # REGEX AND HIGHLIGHTING METHODS #
    ##################################

    @property
    def valid_regex_strings(self) -> bool:
        """Validate both `self.regex` and `self.substitution`. This is needed in cases
        where the substitution method is fired by something other than `Input.Changed`.
        """
        regex_input = self.query_one("#regex-input", RegexInput)
        substitution_input = self.query_one("#substitution-input", SubstitutionInput)
        if not regex_input.is_valid or not substitution_input.is_valid:
            return False
        return True

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

    def flags_update(self) -> None:
        """Toggle the status of any flags found in the regular expression string."""
        flags = self.query_one("#flags", Flags)
        flags.update(self.regex)

    def text_input_update(self) -> None:
        """Apply highlighting to `TextInput`."""
        text_input = self.query_one("#text-input", TextInput)
        text_input.update(self.regex, self.global_match)

    def text_result_update(self) -> None:
        """Apply substitutions and highlighting to `TextResult`."""
        text_input = self.query_one("#text-input", TextInput)
        text_result = self.query_one("#text-result", TextResult)
        if not self.valid_regex_strings:
            text_result.load_text(text_input.text)
        text_result.update(
            text_input.text,
            self.regex,
            self.substitution,
            self.global_match,
        )

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
