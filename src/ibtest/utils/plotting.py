"""
Plotting utilities for cointegration analysis and time series visualization.

This module provides functions to visualize time series data, cointegration results,
and spread analysis for pairs trading.
"""

from typing import List, Optional, Tuple, Dict, Any
import pandas as pd
import numpy as np
import warnings

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.figure import Figure
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    # Create a dummy Figure class for type hints when matplotlib is not available
    class Figure:
        pass

# Import our analysis classes
from ..analysis.cointegration import CointegrationResult


def check_matplotlib() -> None:
    """Check if matplotlib is available and raise error if not."""
    if not MATPLOTLIB_AVAILABLE:
        raise ImportError(
            "matplotlib is required for plotting. "
            "Install with: pip install matplotlib"
        )


def plot_time_series(
    data: pd.DataFrame,
    symbols: Optional[List[str]] = None,
    title: str = "Time Series Data",
    figsize: Tuple[int, int] = (12, 8),
    normalize: bool = False,
    save_path: Optional[str] = None
) -> Figure:
    """
    Plot multiple time series on the same chart.
    
    Args:
        data: DataFrame with time series data
        symbols: List of symbols to plot (if None, plots all columns)
        title: Chart title
        figsize: Figure size (width, height)
        normalize: Whether to normalize series to start at 100
        save_path: Path to save the plot (optional)
    
    Returns:
        matplotlib Figure object
    """
    check_matplotlib()
    
    if symbols is None:
        symbols = data.columns.tolist()
    
    # Filter data to selected symbols
    plot_data = data[symbols].copy()
    
    # Normalize if requested
    if normalize:
        plot_data = plot_data.div(plot_data.iloc[0]) * 100
    
    # Create plot
    fig, ax = plt.subplots(figsize=figsize)
    
    for symbol in symbols:
        if symbol in plot_data.columns:
            ax.plot(plot_data.index, plot_data[symbol], label=symbol, linewidth=1.5)
    
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Price' + (' (Normalized to 100)' if normalize else ''), fontsize=12)
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.grid(True, alpha=0.3)
    
    # Format x-axis dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig


def plot_spread(
    result: CointegrationResult,
    figsize: Tuple[int, int] = (12, 6),
    show_bands: bool = True,
    n_std: float = 2.0,
    save_path: Optional[str] = None
) -> Figure:
    """
    Plot the spread of a cointegrated pair with statistical bands.
    
    Args:
        result: CointegrationResult object
        figsize: Figure size (width, height)
        show_bands: Whether to show standard deviation bands
        n_std: Number of standard deviations for bands
        save_path: Path to save the plot (optional)
    
    Returns:
        matplotlib Figure object
    """
    check_matplotlib()
    
    if result.spread_series is None:
        raise ValueError("No spread data available in the result")
    
    spread = result.spread_series.dropna()
    
    # Create plot
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot spread
    ax.plot(spread.index, spread.values, color='blue', linewidth=1.5, label='Spread')
    
    # Add mean line
    mean_spread = spread.mean()
    ax.axhline(y=mean_spread, color='red', linestyle='--', alpha=0.7, label='Mean')
    
    # Add standard deviation bands
    if show_bands:
        std_spread = spread.std()
        upper_band = mean_spread + n_std * std_spread
        lower_band = mean_spread - n_std * std_spread
        
        ax.axhline(y=upper_band, color='orange', linestyle=':', alpha=0.7, 
                  label=f'+{n_std}σ')
        ax.axhline(y=lower_band, color='orange', linestyle=':', alpha=0.7, 
                  label=f'-{n_std}σ')
        
        # Fill between bands
        ax.fill_between(spread.index, lower_band, upper_band, 
                       alpha=0.1, color='orange')
    
    # Formatting
    pair_name = f"{result.symbol1} - {result.symbol2}"
    ax.set_title(f'Spread Analysis: {pair_name}\n'
                f'P-value: {result.p_value:.4f}, Hedge Ratio: {result.hedge_ratio:.4f}',
                fontsize=14, fontweight='bold')
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Spread', fontsize=12)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Format x-axis dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig


