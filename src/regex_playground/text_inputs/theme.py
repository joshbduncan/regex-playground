from rich.style import Style
from textual.widgets.text_area import TextAreaTheme

THEME = TextAreaTheme(
    name="regex_playground",
    base_style=Style(color="#f8f8f2", bgcolor="#272822"),
    gutter_style=Style(color="#90908a", bgcolor="#272822"),
    cursor_style=Style(color="#272822", bgcolor="#f8f8f0"),
    cursor_line_style=Style(bgcolor="#3e3d32"),
    cursor_line_gutter_style=Style(color="#c2c2bf", bgcolor="#3e3d32"),
    bracket_matching_style=Style(bgcolor="#838889", bold=True),
    selection_style=Style(bgcolor="#65686a"),
    syntax_styles={
        "match": Style(bgcolor="#4ebf71", bold=True),  # $success color
        "sub": Style(bgcolor="#fea62b", bold=True),  # $warning color
    },
)
