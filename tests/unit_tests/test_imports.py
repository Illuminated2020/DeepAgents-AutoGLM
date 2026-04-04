"""Test importing files."""

from __future__ import annotations

import importlib
import sys


def test_package_import_is_lightweight() -> None:
    """Importing the package should not eagerly import the CLI entrypoint."""
    sys.modules.pop("deepagents_cli", None)
    sys.modules.pop("deepagents_cli.main", None)

    package = importlib.import_module("deepagents_cli")

    assert hasattr(package, "__version__")
    assert "deepagents_cli.main" not in sys.modules


def test_imports() -> None:
    """Test importing current deepagents modules."""
    from deepagents_cli import agent, integrations
    from deepagents_cli.main import cli_main

    assert agent is not None
    assert integrations is not None
    assert callable(cli_main)
