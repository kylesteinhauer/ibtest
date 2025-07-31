"""
Pytest configuration and fixtures for IBTest tests.
"""

import pytest


@pytest.fixture
def sample_data():
    """
    Provide sample data for tests.
    
    Returns:
        dict: Sample data dictionary
    """
    return {
        "test_key": "test_value",
        "numbers": [1, 2, 3, 4, 5],
        "nested": {
            "inner_key": "inner_value"
        }
    }

