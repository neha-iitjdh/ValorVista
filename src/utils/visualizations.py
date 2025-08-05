"""
Visualization Module for ValorVista.
Creates charts and plots for analysis and reports.
"""

import io
import base64
from typing import List, Dict, Any, Optional, Tuple

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server
import matplotlib.pyplot as plt
import seaborn as sns


def setup_plot_style():
    """Setup consistent plot styling."""
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.rcParams['figure.facecolor'] = 'white'
    plt.rcParams['axes.facecolor'] = 'white'
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.size'] = 10


def create_feature_importance_chart(
    feature_importance: List[Dict[str, Any]],
    top_n: int = 10,
    figsize: Tuple[int, int] = (10, 6),
    return_base64: bool = True
) -> str:
    """
    Create horizontal bar chart of feature importance.

    Args:
        feature_importance: List of dicts with 'feature' and 'importance' keys.
        top_n: Number of top features to display.
        figsize: Figure size tuple.
        return_base64: Whether to return base64 encoded image.

    Returns:
        Base64 encoded PNG image string or file path.
    """
    setup_plot_style()

    # Prepare data
    data = feature_importance[:top_n]
    features = [d['feature'] for d in data][::-1]
    importance = [d['importance'] for d in data][::-1]

    # Create figure
    fig, ax = plt.subplots(figsize=figsize)

    # Color gradient
    colors = plt.cm.Blues(np.linspace(0.4, 0.8, len(features)))

    # Create bars
    bars = ax.barh(features, importance, color=colors, edgecolor='none')

    # Customize
    ax.set_xlabel('Importance', fontsize=12, fontweight='bold')
    ax.set_title('Top Feature Importance', fontsize=14, fontweight='bold', pad=20)

    # Add value labels
    for bar, imp in zip(bars, importance):
        ax.text(bar.get_width() + 0.002, bar.get_y() + bar.get_height()/2,
                f'{imp:.3f}', va='center', fontsize=9)

    # Clean up
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.tick_params(left=False)

    plt.tight_layout()

    if return_base64:
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close(fig)
        return f"data:image/png;base64,{image_base64}"

    plt.close(fig)
    return ""


def create_price_distribution(
    predicted_price: float,
    lower_bound: float,
    upper_bound: float,
    figsize: Tuple[int, int] = (10, 4),
    return_base64: bool = True
) -> str:
    """
    Create price prediction visualization with confidence interval.

    Args:
        predicted_price: Point estimate of price.
        lower_bound: Lower confidence bound.
        upper_bound: Upper confidence bound.
        figsize: Figure size tuple.
        return_base64: Whether to return base64 encoded image.

    Returns:
        Base64 encoded PNG image string.
    """
    setup_plot_style()

    fig, ax = plt.subplots(figsize=figsize)

    # Create a simple visualization
    margin = (upper_bound - lower_bound) * 0.2
    x_min = lower_bound - margin
    x_max = upper_bound + margin

    # Draw confidence interval bar
    ax.barh(0, upper_bound - lower_bound, left=lower_bound,
            height=0.3, color='#E3F2FD', edgecolor='#1976D2', linewidth=2)

    # Draw point estimate marker
    ax.scatter([predicted_price], [0], s=200, color='#1976D2',
              zorder=5, marker='D')

    # Add labels
    ax.text(lower_bound, -0.25, f'${lower_bound:,.0f}',
            ha='center', fontsize=10, color='#666')
    ax.text(predicted_price, 0.25, f'${predicted_price:,.0f}',
            ha='center', fontsize=12, fontweight='bold', color='#1976D2')
    ax.text(upper_bound, -0.25, f'${upper_bound:,.0f}',
            ha='center', fontsize=10, color='#666')

    # Customize
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(-0.5, 0.5)
    ax.set_title('Predicted Value with 95% Confidence Interval',
                fontsize=12, fontweight='bold', pad=10)

    # Remove axes
    ax.axis('off')

    plt.tight_layout()

    if return_base64:
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close(fig)
        return f"data:image/png;base64,{image_base64}"

    plt.close(fig)
    return ""


def create_neighborhood_heatmap(
    neighborhood_prices: Dict[str, float],
    figsize: Tuple[int, int] = (12, 8),
    return_base64: bool = True
) -> str:
    """
    Create heatmap of neighborhood average prices.

    Args:
        neighborhood_prices: Dictionary mapping neighborhoods to avg prices.
        figsize: Figure size tuple.
        return_base64: Whether to return base64 encoded image.

    Returns:
        Base64 encoded PNG image string.
    """
    setup_plot_style()

    # Sort by price
    sorted_hoods = sorted(neighborhood_prices.items(), key=lambda x: x[1], reverse=True)
    names = [x[0] for x in sorted_hoods]
    prices = [x[1] for x in sorted_hoods]

    fig, ax = plt.subplots(figsize=figsize)

    # Create color scale
    norm = plt.Normalize(min(prices), max(prices))
    colors = plt.cm.RdYlGn(norm(prices))

    bars = ax.barh(names[::-1], prices[::-1], color=colors[::-1])

    # Add labels
    for bar, price in zip(bars, prices[::-1]):
        ax.text(bar.get_width() + 1000, bar.get_y() + bar.get_height()/2,
                f'${price:,.0f}', va='center', fontsize=9)

    ax.set_xlabel('Average Price', fontsize=12, fontweight='bold')
    ax.set_title('Average Home Prices by Neighborhood', fontsize=14, fontweight='bold', pad=20)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()

    if return_base64:
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close(fig)
        return f"data:image/png;base64,{image_base64}"

    plt.close(fig)
    return ""


