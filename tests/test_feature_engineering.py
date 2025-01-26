# import io
import json
from unittest.mock import patch, Mock

import pandas as pd
import pytest

from feature_engineering import heroes, hero_information

# Sample API response data for testing
MOCK_HERO_DATA = [
    {
        "hero_id": 1,
        "games": 10,
        "win": 5,
        "last_played": 1234567890,
        "with_games": 2,
        "with_win": 1,
        "against_games": 3,
        "against_win": 1
    },
    {
        "hero_id": 2,
        "games": 20,
        "win": 12,
        "last_played": 1234567890,
        "with_games": 4,
        "with_win": 2,
        "against_games": 6,
        "against_win": 3
    }
]

MOCK_PRIVATE_DATA = []


@pytest.fixture
def mock_response():
    """Fixture to create a mock response."""
    mock = Mock()
    mock.text = json.dumps(MOCK_HERO_DATA)
    return mock


def test_heroes_successful_request(mock_response):
    """Test the heroes function with a successful API call."""
    with patch('requests.request', return_value=mock_response):
        result = heroes("123456")
        assert isinstance(result, str)
        assert json.loads(result) == MOCK_HERO_DATA


def test_heroes_error_response():
    """Test the heroes function with an error response."""
    error_response = Mock()
    error_response.text = """{"error":"Internal Server Error"}"""

    with patch('requests.request', return_value=error_response):
        result = heroes("123456")
        assert result == """{"error":"Internal Server Error"}"""


def test_hero_information_successful():
    """Test hero_information with valid data."""
    with patch('feature_engineering.heroes',
               return_value=json.dumps(MOCK_HERO_DATA)):
        result = hero_information("123456")

        # Check if result is a pandas Series
        assert isinstance(result, pd.Series)

        # Check if basic statistics are correct
        assert result['total_games_played'] == 30  # 10 + 20
        assert result['total_winrate'] == (17/30)  # (5 + 12)/(10 + 20)

        # Check if hero-specific columns exist
        assert 'games_1' in result.index
        assert 'games_2' in result.index
        assert 'winrate_1' in result.index
        assert 'winrate_2' in result.index


def test_hero_information_private_account():
    """Test hero_information with a private account."""
    with patch('feature_engineering.heroes',
               return_value=json.dumps(MOCK_PRIVATE_DATA)):
        with pytest.raises(TypeError, match="Players information is private"):
            hero_information("123456")


def test_hero_information_server_error():
    """Test hero_information with initial server error then success."""
    error_response = """{"error":"Internal Server Error"}"""

    # Mock the heroes function to return error once, then success
    with patch('feature_engineering.heroes') as mock_heroes:
        mock_heroes.side_effect = [error_response, json.dumps(MOCK_HERO_DATA)]
        with patch('time.sleep'):  # Mock sleep to speed up tests
            result = hero_information("123456")

            assert isinstance(result, pd.Series)
            assert result['total_games_played'] == 30
