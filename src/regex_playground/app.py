import webbrowser
from pathlib import Path

from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.events import Ready
from textual.reactive import reactive
from textual.widgets import Footer, Header, Rule

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

    regex: reactive[str] = reactive("", init=False)
    substitution: reactive[str] = reactive("", init=False)
    global_match: reactive[bool] = reactive(True, init=False)

    def __init__(self, *args, **kwargs):
        """Initialise the application."""

        self.text = ""
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

    def load_text(self, text: str) -> None:
        """Load text into the application.

        Args:
            text: Text to load.
        """
        self.text = text

    def load_file(self, file: str | Path) -> None:
        """Load a text file into the application.

        Args:
            file: File path.
        """
        if isinstance(file, str):
            file = Path(file)
        text = file.read_text()
        self.load_text(text)

    @on(Ready)
    def set_proper_focus(self) -> None:
        """Set focus on the expression input."""
        self.query_one("#regex-input", RegexInput).focus()

    @on(RegexInput.InputChanged)
    def update_regex_string(self, message: RegexInput.InputChanged) -> None:
        """Update `regex` reactive attribute on user input."""
        self.regex = message.expression

    @on(TextInput.Changed)
    def watch_regex(self) -> None:
        """Update application after a change to `regex` reactive attribute."""
        flags = self.query_one("#flags", Flags)
        flags.update_flags(regex_str=self.regex)
        text_input = self.query_one("#text-input", TextInput)
        text_result = self.query_one("#text-result", TextResult)
        text_input.apply_highlighting(
            regex_str=self.regex, global_match=self.global_match
        )
        text_result.make_substitutions(
            text=text_input.text,
            regex_str=self.regex,
            sub_str=self.substitution,
            global_match=self.global_match,
        )

    @on(TextInput.Changed)
    def update_text_result_text(self) -> None:
        """Update the result TextArea when the input TextArea changes."""
        text_input = self.query_one("#text-input", TextInput)
        text_result = self.query_one("#text-result", TextResult)
        text_result.load_text(text_input.text)

    @on(SubstitutionInput.InputChanged)
    def update_substitution_string(
        self, message: SubstitutionInput.InputChanged
    ) -> None:
        """Update `substitution` reactive attribute on user input."""
        self.substitution = message.expression

    @on(TextInput.Changed)
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

    def watch_global_match(self) -> None:
        """Update application after a change to `global match` reactive attribute."""
        self.watch_regex()

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
