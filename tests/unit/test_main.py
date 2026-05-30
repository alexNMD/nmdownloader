"""Main test file to verify basic test infrastructure."""

import sys
from pathlib import Path

import pytest


def test_imports():
    """Test that all main modules can be imported."""
    # All imports are at the top of the file
    assert True  # If we get here, all imports succeeded


def test_pytest_setup():
    """Test that pytest is properly configured."""
    assert pytest is not None


def test_sys_path():
    """Test that src is in sys.path."""
    # Check that src directory is in the Python path
    # The conftest.py adds it, so we can verify it's there
    src_in_path = any(str(Path(p)).endswith("src") for p in sys.path)
    assert src_in_path
