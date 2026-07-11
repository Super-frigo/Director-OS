"""Unit tests for director_os/cli.py — CLI entry point."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from director_os.cli import main


# ============================================================================
# Helpers
# ============================================================================

def _run_cli(*args, capsys):
    """Run the CLI with given argv and capture stdout/stderr."""
    old_argv = sys.argv
    try:
        sys.argv = ["director-os"] + list(args)
        main()
    except SystemExit as e:
        pass
    finally:
        sys.argv = old_argv
    return capsys.readouterr()


# ============================================================================
# 'new' command
# ============================================================================

def test_cli_new_with_title(capsys):
    out, err = _run_cli("new", "--title", "My Film", capsys=capsys)
    assert "My Film" in out


def test_cli_new_with_premise(capsys):
    out, err = _run_cli("new", "--premise", "A great story", capsys=capsys)
    assert "A great story" in out


def test_cli_new_defaults(capsys):
    out, err = _run_cli("new", capsys=capsys)
    assert "Untitled" in out or "Project created" in out


# ============================================================================
# 'validate' command
# ============================================================================

def test_cli_validate_valid_project(capsys):
    out, err = _run_cli("validate", "projects/the_hanging.md", capsys=capsys)
    assert "The Hanging" in out


def test_cli_validate_nonexistent(capsys):
    out, err = _run_cli("validate", "/nonexistent.md", capsys=capsys)
    assert "Error" in err


# ============================================================================
# 'load' command
# ============================================================================

def test_cli_load_valid_project(capsys):
    out, err = _run_cli("load", "projects/the_hanging.md", capsys=capsys)
    assert "The Hanging" in out
    assert "Production Intent generated" in out


def test_cli_load_with_compile(capsys):
    out, err = _run_cli("load", "projects/the_hanging.md", "--compile", "seedance", capsys=capsys)
    assert "SEEDANCE Prompt" in out.upper() or "Seedance" in out


def test_cli_load_nonexistent(capsys):
    out, err = _run_cli("load", "/nonexistent.md", capsys=capsys)
    assert "Error" in err