def create_property_comparison(
    target_property: Dict[str, Any],
    comparable_properties: List[Dict[str, Any]],
    figsize: Tuple[int, int] = (12, 6),
    return_base64: bool = True
) -> str:
    """
    Create comparison chart between target and comparable properties.

    Args:
        target_property: Target property data.
        comparable_properties: List of comparable property data.
        figsize: Figure size tuple.
        return_base64: Whether to return base64 encoded image.

    Returns:
        Base64 encoded PNG image string.
    """
    setup_plot_style()

    # Features to compare
    features = ['GrLivArea', 'OverallQual', 'YearBuilt', 'TotalBsmtSF', 'GarageCars']
    feature_labels = ['Living Area\n(sq ft)', 'Quality\n(1-10)', 'Year Built',
                     'Basement\n(sq ft)', 'Garage\n(cars)']

    fig, axes = plt.subplots(1, len(features), figsize=figsize)

    for i, (feat, label) in enumerate(zip(features, feature_labels)):
        ax = axes[i]

        # Get values
        target_val = target_property.get(feat, 0)
        comp_vals = [p.get(feat, 0) for p in comparable_properties]

        # Plot comparables as box plot
        if comp_vals:
            bp = ax.boxplot([comp_vals], positions=[0], widths=0.6)
            for element in ['boxes', 'whiskers', 'fliers', 'caps', 'medians']:
                plt.setp(bp[element], color='#90CAF9')
            plt.setp(bp['boxes'], facecolor='#E3F2FD')
            plt.setp(bp['medians'], color='#1976D2')

        # Plot target
        ax.scatter([0], [target_val], s=100, color='#D32F2F', zorder=5,
                  marker='*', label='Your Property' if i == 0 else '')

        ax.set_title(label, fontsize=10, fontweight='bold')
        ax.set_xticks([])

    axes[0].legend(loc='upper left', fontsize=8)

    fig.suptitle('Property Comparison Analysis', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()

    if return_base64:
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close(fig)
        return f"data:image/png;base64,{image_base64}"

    plt.close(fig)
    return ""


def create_trend_forecast(
    historical_prices: List[Tuple[int, float]],
    forecast_years: int = 3,
    figsize: Tuple[int, int] = (10, 5),
    return_base64: bool = True
) -> str:
    """
    Create trend and forecast visualization.

    Args:
        historical_prices: List of (year, price) tuples.
        forecast_years: Number of years to forecast.
        figsize: Figure size tuple.
        return_base64: Whether to return base64 encoded image.

    Returns:
        Base64 encoded PNG image string.
    """
    setup_plot_style()

    years = [x[0] for x in historical_prices]
    prices = [x[1] for x in historical_prices]

    # Simple linear forecast
    if len(years) >= 2:
        slope = (prices[-1] - prices[0]) / (years[-1] - years[0])
        forecast_years_list = list(range(years[-1] + 1, years[-1] + forecast_years + 1))
        forecast_prices = [prices[-1] + slope * (y - years[-1]) for y in forecast_years_list]
    else:
        forecast_years_list = []
        forecast_prices = []

    fig, ax = plt.subplots(figsize=figsize)

    # Historical line
    ax.plot(years, prices, 'o-', color='#1976D2', linewidth=2,
            markersize=8, label='Historical')

    # Forecast line
    if forecast_years_list:
        ax.plot([years[-1]] + forecast_years_list, [prices[-1]] + forecast_prices,
                'o--', color='#F57C00', linewidth=2, markersize=8, label='Forecast')

        # Confidence band
        upper = [p * 1.1 for p in forecast_prices]
        lower = [p * 0.9 for p in forecast_prices]
        ax.fill_between(forecast_years_list, lower, upper,
                       alpha=0.2, color='#F57C00')

    ax.set_xlabel('Year', fontsize=12, fontweight='bold')
    ax.set_ylabel('Price ($)', fontsize=12, fontweight='bold')
    ax.set_title('Price Trend & Forecast', fontsize=14, fontweight='bold', pad=20)
    ax.legend(loc='upper left')

    # Format y-axis as currency
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K'))

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()

    if return_base64:
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close(fig)
        return f"data:image/png;base64,{image_base64}"

    plt.close(fig)
    return ""
