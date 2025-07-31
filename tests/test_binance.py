"""
Tests for Binance data source functionality.
"""

from unittest.mock import Mock, patch

import pandas as pd
import pytest

from ibtest.data.binance import BinanceDataSource


@pytest.fixture
def binance_client():
    """Create BinanceDataSource instance."""
    return BinanceDataSource(rate_limit_delay=0.01)  # Faster for testing


def test_binance_client_init():
    """Test BinanceDataSource initialization."""
    client = BinanceDataSource(rate_limit_delay=0.5)
    assert client.rate_limit_delay == 0.5
    assert client.BASE_URL == "https://api.binance.com/api/v3"


def test_get_symbol_list_default(binance_client):
    """Test getting default symbol list."""
    symbols = binance_client.get_symbol_list()

    assert isinstance(symbols, list)
    assert len(symbols) > 0
    assert all(symbol.endswith("USDT") for symbol in symbols)
    assert "BTCUSDT" in symbols
    assert "ETHUSDT" in symbols


def test_get_symbol_list_custom(binance_client):
    """Test getting custom symbol list."""
    custom_assets = ["BTC", "ETH", "ADA"]
    symbols = binance_client.get_symbol_list(base_assets=custom_assets)

    expected = ["BTCUSDT", "ETHUSDT", "ADAUSDT"]
    assert symbols == expected


@patch("ibtest.data.binance.requests.Session.get")
def test_fetch_klines_success(mock_get, binance_client):
    """Test successful klines fetching."""
    # Mock response data - first call returns data, second call returns empty to end loop
    mock_response_with_data = Mock()
    mock_response_with_data.raise_for_status.return_value = None
    mock_response_with_data.json.return_value = [
        [
            1640995200000,  # Open time
            "50000.00",  # Open
            "51000.00",  # High
            "49000.00",  # Low
            "50500.00",  # Close
            "100.50",  # Volume
            1640998799999,  # Close time
            "5050000.00",  # Quote volume
            1000,  # Number of trades
            "50.25",  # Taker buy base volume
            "2525000.00",  # Taker buy quote volume
            "0",  # Ignore
        ]
    ]

    mock_response_empty = Mock()
    mock_response_empty.raise_for_status.return_value = None
    mock_response_empty.json.return_value = []

    # First call returns data, subsequent calls return empty to terminate loop
    mock_get.side_effect = [mock_response_with_data, mock_response_empty]

    df = binance_client.fetch_klines("BTCUSDT", interval="1h", lookback_days=1)

    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert list(df.columns) == ["open", "high", "low", "close", "volume"]
    assert df.index.name == "timestamp"

    # Check data types
    assert df["open"].dtype == float
    assert df["close"].dtype == float
    assert df["volume"].dtype == float


@patch("ibtest.data.binance.requests.Session.get")
def test_fetch_klines_empty_response(mock_get, binance_client):
    """Test handling of empty API response."""
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = []
    mock_get.return_value = mock_response

    df = binance_client.fetch_klines("INVALID", interval="1h", lookback_days=1)

    assert isinstance(df, pd.DataFrame)
    assert df.empty


@patch("ibtest.data.binance.requests.Session.get")
def test_fetch_klines_api_error(mock_get, binance_client):
    """Test handling of API errors."""
    mock_get.side_effect = Exception("API Error")

    df = binance_client.fetch_klines("BTCUSDT", interval="1h", lookback_days=1)

    assert isinstance(df, pd.DataFrame)
    assert df.empty


