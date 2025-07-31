"""
Cointegration analysis module for statistical arbitrage and pairs trading.

This module provides tools for testing cointegration between time series
using the Engle-Granger method and other statistical tests.
"""

from typing import List, Dict, Tuple, Optional, Union
import pandas as pd
import numpy as np
from itertools import combinations
import warnings

try:
    from statsmodels.tsa.stattools import coint, adfuller
    from statsmodels.regression.linear_model import OLS
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False
    warnings.warn(
        "statsmodels not available. Install with: pip install statsmodels",
        ImportWarning
    )


class CointegrationResult:
    """
    Container for cointegration test results.
    """
    
    def __init__(
        self,
        symbol1: str,
        symbol2: str,
        cointegration_stat: float,
        p_value: float,
        critical_values: Dict[str, float],
        is_cointegrated: bool,
        hedge_ratio: float,
        spread_series: Optional[pd.Series] = None
    ):
        self.symbol1 = symbol1
        self.symbol2 = symbol2
        self.cointegration_stat = cointegration_stat
        self.p_value = p_value
        self.critical_values = critical_values
        self.is_cointegrated = is_cointegrated
        self.hedge_ratio = hedge_ratio
        self.spread_series = spread_series
    
    def __repr__(self) -> str:
        status = "✓" if self.is_cointegrated else "✗"
        return (f"CointegrationResult({self.symbol1}-{self.symbol2}: "
                f"{status} p={self.p_value:.4f}, hedge_ratio={self.hedge_ratio:.4f})")


