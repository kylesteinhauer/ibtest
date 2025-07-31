"""
Main module for IBTest package.

This module contains the core functionality for the IBTest package,
including cointegration analysis for market data.
"""

import argparse
from typing import List, Optional

import pandas as pd

from .analysis.cointegration import CointegrationAnalyzer
from .data.binance import BinanceDataSource
from .data.ibkr import IBKRDataSource, create_mock_stock_data

# Import plotting functions only when needed
try:
    from .utils.plotting import plot_cointegrated_pairs, save_all_plots

    PLOTTING_AVAILABLE = True
except ImportError:
    PLOTTING_AVAILABLE = False


def hello_world() -> str:
    """
    Return a simple greeting message.

    Returns:
        str: A greeting message
    """
    return "Hello from IBTest!"


def run_cointegration_analysis(
    symbols: Optional[List[str]] = None,
    data_source: str = "binance",
    interval: str = "1h",
    lookback_days: int = 90,
    significance_level: float = 0.05,
    plot_results: bool = True,
    save_plots: bool = False,
    output_dir: str = "plots",
) -> None:
    """
    Run complete cointegration analysis pipeline.

    Args:
        symbols: List of trading symbols to analyze
        data_source: Data source to use ("binance", "ibkr", "mock")
        interval: Time interval for data (e.g., "1h", "4h", "1d")
        lookback_days: Number of days of historical data
        significance_level: P-value threshold for cointegration
        plot_results: Whether to generate plots
        save_plots: Whether to save plots to files
        output_dir: Directory to save plots
    """
    print("🚀 Starting Cointegration Analysis")
    print("=" * 50)

    # Initialize data source
    if data_source.lower() == "binance":
        print("📊 Using Binance data source")
        data_client = BinanceDataSource()

        if symbols is None:
            symbols = data_client.get_symbol_list()[:10]  # Limit to 10 for demo

        print(f"📈 Fetching data for {len(symbols)} symbols: {symbols}")

        # Validate symbols
        valid_symbols, invalid_symbols = data_client.validate_symbols(symbols)
        if invalid_symbols:
            print(f"⚠️  Invalid symbols removed: {invalid_symbols}")

        # Fetch aligned price data
        price_data = data_client.get_aligned_prices(
            symbols=valid_symbols, interval=interval, lookback_days=lookback_days
        )

    elif data_source.lower() == "ibkr":
        print("📊 Using IBKR data source (stub)")
        data_client = IBKRDataSource()

        if symbols is None:
            symbols = data_client.get_stock_list()[:10]

        print(f"📈 Would fetch IBKR data for: {symbols}")
        print("⚠️  Using mock data instead (IBKR integration pending)")

        # Use mock data for now
        mock_data = create_mock_stock_data(symbols, days=lookback_days)
        price_data = pd.DataFrame(
            {symbol: df["close"] for symbol, df in mock_data.items()}
        )

    elif data_source.lower() == "mock":
        print("📊 Using mock data source")

        if symbols is None:
            symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "JPM"]

        print(f"📈 Generating mock data for: {symbols}")
        mock_data = create_mock_stock_data(symbols, days=lookback_days)
        price_data = pd.DataFrame(
            {symbol: df["close"] for symbol, df in mock_data.items()}
        )

    else:
        raise ValueError(f"Unknown data source: {data_source}")

    if price_data.empty:
        print("❌ No data retrieved. Exiting.")
        return

    print(
        f"✅ Data retrieved: {price_data.shape[0]} observations, {price_data.shape[1]} symbols"
    )
    print(f"📅 Date range: {price_data.index.min()} to {price_data.index.max()}")

    # Run cointegration analysis
    print("\n🔍 Running Cointegration Analysis")
    print("-" * 30)

    analyzer = CointegrationAnalyzer(significance_level=significance_level)
    results = analyzer.analyze_pairs(price_data)

    # Print results
    analyzer.print_results(results, show_all=False, max_pairs=10)

    # Get cointegrated pairs
    cointegrated_pairs = analyzer.filter_cointegrated_pairs(results)

    if cointegrated_pairs:
        print(f"\n✅ Found {len(cointegrated_pairs)} cointegrated pairs!")

        # Create summary report
        summary_df = analyzer.create_summary_report(results, include_all=False)
        if not summary_df.empty:
            print("\n📊 Top Cointegrated Pairs:")
            print(summary_df.head().to_string(index=False))

        # Generate plots if requested
        if plot_results:
            if not PLOTTING_AVAILABLE:
                print("⚠️  Matplotlib not available. Skipping plots.")
                print("   Install with: pip install matplotlib")
            else:
                try:
                    print("\n📈 Generating plots...")

                    if save_plots:
                        save_all_plots(results, price_data, output_dir)
                    else:
                        # Just show the main plots
                        from .utils.plotting import plot_time_series

                        # Plot time series
                        plot_time_series(
                            price_data, normalize=True, title="Normalized Price Series"
                        )

                        # Plot cointegrated pairs
                        plot_cointegrated_pairs(results, price_data, max_pairs=4)

                        # Show plots
                        import matplotlib.pyplot as plt

                        plt.show()

                except Exception as e:
                    print(f"⚠️  Error generating plots: {e}")
                    print("   Install with: pip install matplotlib")

    else:
        print(
            f"\n❌ No cointegrated pairs found at significance level {significance_level}"
        )
        print("💡 Try:")
        print("   - Increasing the significance level (e.g., 0.10)")
        print("   - Using more historical data")
        print("   - Trying different symbols")

    print(f"\n🎉 Analysis complete! Tested {len(results)} pairs total.")


def main() -> None:
    """
    Main entry point for the application.
    """
    parser = argparse.ArgumentParser(description="IBTest - Cointegration Analysis Tool")

    parser.add_argument(
        "--symbols",
        nargs="+",
        help="List of symbols to analyze (e.g., BTCUSDT ETHUSDT)",
    )
    parser.add_argument(
        "--data-source",
        choices=["binance", "ibkr", "mock"],
        default="binance",
        help="Data source to use (default: binance)",
    )
    parser.add_argument("--interval", default="1h", help="Time interval (default: 1h)")
    parser.add_argument(
        "--lookback-days",
        type=int,
        default=90,
        help="Number of days of historical data (default: 90)",
    )
    parser.add_argument(
        "--significance",
        type=float,
        default=0.05,
        help="Significance level for cointegration test (default: 0.05)",
    )
    parser.add_argument(
        "--no-plots", action="store_true", help="Disable plot generation"
    )
    parser.add_argument("--save-plots", action="store_true", help="Save plots to files")
    parser.add_argument(
        "--output-dir", default="plots", help="Directory to save plots (default: plots)"
    )
    parser.add_argument("--demo", action="store_true", help="Run demo with sample data")

    args = parser.parse_args()

    if args.demo:
        print("🎯 Running Demo Mode")
        run_cointegration_analysis(
            data_source="mock",
            plot_results=not args.no_plots,
            save_plots=args.save_plots,
            output_dir=args.output_dir,
        )
    else:
        run_cointegration_analysis(
            symbols=args.symbols,
            data_source=args.data_source,
            interval=args.interval,
            lookback_days=args.lookback_days,
            significance_level=args.significance,
            plot_results=not args.no_plots,
            save_plots=args.save_plots,
            output_dir=args.output_dir,
        )


if __name__ == "__main__":
    main()