def plot_cointegrated_pairs(
    results: List[CointegrationResult],
    price_data: pd.DataFrame,
    max_pairs: int = 4,
    figsize: Tuple[int, int] = (15, 10),
    save_path: Optional[str] = None
) -> Figure:
    """
    Plot multiple cointegrated pairs in a grid layout.
    
    Args:
        results: List of CointegrationResult objects
        price_data: Original price data DataFrame
        max_pairs: Maximum number of pairs to plot
        figsize: Figure size (width, height)
        save_path: Path to save the plot (optional)
    
    Returns:
        matplotlib Figure object
    """
    check_matplotlib()
    
    # Filter to cointegrated pairs only
    cointegrated = [r for r in results if r.is_cointegrated]
    
    if not cointegrated:
        raise ValueError("No cointegrated pairs found to plot")
    
    # Limit number of pairs
    pairs_to_plot = cointegrated[:max_pairs]
    n_pairs = len(pairs_to_plot)
    
    # Calculate grid dimensions
    n_cols = min(2, n_pairs)
    n_rows = (n_pairs + n_cols - 1) // n_cols
    
    # Create subplots
    fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize)
    if n_pairs == 1:
        axes = [axes]
    elif n_rows == 1:
        axes = axes.flatten()
    else:
        axes = axes.flatten()
    
    for i, result in enumerate(pairs_to_plot):
        ax = axes[i]
        
        # Get price data for the pair
        symbol1, symbol2 = result.symbol1, result.symbol2
        
        if symbol1 in price_data.columns and symbol2 in price_data.columns:
            # Normalize prices to start at 100 for comparison
            pair_data = price_data[[symbol1, symbol2]].dropna()
            normalized_data = pair_data.div(pair_data.iloc[0]) * 100
            
            # Plot normalized prices
            ax.plot(normalized_data.index, normalized_data[symbol1], 
                   label=symbol1, linewidth=1.5)
            ax.plot(normalized_data.index, normalized_data[symbol2], 
                   label=symbol2, linewidth=1.5)
            
            # Formatting
            ax.set_title(f'{symbol1} vs {symbol2}\n'
                        f'P-value: {result.p_value:.4f}',
                        fontsize=11, fontweight='bold')
            ax.set_ylabel('Normalized Price', fontsize=10)
            ax.legend(fontsize=9)
            ax.grid(True, alpha=0.3)
            
            # Format dates
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, fontsize=8)
    
    # Hide unused subplots
    for i in range(n_pairs, len(axes)):
        axes[i].set_visible(False)
    
    plt.suptitle('Cointegrated Pairs Analysis', fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig


def plot_correlation_heatmap(
    data: pd.DataFrame,
    figsize: Tuple[int, int] = (10, 8),
    save_path: Optional[str] = None
) -> Figure:
    """
    Plot correlation heatmap of price data.
    
    Args:
        data: DataFrame with price data
        figsize: Figure size (width, height)
        save_path: Path to save the plot (optional)
    
    Returns:
        matplotlib Figure object
    """
    check_matplotlib()
    
    # Calculate correlation matrix
    corr_matrix = data.corr()
    
    # Create plot
    fig, ax = plt.subplots(figsize=figsize)
    
    # Create heatmap
    im = ax.imshow(corr_matrix, cmap='RdYlBu_r', aspect='auto', vmin=-1, vmax=1)
    
    # Set ticks and labels
    ax.set_xticks(range(len(corr_matrix.columns)))
    ax.set_yticks(range(len(corr_matrix.columns)))
    ax.set_xticklabels(corr_matrix.columns, rotation=45, ha='right')
    ax.set_yticklabels(corr_matrix.columns)
    
    # Add correlation values as text
    for i in range(len(corr_matrix.columns)):
        for j in range(len(corr_matrix.columns)):
            text = ax.text(j, i, f'{corr_matrix.iloc[i, j]:.2f}',
                          ha="center", va="center", color="black", fontsize=8)
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Correlation', rotation=270, labelpad=15)
    
    ax.set_title('Price Correlation Matrix', fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig


def plot_summary_statistics(
    results: List[CointegrationResult],
    figsize: Tuple[int, int] = (12, 8),
    save_path: Optional[str] = None
) -> Figure:
    """
    Plot summary statistics of cointegration analysis.
    
    Args:
        results: List of CointegrationResult objects
        figsize: Figure size (width, height)
        save_path: Path to save the plot (optional)
    
    Returns:
        matplotlib Figure object
    """
    check_matplotlib()
    
    if not results:
        raise ValueError("No results to plot")
    
    # Extract data
    p_values = [r.p_value for r in results]
    hedge_ratios = [r.hedge_ratio for r in results]
    cointegrated = [r.is_cointegrated for r in results]
    
    # Create subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=figsize)
    
    # P-value distribution
    ax1.hist(p_values, bins=20, alpha=0.7, color='skyblue', edgecolor='black')
    ax1.axvline(x=0.05, color='red', linestyle='--', label='α = 0.05')
    ax1.set_xlabel('P-value')
    ax1.set_ylabel('Frequency')
    ax1.set_title('P-value Distribution')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Hedge ratio distribution
    ax2.hist(hedge_ratios, bins=20, alpha=0.7, color='lightgreen', edgecolor='black')
    ax2.set_xlabel('Hedge Ratio')
    ax2.set_ylabel('Frequency')
    ax2.set_title('Hedge Ratio Distribution')
    ax2.grid(True, alpha=0.3)
    
    # Cointegration status pie chart
    coint_counts = pd.Series(cointegrated).value_counts()
    labels = ['Not Cointegrated', 'Cointegrated']
    colors = ['lightcoral', 'lightgreen']
    ax3.pie(coint_counts.values, labels=labels, colors=colors, autopct='%1.1f%%')
    ax3.set_title('Cointegration Status')
    
    # P-value vs Hedge ratio scatter
    colors = ['red' if c else 'blue' for c in cointegrated]
    ax4.scatter(hedge_ratios, p_values, c=colors, alpha=0.6)
    ax4.axhline(y=0.05, color='red', linestyle='--', alpha=0.7)
    ax4.set_xlabel('Hedge Ratio')
    ax4.set_ylabel('P-value')
    ax4.set_title('P-value vs Hedge Ratio')
    ax4.grid(True, alpha=0.3)
    
    # Add legend for scatter plot
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor='red', 
               markersize=8, label='Cointegrated'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', 
               markersize=8, label='Not Cointegrated')
    ]
    ax4.legend(handles=legend_elements)
    
    plt.suptitle('Cointegration Analysis Summary', fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig


def save_all_plots(
    results: List[CointegrationResult],
    price_data: pd.DataFrame,
    output_dir: str = "plots",
    file_format: str = "png"
) -> None:
    """
    Save all available plots to files.
    
    Args:
        results: List of CointegrationResult objects
        price_data: Original price data DataFrame
        output_dir: Directory to save plots
        file_format: File format for plots ('png', 'pdf', 'svg')
    """
    import os
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Plot time series
    fig1 = plot_time_series(price_data, title="All Time Series")
    fig1.savefig(f"{output_dir}/time_series.{file_format}", dpi=300, bbox_inches='tight')
    plt.close(fig1)
    
    # Plot correlation heatmap
    fig2 = plot_correlation_heatmap(price_data)
    fig2.savefig(f"{output_dir}/correlation_heatmap.{file_format}", dpi=300, bbox_inches='tight')
    plt.close(fig2)
    
    # Plot summary statistics
    fig3 = plot_summary_statistics(results)
    fig3.savefig(f"{output_dir}/summary_statistics.{file_format}", dpi=300, bbox_inches='tight')
    plt.close(fig3)
    
    # Plot cointegrated pairs
    cointegrated = [r for r in results if r.is_cointegrated]
    if cointegrated:
        fig4 = plot_cointegrated_pairs(results, price_data)
        fig4.savefig(f"{output_dir}/cointegrated_pairs.{file_format}", dpi=300, bbox_inches='tight')
        plt.close(fig4)
        
        # Plot individual spreads for top pairs
        for i, result in enumerate(cointegrated[:5]):  # Top 5 pairs
            fig = plot_spread(result)
            pair_name = f"{result.symbol1}_{result.symbol2}"
            fig.savefig(f"{output_dir}/spread_{pair_name}.{file_format}", 
                       dpi=300, bbox_inches='tight')
            plt.close(fig)
    
    print(f"All plots saved to {output_dir}/ directory")