class CointegrationAnalyzer:
    """
    Analyzer for testing cointegration between time series.
    
    This class provides methods to test for cointegration using the Engle-Granger
    method and filter pairs based on statistical significance.
    """
    
    def __init__(self, significance_level: float = 0.05):
        """
        Initialize the cointegration analyzer.
        
        Args:
            significance_level: P-value threshold for cointegration (default: 0.05)
        """
        if not STATSMODELS_AVAILABLE:
            raise ImportError(
                "statsmodels is required for cointegration analysis. "
                "Install with: pip install statsmodels"
            )
        
        self.significance_level = significance_level
    
    def test_cointegration(
        self,
        series1: pd.Series,
        series2: pd.Series,
        symbol1: str = "Series1",
        symbol2: str = "Series2"
    ) -> CointegrationResult:
        """
        Test cointegration between two time series using Engle-Granger method.
        
        Args:
            series1: First time series
            series2: Second time series
            symbol1: Name of first series
            symbol2: Name of second series
        
        Returns:
            CointegrationResult object with test results
        """
        # Align series and remove NaN values
        aligned_data = pd.DataFrame({symbol1: series1, symbol2: series2}).dropna()
        
        if len(aligned_data) < 10:
            raise ValueError("Insufficient data points for cointegration test")
        
        y1 = aligned_data[symbol1].values
        y2 = aligned_data[symbol2].values
        
        # Perform Engle-Granger cointegration test
        coint_stat, p_value, critical_values = coint(y1, y2)
        
        # Calculate hedge ratio using OLS regression
        # y1 = alpha + beta * y2 + error
        ols_result = OLS(y1, np.column_stack([np.ones(len(y2)), y2])).fit()
        hedge_ratio = ols_result.params[1]  # Beta coefficient
        
        # Calculate spread (residuals)
        spread = y1 - hedge_ratio * y2
        spread_series = pd.Series(spread, index=aligned_data.index)
        
        # Determine if cointegrated
        is_cointegrated = p_value < self.significance_level
        
        # Format critical values
        crit_vals = {
            "1%": critical_values[0],
            "5%": critical_values[1], 
            "10%": critical_values[2]
        }
        
        return CointegrationResult(
            symbol1=symbol1,
            symbol2=symbol2,
            cointegration_stat=coint_stat,
            p_value=p_value,
            critical_values=crit_vals,
            is_cointegrated=is_cointegrated,
            hedge_ratio=hedge_ratio,
            spread_series=spread_series
        )
    
    def test_stationarity(self, series: pd.Series, symbol: str = "Series") -> Dict:
        """
        Test if a time series is stationary using Augmented Dickey-Fuller test.
        
        Args:
            series: Time series to test
            symbol: Name of the series
        
        Returns:
            Dictionary with ADF test results
        """
        series_clean = series.dropna()
        
        if len(series_clean) < 10:
            raise ValueError("Insufficient data points for stationarity test")
        
        adf_stat, p_value, used_lag, nobs, critical_values, icbest = adfuller(
            series_clean, autolag='AIC'
        )
        
        is_stationary = p_value < self.significance_level
        
        return {
            'symbol': symbol,
            'adf_statistic': adf_stat,
            'p_value': p_value,
            'critical_values': critical_values,
            'is_stationary': is_stationary,
            'used_lag': used_lag,
            'n_observations': nobs
        }
    
    def analyze_pairs(
        self,
        price_data: pd.DataFrame,
        min_observations: int = 50
    ) -> List[CointegrationResult]:
        """
        Analyze all possible pairs in the price data for cointegration.
        
        Args:
            price_data: DataFrame with prices, symbols as columns
            min_observations: Minimum number of observations required
        
        Returns:
            List of CointegrationResult objects for all pairs
        """
        symbols = price_data.columns.tolist()
        results = []
        
        # Filter data to have minimum observations
        if len(price_data) < min_observations:
            warnings.warn(
                f"Insufficient data: {len(price_data)} < {min_observations} observations"
            )
        
        # Test all possible pairs
        for symbol1, symbol2 in combinations(symbols, 2):
            try:
                result = self.test_cointegration(
                    series1=price_data[symbol1],
                    series2=price_data[symbol2],
                    symbol1=symbol1,
                    symbol2=symbol2
                )
                results.append(result)
                
            except Exception as e:
                print(f"Error testing {symbol1}-{symbol2}: {e}")
                continue
        
        return results
    
    def filter_cointegrated_pairs(
        self,
        results: List[CointegrationResult],
        p_value_threshold: Optional[float] = None
    ) -> List[CointegrationResult]:
        """
        Filter results to only include cointegrated pairs.
        
        Args:
            results: List of CointegrationResult objects
            p_value_threshold: Override default significance level
        
        Returns:
            List of cointegrated pairs only
        """
        threshold = p_value_threshold or self.significance_level
        
        cointegrated = [
            result for result in results 
            if result.p_value < threshold
        ]
        
        # Sort by p-value (most significant first)
        cointegrated.sort(key=lambda x: x.p_value)
        
        return cointegrated
    
    def create_summary_report(
        self,
        results: List[CointegrationResult],
        include_all: bool = False
    ) -> pd.DataFrame:
        """
        Create a summary report of cointegration test results.
        
        Args:
            results: List of CointegrationResult objects
            include_all: Include all pairs or only cointegrated ones
        
        Returns:
            DataFrame with summary statistics
        """
        if include_all:
            filtered_results = results
        else:
            filtered_results = self.filter_cointegrated_pairs(results)
        
        if not filtered_results:
            return pd.DataFrame()
        
        summary_data = []
        for result in filtered_results:
            summary_data.append({
                'Symbol1': result.symbol1,
                'Symbol2': result.symbol2,
                'P_Value': result.p_value,
                'Cointegration_Stat': result.cointegration_stat,
                'Hedge_Ratio': result.hedge_ratio,
                'Is_Cointegrated': result.is_cointegrated,
                'Critical_1%': result.critical_values['1%'],
                'Critical_5%': result.critical_values['5%'],
                'Critical_10%': result.critical_values['10%']
            })
        
        df = pd.DataFrame(summary_data)
        df = df.sort_values('P_Value')
        
        return df
    
    def get_spread_statistics(
        self,
        result: CointegrationResult
    ) -> Dict[str, float]:
        """
        Calculate statistics for the spread of a cointegrated pair.
        
        Args:
            result: CointegrationResult object
        
        Returns:
            Dictionary with spread statistics
        """
        if result.spread_series is None:
            return {}
        
        spread = result.spread_series.dropna()
        
        return {
            'mean': spread.mean(),
            'std': spread.std(),
            'min': spread.min(),
            'max': spread.max(),
            'current': spread.iloc[-1] if len(spread) > 0 else np.nan,
            'z_score': (spread.iloc[-1] - spread.mean()) / spread.std() if len(spread) > 0 else np.nan
        }
    
    def print_results(
        self,
        results: List[CointegrationResult],
        show_all: bool = False,
        max_pairs: int = 10
    ) -> None:
        """
        Print cointegration analysis results in a formatted way.
        
        Args:
            results: List of CointegrationResult objects
            show_all: Show all pairs or only cointegrated ones
            max_pairs: Maximum number of pairs to display
        """
        if show_all:
            display_results = results[:max_pairs]
            print(f"\n=== Cointegration Analysis Results (Top {len(display_results)}) ===")
        else:
            cointegrated = self.filter_cointegrated_pairs(results)
            display_results = cointegrated[:max_pairs]
            print(f"\n=== Cointegrated Pairs Found: {len(cointegrated)} ===")
        
        if not display_results:
            print("No cointegrated pairs found at the specified significance level.")
            return
        
        print(f"{'Pair':<20} {'P-Value':<10} {'Hedge Ratio':<12} {'Status':<10}")
        print("-" * 55)
        
        for result in display_results:
            status = "✓ Coint" if result.is_cointegrated else "✗ Not"
            print(f"{result.symbol1}-{result.symbol2:<15} "
                  f"{result.p_value:<10.4f} "
                  f"{result.hedge_ratio:<12.4f} "
                  f"{status}")
        
        if len(results) > max_pairs:
            remaining = len(results) - max_pairs
            print(f"\n... and {remaining} more pairs")


def quick_cointegration_analysis(
    price_data: pd.DataFrame,
    significance_level: float = 0.05,
    print_results: bool = True
) -> List[CointegrationResult]:
    """
    Convenience function for quick cointegration analysis.
    
    Args:
        price_data: DataFrame with aligned price data
        significance_level: P-value threshold for significance
        print_results: Whether to print results
    
    Returns:
        List of CointegrationResult objects
    """
    analyzer = CointegrationAnalyzer(significance_level=significance_level)
    results = analyzer.analyze_pairs(price_data)
    
    if print_results:
        analyzer.print_results(results)
    
    return results