@patch("ibtest.data.binance.BinanceDataSource.fetch_klines")
def test_fetch_multiple_symbols(mock_fetch_klines, binance_client):
    """Test fetching data for multiple symbols."""
    # Mock successful response for each symbol
    mock_df = pd.DataFrame(
        {
            "open": [100.0, 101.0],
            "high": [102.0, 103.0],
            "low": [99.0, 100.0],
            "close": [101.0, 102.0],
            "volume": [1000.0, 1100.0],
        },
        index=pd.date_range("2024-01-01", periods=2, freq="h"),
    )

    mock_fetch_klines.return_value = mock_df

    symbols = ["BTCUSDT", "ETHUSDT"]
    data = binance_client.fetch_multiple_symbols(
        symbols, interval="1h", lookback_days=1
    )

    assert isinstance(data, dict)
    assert len(data) == 2
    assert "BTCUSDT" in data
    assert "ETHUSDT" in data

    for _symbol, df in data.items():
        assert isinstance(df, pd.DataFrame)
        assert not df.empty


@patch("ibtest.data.binance.BinanceDataSource.fetch_multiple_symbols")
def test_get_aligned_prices(mock_fetch_multiple, binance_client):
    """Test getting aligned price data."""
    # Create mock data with different timestamps
    dates1 = pd.date_range("2024-01-01", periods=5, freq="h")
    dates2 = pd.date_range("2024-01-01 01:00:00", periods=5, freq="h")  # 1 hour offset

    mock_data = {
        "BTCUSDT": pd.DataFrame({"close": [100, 101, 102, 103, 104]}, index=dates1),
        "ETHUSDT": pd.DataFrame({"close": [200, 201, 202, 203, 204]}, index=dates2),
    }

    mock_fetch_multiple.return_value = mock_data

    aligned_df = binance_client.get_aligned_prices(["BTCUSDT", "ETHUSDT"])

    assert isinstance(aligned_df, pd.DataFrame)
    assert list(aligned_df.columns) == ["BTCUSDT", "ETHUSDT"]
    # Should have overlapping timestamps only
    assert len(aligned_df) <= min(len(dates1), len(dates2))


@patch("ibtest.data.binance.requests.Session.get")
def test_validate_symbols_success(mock_get, binance_client):
    """Test successful symbol validation."""
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "symbols": [
            {"symbol": "BTCUSDT", "status": "TRADING"},
            {"symbol": "ETHUSDT", "status": "TRADING"},
            {"symbol": "ADAUSDT", "status": "BREAK"},  # Not trading
        ]
    }
    mock_get.return_value = mock_response

    test_symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT", "INVALID"]
    valid, invalid = binance_client.validate_symbols(test_symbols)

    assert "BTCUSDT" in valid
    assert "ETHUSDT" in valid
    assert "ADAUSDT" not in valid  # Status is BREAK
    assert "INVALID" in invalid


@patch("ibtest.data.binance.requests.Session.get")
def test_validate_symbols_api_error(mock_get, binance_client):
    """Test symbol validation with API error."""
    mock_get.side_effect = Exception("API Error")

    test_symbols = ["BTCUSDT", "ETHUSDT"]
    valid, invalid = binance_client.validate_symbols(test_symbols)

    # Should return all as valid if validation fails
    assert valid == test_symbols
    assert invalid == []


def test_get_aligned_prices_empty_data(binance_client):
    """Test aligned prices with empty data."""
    with patch.object(binance_client, "fetch_multiple_symbols", return_value={}):
        aligned_df = binance_client.get_aligned_prices(["BTCUSDT"])

        assert isinstance(aligned_df, pd.DataFrame)
        assert aligned_df.empty


def test_get_aligned_prices_missing_column(binance_client):
    """Test aligned prices with missing price column."""
    mock_data = {
        "BTCUSDT": pd.DataFrame(
            {"open": [100, 101, 102]},  # Missing 'close' column
            index=pd.date_range("2024-01-01", periods=3, freq="h"),
        )
    }

    with patch.object(binance_client, "fetch_multiple_symbols", return_value=mock_data):
        aligned_df = binance_client.get_aligned_prices(
            ["BTCUSDT"], price_column="close"
        )

        assert isinstance(aligned_df, pd.DataFrame)
        assert aligned_df.empty
