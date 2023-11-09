import sys
from argparse import ArgumentParser, Namespace
from collections.abc import Sequence
from importlib.metadata import version
from pathlib import Path

from regex_playground import RegexPlayground


def parse_args(argv: Sequence[str] | None = None) -> Namespace:
    """Parse command line arguments.

    Args:
        argv: Sequence of command line arguments. Defaults to None.

    Returns:
        Parsed arguments.
    """
    parser = ArgumentParser(
        description="Learn, Build, & Test Python Flavored RegEx.",
        epilog="Copyright 2023 Josh Duncan (joshbduncan.com)",
    )
    parser.add_argument(
        "file",
        type=Path,
        nargs="*",
        help="text to load into the playground",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {version('regex_playground')}",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """Parse command line arguments, and run application.

    Args:
        argv: Sequence of command line arguments. Defaults to None.

    Returns:
        Exit code.
    """
    args = parse_args(argv)

    app = RegexPlayground()
    if args.file:
        file = args.file[0]
        app.load_file(file)
    else:
        text = Path(__file__).parent.joinpath("zen.txt").read_text()
        app.load_text(text)

    return app.run()  # type: ignore


if __name__ == "__main__":
    sys.exit(main())
