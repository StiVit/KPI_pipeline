import os
import matplotlib.pyplot as plt
import pandas as pd

from dotenv import load_dotenv


def get_output_path():
    """Get the output charts path from .env file."""
    load_dotenv()
    return os.getenv("OUTPUT_PATH", "../output/charts")


def ensure_output_folder():
    """Create the output folder if it doesn't exist."""
    path = get_output_path()
    os.makedirs(path, exist_ok=True)
    return path


def visualize_single_kpis(kpi_results, output_path):
    """Create visualization for single-value KPIs (aggregation, mixed, count).

    Creates a horizontal bar chart comparing all single-value KPIs.

    Args:
        kpi_results (dict): Results dict from KPIEngine.compute_all()
        output_path (str): Path to save the chart

    Returns:
        str: Full path to saved chart file
    """
    names = []
    values = []

    for kpi_id, kpi_result in kpi_results.items():
        value = kpi_result["value"]

        # Filter for single values (not groupby/series)
        if not isinstance(value, (pd.Series, dict)) and value is not None:
            names.append(kpi_result["name"])
            values.append(value)

    if not names:
        return None

    fig, ax = plt.subplots(figsize=(10, max(4, len(names) * 0.5)))
    bars = ax.barh(names, values, color='steelblue', edgecolor='navy')

    ax.set_xlabel('Value', fontsize=11)
    ax.set_title('KPI Summary - Single Values', fontsize=14, fontweight='bold')
    ax.grid(axis='x', alpha=0.3, linestyle='--')

    # Add value labels on bars
    for bar, val in zip(bars, values):
        if isinstance(val, (int, float)):
            label_text = f'{val:,.2f}' if val % 1 else f'{val:,.0f}'
            ax.text(bar.get_width() + 0.01 * max(values),
                   bar.get_y() + bar.get_height() / 2,
                   label_text,
                   va='center', fontsize=9)

    plt.tight_layout()
    filepath = os.path.join(output_path, "kpi_single_values.png")
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close()

    return filepath


def visualize_groupby_kpi(kpi_name, kpi_series, output_path):
    """Create visualization for a groupby KPI.

    Creates a bar chart for groupby results.

    Args:
        kpi_name (str): Name of the KPI
        kpi_series (pd.Series): The groupby result
        output_path (str): Path to save the chart

    Returns:
        str: Full path to saved chart file
    """
    if not isinstance(kpi_series, pd.Series) or len(kpi_series) == 0:
        return None

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(kpi_series.index, kpi_series.values, color='#5DADE2', edgecolor='#2E86C1')

    ax.set_xlabel('Category', fontsize=11)
    ax.set_ylabel('Value', fontsize=11)
    ax.set_title(kpi_name, fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3, linestyle='--')

    # Rotate x labels if needed
    if len(str(kpi_series.index[0])) > 10:
        plt.xticks(rotation=45, ha='right')

    # Add value labels on bars
    for bar, val in zip(bars, kpi_series.values):
        if isinstance(val, (int, float)):
            label_text = f'{val:,.2f}' if val % 1 else f'{val:,.0f}'
            ax.text(bar.get_x() + bar.get_width() / 2,
                   bar.get_height() + 0.01 * kpi_series.max(),
                   label_text,
                   ha='center', va='bottom', fontsize=9)

    plt.tight_layout()

    safe_name = kpi_name.replace(' ', '_').replace('/', '_')
    filepath = os.path.join(output_path, f"{safe_name}.png")
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close()

    return filepath


def visualize_kpis(kpi_results):
    """Create visualizations for all KPIs and save to charts folder.

    Args:
        kpi_results (dict): Results dict from KPIEngine.compute_all()

    Returns:
        dict: Mapping of KPI ID to chart file paths (None if no chart created)
    """
    output_path = ensure_output_folder()
    chart_paths = {}

    # Single-value KPIs chart
    single_path = visualize_single_kpis(kpi_results, output_path)
    chart_paths["_summary"] = single_path

    # Groupby KPIs - individual charts
    for kpi_id, kpi_result in kpi_results.items():
        value = kpi_result["value"]
        if isinstance(value, pd.Series):
            path = visualize_groupby_kpi(kpi_result["name"], value, output_path)
            chart_paths[kpi_id] = path

    return chart_paths


def plot_data(df):
    """Legacy function for backward compatibility.

    Args:
        df (pd.DataFrame): Input dataframe (unused, kept for compatibility)
    """
    pass
