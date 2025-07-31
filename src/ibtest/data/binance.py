"""
Binance data source for fetching historical market data.

This module provides functionality to fetch OHLCV data from Binance public REST API.
"""

import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import pandas as pd
import requests


class BinanceDataSource:
    """
    Data source for fetching historical price data from Binance.

    This class provides methods to fetch OHLCV data for trading pairs
    using Binance's public REST API.
    """

    BASE_URL = "https://api.binance.com/api/v3"

    def __init__(self, rate_limit_delay: float = 0.1):
        """
        Initialize the Binance data source.

        Args:
            rate_limit_delay: Delay between API requests to avoid rate limiting
        """
        self.rate_limit_delay = rate_limit_delay
        self.session = requests.Session()

    def get_symbol_list(self, base_assets: Optional[List[str]] = None) -> List[str]:
        """
        Get a default list of trading pairs for analysis.

        Args:
            base_assets: List of base assets to include (e.g., ['BTC', 'ETH'])
                        If None, uses a default set of major cryptocurrencies

        Returns:
            List of trading pair symbols (e.g., ['BTCUSDT', 'ETHUSDT'])
        """
        if base_assets is None:
            base_assets = [
                "BTC",
                "ETH",
                "BNB",
                "ADA",
                "XRP",
                "SOL",
                "DOT",
                "DOGE",
                "AVAX",
                "SHIB",
                "MATIC",
                "LTC",
                "UNI",
                "LINK",
                "ATOM",
            ]

        return [f"{asset}USDT" for asset in base_assets]

    def fetch_klines(
        self,
        symbol: str,
        interval: str = "1h",
        lookback_days: int = 90,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> pd.DataFrame:
        """
        Fetch historical kline/candlestick data for a symbol.

        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            interval: Kline interval ('1m', '5m', '1h', '4h', '1d', etc.)
            lookback_days: Number of days to look back from current time
            start_time: Start time for data fetch (overrides lookback_days)
            end_time: End time for data fetch (defaults to current time)

        Returns:
            DataFrame with columns: timestamp, open, high, low, close, volume
        """
        # Calculate time range
        if end_time is None:
            end_time = datetime.now()

        if start_time is None:
            start_time = end_time - timedelta(days=lookback_days)

        # Convert to milliseconds
        start_ms = int(start_time.timestamp() * 1000)
        end_ms = int(end_time.timestamp() * 1000)

        # Binance API parameters
        params = {
            "symbol": symbol,
            "interval": interval,
            "startTime": start_ms,
            "endTime": end_ms,
            "limit": 1000,  # Maximum allowed by Binance
        }

        all_data = []
        current_start = start_ms

        while current_start < end_ms:
            params["startTime"] = current_start

            try:
                response = self.session.get(f"{self.BASE_URL}/klines", params=params)
                response.raise_for_status()
                data = response.json()

                if not data:
                    break

                all_data.extend(data)

                # Update start time for next batch
                current_start = data[-1][6] + 1  # Close time + 1ms

                # Rate limiting
                time.sleep(self.rate_limit_delay)

            except Exception as e:
                print(f"Error fetching data for {symbol}: {e}")
                break

        if not all_data:
            return pd.DataFrame()

        # Convert to DataFrame
        df = pd.DataFrame(
            all_data,
            columns=[
                "open_time",
                "open",
                "high",
                "low",
                "close",
                "volume",
                "close_time",
                "quote_volume",
                "trades",
                "taker_buy_base",
                "taker_buy_quote",
                "ignore",
            ],
        )

        # Convert data types and create timestamp
        df["timestamp"] = pd.to_datetime(df["open_time"], unit="ms")
        df["open"] = df["open"].astype(float)
        df["high"] = df["high"].astype(float)
        df["low"] = df["low"].astype(float)
        df["close"] = df["close"].astype(float)
        df["volume"] = df["volume"].astype(float)

        # Select and reorder columns
        df = df[["timestamp", "open", "high", "low", "close", "volume"]].copy()
        df.set_index("timestamp", inplace=True)

        return df

    def fetch_multiple_symbols(
        self,
        symbols: List[str],
        interval: str = "1h",
        lookback_days: int = 90,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> Dict[str, pd.DataFrame]:
        """
        Fetch historical data for multiple symbols.

        Args:
            symbols: List of trading pair symbols
            interval: Kline interval
            lookback_days: Number of days to look back
            start_time: Start time for data fetch
            end_time: End time for data fetch

        Returns:
            Dictionary mapping symbol to DataFrame
        """
        data = {}

        for symbol in symbols:
            print(f"Fetching data for {symbol}...")
            df = self.fetch_klines(
                symbol=symbol,
                interval=interval,
                lookback_days=lookback_days,
                start_time=start_time,
                end_time=end_time,
            )

            if not df.empty:
                data[symbol] = df
            else:
                print(f"Warning: No data retrieved for {symbol}")

        return data

    def get_aligned_prices(
        self,
        symbols: List[str],
        price_column: str = "close",
        interval: str = "1h",
        lookback_days: int = 90,
        fill_method: str = "ffill",
    ) -> pd.DataFrame:
        """
        Fetch and align price data for multiple symbols.

        Args:
            symbols: List of trading pair symbols
            price_column: Which price column to use ('open', 'high', 'low', 'close')
            interval: Kline interval
            lookback_days: Number of days to look back
            fill_method: Method to fill missing values ('ffill', 'bfill', 'interpolate')

        Returns:
            DataFrame with aligned prices, symbols as columns
        """
        # Fetch data for all symbols
        data = self.fetch_multiple_symbols(
            symbols=symbols, interval=interval, lookback_days=lookback_days
        )

        if not data:
            return pd.DataFrame()

        # Extract price series and align
        price_series = {}
        for symbol, df in data.items():
            if price_column in df.columns:
                price_series[symbol] = df[price_column]

        if not price_series:
            return pd.DataFrame()

        # Create aligned DataFrame
        aligned_df = pd.DataFrame(price_series)

        # Handle missing values
        if fill_method == "ffill":
            aligned_df = aligned_df.ffill()
        elif fill_method == "bfill":
            aligned_df = aligned_df.bfill()
        elif fill_method == "interpolate":
            aligned_df = aligned_df.interpolate()

        # Drop any remaining NaN rows
        aligned_df = aligned_df.dropna()

        return aligned_df

    def validate_symbols(self, symbols: List[str]) -> Tuple[List[str], List[str]]:
        """
        Validate that symbols exist on Binance.

        Args:
            symbols: List of symbols to validate

        Returns:
            Tuple of (valid_symbols, invalid_symbols)
        """
        try:
            response = self.session.get(f"{self.BASE_URL}/exchangeInfo")
            response.raise_for_status()
            exchange_info = response.json()

            valid_symbols_set = {
                s["symbol"]
                for s in exchange_info["symbols"]
                if s["status"] == "TRADING"
            }

            valid_symbols = [s for s in symbols if s in valid_symbols_set]
            invalid_symbols = [s for s in symbols if s not in valid_symbols_set]

            return valid_symbols, invalid_symbols

        except Exception as e:
            print(f"Error validating symbols: {e}")
            return symbols, []  # Assume all are valid if we can't check
