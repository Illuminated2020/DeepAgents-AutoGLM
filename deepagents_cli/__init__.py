"""Deep Agents CLI - Interactive AI coding assistant."""

from deepagents_cli._version import __version__

__all__ = [
    "__version__",
    "cli_main",
]


def __getattr__(name: str) -> object:
    """Lazily expose expensive package attributes."""
    if name == "cli_main":
        from deepagents_cli.main import cli_main

        return cli_main
    msg = f"module {__name__!r} has no attribute {name!r}"
    raise AttributeError(msg)
