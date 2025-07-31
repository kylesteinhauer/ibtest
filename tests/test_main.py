"""
Tests for the main module of IBTest.
"""

import pytest
from ibtest.main import hello_world


def test_hello_world():
    """Test the hello_world function."""
    result = hello_world()
    assert result == "Hello from IBTest!"
    assert isinstance(result, str)


def test_hello_world_not_empty():
    """Test that hello_world returns a non-empty string."""
    result = hello_world()
    assert len(result) > 0


def test_sample_fixture(sample_data):
    """Test using the sample_data fixture."""
    assert "test_key" in sample_data
    assert sample_data["test_key"] == "test_value"
    assert len(sample_data["numbers"]) == 5

