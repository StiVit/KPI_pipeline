import streamlit as st
import pandas as pd

from src.kpi_builder import KPIBuilder
from src.kpi import KPIEngine
from src.loader import load_data
from src.processor import clean_data
from src.visualization import visualize_kpis, get_output_path

st.set_page_config(page_title="Dynamic KPI Generator", layout="wide")

st.title("Dynamic KPI Reporting System")

# =====================================================
# SESSION STATE
# =====================================================

if "builder" not in st.session_state:
    st.session_state.builder = KPIBuilder()

if "selected_columns" not in st.session_state:
    st.session_state.selected_columns = []

if "step" not in st.session_state:
    st.session_state.step = 1

if "filters" not in st.session_state:
    st.session_state.filters = []


# =====================================================
# STEP 1 — UPLOAD EXCEL FILE
# =====================================================

st.header("1. Upload Excel File")

uploaded_file = st.file_uploader(
    "Upload Excel File",
    type=["xlsx", "xls"]
)

if uploaded_file and st.session_state.step == 1:
    st.session_state.uploaded_file = uploaded_file
    st.session_state.step = 2
    
if st.session_state.step >= 2:

    st.header("2. Select Sheet and Header")

    # Read all sheets
    excel_file = pd.ExcelFile(st.session_state.uploaded_file)

    sheet_name = st.selectbox(
        "Select Sheet",
        excel_file.sheet_names
    )

    header = st.selectbox(
        "Select header number",
        range(5)
    )

    if st.button("Confirm Sheet Settings"):

        df = load_data(excel_file, sheet_name=sheet_name, header=header)

        st.session_state.df = df
        st.session_state.step = 3

        st.success("Sheet configuration saved")

# =====================================================
# STEP 2 — COLUMN SELECTION
# =====================================================

if st.session_state.step >= 3:

    st.header("3. Select Columns")

    df = st.session_state.df

    all_columns = df.columns.tolist()

    with st.form("columns_form"):

        selected_columns = st.multiselect(
            "Choose columns to keep",
            all_columns,
            default=all_columns
        )

        submitted = st.form_submit_button("Confirm Columns")

        if submitted:

            filtered_df = clean_data(df, selected_columns)

            st.session_state.selected_columns = filtered_df.columns
            st.session_state.filtered_df = filtered_df
            st.session_state.step = 4
            
            st.success("Columns confirmed")

            st.subheader("Filtered Data")
            st.dataframe(filtered_df.head())

# =====================================================
# STEP 3 — KPI CREATION
# =====================================================

if st.session_state.step >= 4:

    st.header("4. Create KPIs")

    filtered_df = st.session_state.filtered_df
    selected_columns = st.session_state.selected_columns

    kpi_type = st.selectbox(
        "KPI type",
        ["aggregation", "count", "groupby", "mixed"]
    )

    kpi_name = st.text_input("KPI Name")

    # =====================================================
    # FILTERS
    # =====================================================

    st.subheader("Filters")

    use_filters = st.checkbox("Use Filter")

    if use_filters:
        filter_column = st.selectbox(
            "Filter Column",
            selected_columns,
            key = "filter_column"
        )

        filter_operator = st.selectbox(
            "Operator",
            ["==", "!=", ">", "<", ">=", "<=", "in", "not in"]
        )

        filter_value = st.text_input("Filter value")

        if st.button("Add Filter"):
            st.session_state.filters.append({
                "column": filter_column,
                "operator": filter_operator,
                "value": filter_value
            })
            st.success("Filter Added")
        
        if st.button("Remove Filters"):
            st.session_state.filters = []
            st.success("Filter Removed")

    
    # =====================================================
    # KPI TYPE FORMS
    # =====================================================

    if kpi_type == "aggregation":
        
        column = st.selectbox(
            "Column",
            selected_columns,
            key="agg_column"
        )

        operation = st.selectbox(
            "Operation",
            ["sum", "mean", "max", "min"]
        )

        if st.button("Create Aggregation KPI"):
            st.session_state.builder.add_aggregation(
                name=kpi_name,
                column=column,
                operation=operation,
                filters=st.session_state.filters
            )

            st.success("Aggregation KPI created")
    
    elif kpi_type == "count":

        if st.button("Create Count KPI"):
            st.session_state.builder.add_count(
                name=kpi_name,
                filters=st.session_state.filters
            )

            st.success("Count KPI created")
    

    elif kpi_type == "groupby":

        groupby_column = st.selectbox(
            "Group By Column",
            selected_columns,
            key="groupby_col"
        )

        value_column = st.selectbox(
            "Value Column",
            selected_columns,
            key="groupby_val"
        )

        operation = st.selectbox(
            "Operation",
            ["sum", "mean", "count"],
            key="groupby_op"
        )

        if st.button("Create GroupBy KPI"):
            st.session_state.builder.add_groupby(
                name=kpi_name,
                groupby=groupby_column,
                column=value_column,
                operation=operation,
                filters=st.session_state.filters
            )

            st.success("GroupBy KPI created")
    

    elif kpi_type == "mixed":

        existing_kpis = st.session_state.builder.kpis

        if len(existing_kpis) < 2:
            st.warning("Create at least 2 KPIs first")

        else:
            kpi_options = {
                k["name"]: k["id"]
                for k in existing_kpis
            }

            kpi_1 = st.selectbox(
                "KPI 1",
                list(kpi_options.keys())
            )

            kpi_2 = st.selectbox(
                "KPI 2",
                list(kpi_options.keys()),
                key="mixed_2"
            )

            mixed_operation = st.selectbox(
                "Operation",
                ["add", "subtract", "multiply", "divide"]
            )

            if st.button("Create Mixed KPI"):
                st.session_state.builder.add_mixed(
                    name=kpi_name,
                    kpi1_id=kpi_options[kpi_1],
                    kpi2_id=kpi_options[kpi_2],
                    operation=mixed_operation
                )

                st.success("Mixed KPI created")

    # =====================================================
    # SHOW CREATED KPIS
    # =====================================================

    st.header("5. Create KPIs")

    st.json(st.session_state.builder.build())

# =====================================================
# COMPUTE KPIS
# =====================================================
if len(st.session_state.builder.kpis) > 0:
    st.header("6. Compute KPIs")

    if st.button("Run KPI Engine"):
        config = st.session_state.builder.build()

        st.dataframe(filtered_df.head())
        engine = KPIEngine(filtered_df, config)

        results = engine.compute_all()
        st.session_state.results = results
        st.session_state.step = 5

        st.success("KPIs Computed")

        for kpi_id, result in results.items():
            kpi_name = result["name"]
            kpi_value = result["value"]

            if isinstance(kpi_value, pd.Series):
                st.subheader(kpi_name)
                st.dataframe(kpi_value)
            else:
                st.metric(
                    label=kpi_name,
                    value=kpi_value
                )

if st.session_state.step >= 5:
    if st.button("Visualize KPIs"):
        chart_paths = visualize_kpis(st.session_state.results)
        st.subheader(f"Visualization saved to: {get_output_path()}")