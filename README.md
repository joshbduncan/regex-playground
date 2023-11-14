# Python RegEx Playground

Learn, Build, & Test Python Flavored Regular Expressions inside of your terminal. Simply enter some text into the input text area, enter a regular expression into the expression input, and watch your matches **light up**.

RegEx Playground supports most features of the Python `re` module. For a better understanding of the Python `re` module, I suggest reading the official [Regular Expression HOWTO](https://docs.python.org/3/howto/regex.html#regex-howto) tutorial or going straight to the [module documentation](https://docs.python.org/3/library/re.html).

![regex-playground_v0 1 0](https://github.com/joshbduncan/regex-playground/assets/44387852/0818070e-d31f-486d-90b7-5f0b33c99244)

## Features

- ⭐️ Metacharacters
- 🚩 Flags
- ❨❩ Groups
- 🌎 Global Matching
- 💻 CLI
- 💾 Saving
- 👍 & more...

## ⭐️ Metacharacters

Most letters and characters will simply match themselves but there are exceptions to this rule; some characters are special metacharacters, and don't match themselves. Instead, they signal that some out-of-the-ordinary thing should be matched, or they affect other portions of your regular expression by repeating them or changing their meaning.

Here's a complete list of the metacharacters; their meanings are discussed in detail [here](https://docs.python.org/3/howto/regex.html#matching-characters).

`. ^ $ * + ? { } [ ] \ | ( )`

## 🚩 Flags

You can use any of the supported in-line flags below within the expression input by prepending your expression `(?aimsu)`.

- re.A, re.ASCII - Make \w, \W, \\b, \B, \d, \D, \s and \S perform ASCII-only matching instead of full Unicode matching. This is only meaningful for Unicode patterns and is ignored for byte patterns. Corresponds to the inline flag (?a).
- re.I, re.IGNORECASE - Perform case-insensitive matching; expressions like [A-Z] will also match lowercase letters. Full Unicode matching (such as Ü matching ü) also works unless the re.ASCII flag is used to disable non-ASCII matches. The current locale does not change the effect of this flag unless the re.LOCALE flag is also used. Corresponds to the inline flag (?i).
- re.M, re.MULTILINE - When specified, the pattern character '^' matches at the beginning of the string and at the beginning of each line (immediately following each newline); and the pattern character '$' matches at the end of the string and at the end of each line (immediately preceding each newline). By default, '^' matches only at the beginning of the string, and '$' only at the end of the string and immediately before the newline (if any) at the end of the string. Corresponds to the inline flag (?m).
- re.S, re.DOTALL - Make the '.' special character match any character at all, including a newline; without this flag, '.' will match anything except a newline. Corresponds to the inline flag (?s)
- re.U, re.UNICODE - In Python 2, this flag made special sequences include Unicode characters in matches. Since Python 3, Unicode characters are matched by default.

## ❨❩ Groups

Frequently you need to obtain more information than just whether your regular expression matches or not. Regular expressions are often used to dissect strings by writing a regular expression divided into several subgroups that match different components of interest. For example, an RFC-822 header line is divided into a header name and a value, separated by a ':', like this:

```
From: author@example.com
User-Agent: Thunderbird 1.5.0.9 (X11/20061227)
MIME-Version: 1.0
To: editor@example.com
```

This can be handled by writing a regular expression that matches an entire header line and has one group which matches the header name, and another group that matches the header’s value.

Groups are marked by the '(', ')' metacharacters. '(' and ')' have much the same meaning as they do in mathematical expressions; they group together the expressions contained inside them, and you can repeat the contents of a group with a quantifier, such as *, +, ?, or {m,n}. For example, (ab)* will match zero or more repetitions of ab.

Learn all there is to know about grouping in the [Regular Expression HOWTO](https://docs.python.org/3/howto/regex.html#grouping)

## 🌎 Global Matching

By default, global matching is enabled. This means that all matches for your regular expression will be highlighted and substituted.

To toggle global matching you can use the keybinding `CTRL+G` while inside of the Regular Expression input or the input text area. You can also click the `Global Toggle` option in the footer menu.

## 💻 CLI

You can load content directly into RegEx Playground using the CLI. Just specify a path like `$ regex-playgound file.txt` when running the application.

```bash
$ regex-playground -h
usage: regex-playground [-h] [--version] [file ...]

Learn, Build, & Test Python Flavored RegEx.

positional arguments:
  file        text to load into the playground

options:
  -h, --help  show this help message and exit
  --version   show program's version number and exit

Copyright 2023 Josh Duncan (joshbduncan.com)
```

## 💾 Saving

You can save the resulting text (after applying the substitution to your matches) via the `CTRL+S` keybinding.

## Rabbit Holes

Please know, Regular Expressions can be a deep, deep rabbit hole. If you find something that doesn't work in the playground please [file an issue](https://github.com/joshbduncan/regex-playground/issues) and I'll take a look. Thanks!

## Resources

- [Textual](https://github.com/Textualize/textual)
- [Python Regular Expressions](https://docs.python.org/3/library/re.html)
