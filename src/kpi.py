import pandas as pd
from src.processor import transform_to_numeric, preprocess_dates


class KPIEngine:
    """Engine for computing various types of Key Performance Indicators.

    Supports aggregation (sum, mean, max, min), count, groupby operations,
    and mixed KPIs that combine previously computed KPI values.

    Args:
        df (pd.DataFrame): The input dataframe containing the data.
        config (dict): Configuration dictionary defining KPIs to compute.
    """
    def __init__(self, df, config):
        self.df = df
        self.config = config

    def compute_all(self):
        """Compute all KPIs defined in the configuration.

        Non-mixed KPIs are computed first, followed by mixed KPIs that depend
        on previously computed values.

        Returns:
            dict: A dictionary mapping KPI IDs to their computed results,
                  each containing "name" and "value" keys.
        """
        results = {}

        # Compute non-mixed KPIs first (aggregation, count, groupby)
        for kpi in self.config["kpis"]:
            filtered_df = self._apply_filters(self.df, kpi.get("filters"))
            if kpi["type"] != "mixed":
                result = self.compute_kpi(kpi, filtered_df)
                results[kpi["id"]] = {
                    "name": kpi["name"],
                    "value": result
                }
        # Compute mixed KPIs that reference previously computed values
        for kpi in self.config["kpis"]:
            if kpi["type"] == "mixed":
                result = self._compute_mixed(kpi, results)
                results[kpi["id"]] = {
                    "name": kpi["name"],
                    "value": result
                }
        return results
    
    def compute_kpi(self, kpi, df):
        kpi_type = kpi["type"]
        if kpi_type == "aggregation":
            return self._compute_aggregation(kpi, df)

        elif kpi_type == "count":
            return len(self.df)

        elif kpi_type == "groupby":
            return self._compute_groupby(kpi, df)

        else:
            raise ValueError(f"Uknown KPI type: {kpi_type}")
        
    def _compute_aggregation(self, kpi, df):
        column = kpi["column"]
        operation = kpi["operation"]
        _temp_df = transform_to_numeric(df.copy(), column)

        if operation == "sum":
            return _temp_df[column].sum()
        
        if operation == "mean":
            return round(_temp_df[column].mean(), 2)
        
        if operation == "max":
            return _temp_df[column].max()
        
        if operation == "min":
            return _temp_df[column].min()
        
        raise ValueError(f"Unsupported operation: {operation}")
    
    def _compute_groupby(self, kpi, df):
        groupby_col = kpi['groupby']
        column = kpi['column']
        operation = kpi['operation']

        grouped = df.groupby(groupby_col)[column]

        if operation == "sum":
            return grouped.sum()

        if operation == "mean":
            return grouped.mean()

        if operation == "count":
            return grouped.count()

        raise ValueError(f"Unsupported groupby operation: {operation}")

    def _compute_mixed(self, kpi, results):
        """Compute a mixed KPI by combining two existing KPI values.

        Args:
            kpi (dict): KPI config with "ref_kpi_1", "ref_kpi_2", and "operation" keys.
                        Operations: add, subtract, multiply, divide.
            results (dict): Previously computed KPI results to reference.

        Returns:
            The computed mixed value (rounded to 2 decimal places for division),
            or None for division by zero.
        """
        ref_kpi_1 = kpi["ref_kpi_1"]
        ref_kpi_2 = kpi["ref_kpi_2"]
        operation = kpi["operation"]

        if ref_kpi_1 not in results:
            raise ValueError(f"Referenced KPI {ref_kpi_1} not found in results")
        if ref_kpi_2 not in results:
            raise ValueError(f"Referenced KPI {ref_kpi_2} not found in results")

        val1 = results[ref_kpi_1]["value"]
        val2 = results[ref_kpi_2]["value"]

        if operation == "add":
            return val1 + val2
        elif operation == "subtract":
            return val1 - val2
        elif operation == "multiply":
            return val1 * val2
        elif operation == "divide":
            return round(val1 / val2, 2) if val2 != 0 else None
        else:
            raise ValueError(f"Unsupported mixed operation: {operation}")
        
    def _apply_filters(self, df, filters):
        if not filters:
            return df
        
        filtered_df = df.copy()
        
        for f in filters:
            column = f["column"]
            operator = f["operator"]
            value = f["value"]

            filtered_df = self._apply_single_filter(filtered_df, column, operator, value)
        
        return filtered_df

    def _apply_single_filter(self, df, column, operator, value):
        if column in ("data", "date"):
            value = pd.to_datetime(value)

        if isinstance(value, int) or isinstance(value, float) or value.isdigit():
            df = transform_to_numeric(df, column)
            value = int(value)

        if operator == "==":
            return df[df[column] == value]

        elif operator == "!=":
            return df[df[column] != value]

        elif operator == ">":
            return df[df[column] > value]

        elif operator == "<":
            return df[df[column] < value]

        elif operator == ">=":
            return df[df[column] >= value]

        elif operator == "<=":
            return df[df[column] <= value]

        elif operator == "in":
            return df[df[column].isin(value)]

        elif operator == "not in":
            return df[~df[column].isin(value)]

        else:
            raise ValueError(f"Unsupported operator: {operator}")