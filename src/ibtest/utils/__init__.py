"""
Utilities module for IBTest package.

This module contains utility functions for data processing, plotting, and other helper functions.
"""

# Optional plotting imports
try:
    from .plotting import plot_cointegrated_pairs, plot_time_series, plot_spread
    _plotting_available = True
except ImportError:
    _plotting_available = False

__all__ = []

if _plotting_available:
    __all__.extend(["plot_cointegrated_pairs", "plot_time_series", "plot_spread"])
