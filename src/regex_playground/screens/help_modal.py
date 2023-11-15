import webbrowser

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Center, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, Markdown

HELP_TEXT = """\
# Python RegEx Playground

Learn, Build, & Test Python Flavored RegEx inside your terminal. Simply enter some text into the input text area, enter a regular expression into the expression input, and watch your matches **light up**.

RegEx Playground supports most features of the Python `re` module like ⭐️ Metacharacters, 🚩 Flags, ❨❩ Groups, 🌎 Global Matching, and more...

For a better understanding of the Python `re` module, I suggest reading the official [Regular Expression HOWTO](https://docs.python.org/3/howto/regex.html#regex-howto) tutorial or going straight to the [module documentation](https://docs.python.org/3/library/re.html).

## 🤷‍♂️ How To Use

RegEx Playground is split into two halves.

### Top Half ⬆️

- Expression Input: This is where you enter a regular expression to test (including any flags). The results in the Text panel will update as you type.
- Text Panel: This is where you enter text to test your expression against. You can paste text directly into the text area, load text from a file via the `CTRL+L` keybinding, or load text via the command-line interface (CLI). Matches will be highlighted as you type.

### Bottom Half ⬇️

- Substitution Input: This is where you enter a regular expression substitution to go with your expression. The results in the Result panel will update as you type.
- Result Panel: This is where the resulting text (after substitution) is displayed.

## Other Options

- Global Toggle: RegEx Playground uses the `re.finditer` method to find all non-overlapping matches within your text. You can disable this with the `Ctrl+G` keybinding. When disabled, only the first match will be highlighted/substituted.
- Result as Input: Want to performance multiple operations on your text? Use `Ctrl+R` to reset the Text Panel with the text from the Result Panel.
- Saving: You can save the resulting text (after applying the substitution to your matches) via the `CTRL+S` keybinding. You must select the Result text area for this keybinding to be available.

## ❌ How to QUIT

Just use the keybinding "Ctrl+C" to quit the app at any time.

## More Info

You can find out more info about RegEx Playground in the [README](https://github.com/joshbduncan/regex-playground/blob/main/README.md).

🐇 Please know, regular expression can be a deep, deep rabbit hole. If you find something that doesn't work in the playground please [file an issue](https://github.com/joshbduncan/regex-playground/issues) and I'll take a look. Thanks!
"""


class HelpModal(ModalScreen[None]):
    """Help documentation modal screen."""

    BINDINGS = [
        Binding("escape,f1", "dismiss_modal", show=False),
    ]

    def compose(self) -> ComposeResult:
        with Vertical():
            with VerticalScroll():
                yield Markdown(HELP_TEXT)
            with Center():
                yield Button("Close", variant="primary")

    @on(Button.Pressed)
    def action_dismiss_modal(self) -> None:
        """Dismiss the modal."""
        self.dismiss(None)

    @on(Markdown.LinkClicked)
    def visit_link(self, event: Markdown.LinkClicked) -> None:
        """A link was clicked in the help document."""
        webbrowser.open(event.href)
