"""
Tests for cointegration analysis functionality.
"""


import numpy as np
import pandas as pd
import pytest

from ibtest.analysis.cointegration import CointegrationAnalyzer, CointegrationResult


@pytest.fixture
def sample_price_data():
    """Create sample price data for testing."""
    # Create 100 days of hourly data
    dates = pd.date_range(start="2024-01-01", periods=100 * 24, freq="h")

    # Create cointegrated series
    np.random.seed(42)
    base_series = np.cumsum(np.random.randn(len(dates))) + 100

    # Create cointegrated pair (with some noise)
    cointegrated_series = 0.8 * base_series + np.random.randn(len(dates)) * 0.5 + 20

    # Create non-cointegrated series
    independent_series = np.cumsum(np.random.randn(len(dates))) + 150

    return pd.DataFrame(
        {
            "SYMBOL_A": base_series,
            "SYMBOL_B": cointegrated_series,
            "SYMBOL_C": independent_series,
        },
        index=dates,
    )


@pytest.fixture
def analyzer():
    """Create CointegrationAnalyzer instance."""
    return CointegrationAnalyzer(significance_level=0.05)


def test_cointegration_analyzer_init():
    """Test CointegrationAnalyzer initialization."""
    analyzer = CointegrationAnalyzer(significance_level=0.01)
    assert analyzer.significance_level == 0.01


def test_cointegration_test(analyzer, sample_price_data):
    """Test basic cointegration test functionality."""
    result = analyzer.test_cointegration(
        series1=sample_price_data["SYMBOL_A"],
        series2=sample_price_data["SYMBOL_B"],
        symbol1="SYMBOL_A",
        symbol2="SYMBOL_B",
    )

    assert isinstance(result, CointegrationResult)
    assert result.symbol1 == "SYMBOL_A"
    assert result.symbol2 == "SYMBOL_B"
    assert isinstance(result.p_value, float)
    assert isinstance(result.hedge_ratio, float)
    assert isinstance(result.cointegration_stat, float)
    assert isinstance(result.is_cointegrated, bool)
    assert result.spread_series is not None


def test_analyze_pairs(analyzer, sample_price_data):
    """Test analyzing multiple pairs."""
    results = analyzer.analyze_pairs(sample_price_data)

    # Should have 3 pairs: A-B, A-C, B-C
    assert len(results) == 3

    # All results should be CointegrationResult objects
    for result in results:
        assert isinstance(result, CointegrationResult)
        assert result.symbol1 in sample_price_data.columns
        assert result.symbol2 in sample_price_data.columns


def test_filter_cointegrated_pairs(analyzer, sample_price_data):
    """Test filtering cointegrated pairs."""
    results = analyzer.analyze_pairs(sample_price_data)
    cointegrated = analyzer.filter_cointegrated_pairs(results)

    # Should be a subset of all results
    assert len(cointegrated) <= len(results)

    # All filtered results should be cointegrated
    for result in cointegrated:
        assert result.is_cointegrated
        assert result.p_value < analyzer.significance_level


def test_create_summary_report(analyzer, sample_price_data):
    """Test creating summary report."""
    results = analyzer.analyze_pairs(sample_price_data)
    summary_df = analyzer.create_summary_report(results, include_all=True)

    assert isinstance(summary_df, pd.DataFrame)
    assert len(summary_df) == len(results)

    expected_columns = [
        "Symbol1",
        "Symbol2",
        "P_Value",
        "Cointegration_Stat",
        "Hedge_Ratio",
        "Is_Cointegrated",
        "Critical_1%",
        "Critical_5%",
        "Critical_10%",
    ]
    for col in expected_columns:
        assert col in summary_df.columns


def test_get_spread_statistics(analyzer, sample_price_data):
    """Test spread statistics calculation."""
    result = analyzer.test_cointegration(
        series1=sample_price_data["SYMBOL_A"],
        series2=sample_price_data["SYMBOL_B"],
        symbol1="SYMBOL_A",
        symbol2="SYMBOL_B",
    )

    stats = analyzer.get_spread_statistics(result)

    expected_keys = ["mean", "std", "min", "max", "current", "z_score"]
    for key in expected_keys:
        assert key in stats
        assert isinstance(stats[key], (int, float))


def test_test_stationarity(analyzer, sample_price_data):
    """Test stationarity testing."""
    # Test with a non-stationary series (price levels)
    result = analyzer.test_stationarity(sample_price_data["SYMBOL_A"], "SYMBOL_A")

    assert isinstance(result, dict)
    expected_keys = [
        "symbol",
        "adf_statistic",
        "p_value",
        "critical_values",
        "is_stationary",
        "used_lag",
        "n_observations",
    ]
    for key in expected_keys:
        assert key in result


def test_insufficient_data_error(analyzer):
    """Test error handling with insufficient data."""
    # Create very short series
    short_series = pd.Series([1, 2, 3, 4, 5])

    with pytest.raises(ValueError, match="Insufficient data points"):
        analyzer.test_cointegration(short_series, short_series)


def test_cointegration_result_repr():
    """Test CointegrationResult string representation."""
    result = CointegrationResult(
        symbol1="TEST1",
        symbol2="TEST2",
        cointegration_stat=-3.5,
        p_value=0.03,
        critical_values={"1%": -4.0, "5%": -3.4, "10%": -3.1},
        is_cointegrated=True,
        hedge_ratio=0.85,
    )

    repr_str = repr(result)
    assert "TEST1-TEST2" in repr_str
    assert "✓" in repr_str  # Should show checkmark for cointegrated
    assert "0.0300" in repr_str
    assert "0.8500" in repr_str


def test_empty_dataframe_handling(analyzer):
    """Test handling of empty DataFrames."""
    empty_df = pd.DataFrame()
    results = analyzer.analyze_pairs(empty_df)
    assert len(results) == 0


def test_single_column_dataframe(analyzer):
    """Test handling of single column DataFrame."""
    single_col_df = pd.DataFrame({"SYMBOL_A": [1, 2, 3, 4, 5]})
    results = analyzer.analyze_pairs(single_col_df)
    assert len(results) == 0  # No pairs to test
