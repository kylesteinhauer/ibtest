"""
IBTest - Interactive Brokers Testing Package

A Python package for testing and interacting with Interactive Brokers API.
Includes cointegration analysis tools for market data.
"""

__version__ = "0.1.0"
__author__ = "Kyle Steinhauer"
__email__ = "your.email@example.com"

# Import main functionality
from .main import hello_world
from .analysis.cointegration import CointegrationAnalyzer
from .data.binance import BinanceDataSource

# Optional plotting imports
try:
    from .utils.plotting import plot_cointegrated_pairs
    _plotting_available = True
except ImportError:
    _plotting_available = False

__all__ = [
    "hello_world",
    "CointegrationAnalyzer", 
    "BinanceDataSource",
]

if _plotting_available:
    __all__.append("plot_cointegrated_pairs")
