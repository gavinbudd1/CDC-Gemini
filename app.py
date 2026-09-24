import os
import pandas as pd
import streamlit as st
import plotly.express as px

# Set page layout configuration
st.set_page_config(
    page_title="CDC Provisional Natality Dashboard",
    page_icon="👶",
    layout="wide"
)

# Standard state name to 2-letter abbreviation mapping for US choropleth maps
STATE_ABBR_MAP = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
    "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE",
    "District of Columbia": "DC", "Florida": "FL", "Georgia": "GA", "Hawaii": "HI",
    "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA",
    "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME",
    "Maryland": "MD", "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN",
    "Mississippi": "MS", "Missouri": "MO", "Montana": "MT", "Nebraska": "NE",
    "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM",
    "New York": "NY", "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH",
    "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI",
    "South Carolina": "SC", "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX",
    "Utah": "UT", "Vermont": "VT", "Virginia": "VA", "Washington": "WA",
    "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY"
}

MONTH_ORDER = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

COLOR_PRIMARY = "#1f77b4"
COLOR_FEMALE = "#e377c2"
COLOR_MALE = "#1f77b4"


# ==========================================
# DATA LOADING AND VALIDATION
# ==========================================
@st.cache_data
def load_and_validate_data(file_path: str = "Provisional_Natality_2025_CDC1.csv") -> pd.DataFrame:
    """Loads natality dataset, enforces categorical month order, maps state abbreviations,

    and performs basic data validation.
    """
    if not os.path.exists(file_path):
        alt_path = os.path.join("data", os.path.basename(file_path))
        if os.path.exists(alt_path):
            file_path = alt_path
        else:
            raise FileNotFoundError(f"Data file not found at '{file_path}' or '{alt_path}'.")

    df = pd.read_csv(file_path)

    # Required columns validation check
    required_cols = {"state_of_residence", "month", "month_code", "year_code", "sex_of_infant", "births"}
    missing_cols = required_cols - set(df.columns)
    if missing_cols:
        raise ValueError(f"Dataset missing required columns: {missing_cols}")

    # Data type & validation checks
    if df.empty:
        raise ValueError("Dataset is empty.")
    
    if (df["births"] < 0).any():
        raise ValueError("Data validation error: Negative birth counts detected.")

    # Enforce chronological ordering on month
    df["month"] = pd.Categorical(df["month"], categories=MONTH_ORDER, ordered=True)
    
    # Map state codes for geographical visualisations
    df["state_abbr"] = df["state_of_residence"].map(STATE_ABBR_MAP)

    return df


# ==========================================
# SIDEBAR FILTERS & COMPONENT RENDERERS
# ==========================================
def render_sidebar_filters(df):
    """Renders filter controls in the sidebar and updates session state cleanly."""
    st.sidebar.header("🔍 Data Filters")

    all_states = sorted(df["state_of_residence"].unique().tolist())
    all_months = df["month"].cat.categories.tolist()

    # Reset button trigger
    if st.sidebar.button("🔄 Reset All Filters", use_container_width=True):
        st.session_state["selected_states"] = all_states
        st.session_state["selected_months"] = all_months
        st.session_state["selected_sex"] = "All"
        st.rerun()

    # Session state defaults initialization
    if "selected_states" not in st.session_state:
        st.session_state["selected_states"] = all_states
    if "selected_months" not in st.session_state:
        st.session_state["selected_months"] = all_months
    if "selected_sex" not in st.session_state:
        st.session_state["selected_sex"] = "All"

    # State Selection Controls
    st.sidebar.subheader("Geography")
    select_all_states = st.sidebar.checkbox("Select All States", value=len(st.session_state["selected_states"]) == len(all_states))
    if select_all_states:
        selected_states = st.sidebar.multiselect("Select States", options=all_states, default=all_states)
    else:
        selected_states = st.sidebar.multiselect("Select States", options=all_states, default=st.session_state["selected_states"])
    st.session_state["selected_states"] = selected_states

    # Month Selection Controls
    st.sidebar.subheader("Month")
    select_all_months = st.sidebar.checkbox("Select All Months", value=len(st.session_state["selected_months"]) == len(all_months))
    if select_all_months:
        selected_months = st.sidebar.multiselect("Select Months", options=all_months, default=all_months)
    else:
        selected_months = st.sidebar.multiselect("Select Months", options=all_months, default=st.session_state["selected_months"])
    st.session_state["selected_months"] = selected_months

    # Sex Filter Control
    st.sidebar.subheader("Infant Sex")
    selected_sex = st.sidebar.radio("Select Sex", options=["All", "Female", "Male"], index=["All", "Female", "Male"].index(st.session_state["selected_sex"]))
    st.session_state["selected_sex"] = selected_sex

    # Active Filters Summary Box
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Active Filters Summary:**")
    st.sidebar.caption(f"• **States Selected:** {len(selected_states)} of {len(all_states)}")
    st.sidebar.caption(f"• **Months Selected:** {len(selected_months)} of {len(all_months)}")
    st.sidebar.caption(f"• **Infant Sex:** {selected_sex}")

    return selected_states, selected_months, selected_sex


def render_kpi_cards(filtered_df, selected_states, selected_months):
    """Renders 5 top-level KPI summary cards with thousands separators."""
    total_births = filtered_df["births"].sum()
    num_states = len(selected_states)
    
    num_months = len(selected_months) if len(selected_months) > 0 else 1
    avg_births_per_month = total_births / num_months if not filtered_df.empty else 0

    if not filtered_df.empty:
        top_geo_series = filtered_df.groupby("state_of_residence")["births"].sum()
        top_geo = top_geo_series.idxmax() if not top_geo_series.empty else "N/A"
        top_geo_count = top_geo_series.max() if not top_geo_series.empty else 0
        
        top_month_series = filtered_df.groupby("month", observed=False)["births"].sum()
        top_month = top_month_series.idxmax() if not top_month_series.empty else "N/A"
        top_month_count = top_month_series.max() if not top_month_series.empty else 0
    else:
        top_geo, top_geo_count = "N/A", 0
        top_month, top_month_count = "N/A", 0

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Births", f"{total_births:,}")
    col2.metric("Geographies", f"{num_states}")
    col3.metric("Avg Births / Month", f"{int(avg_births_per_month):,}")
    col4.metric("Top Geography", f"{top_geo}", f"{top_geo_count:,} births" if top_geo != "N/A" else None)
    col5.metric("Top Month", f"{top_month}", f"{top_month_count:,} births" if top_month != "N/A" else None)


# ==========================================
# VISUALIZATION FUNCTIONS
# ==========================================
def plot_monthly_trend(df: pd.DataFrame):
    """Monthly birth trend line chart maintaining chronological month order."""
    monthly_data = df.groupby("month", observed=False)["births"].sum().reset_index()
    fig = px.line(
        monthly_data,
        x="month",
        y="births",
        markers=True,
        title="Monthly Birth Trend",
        labels={"month": "Month", "births": "Total Births"},
        color_discrete_sequence=[COLOR_PRIMARY]
    )
    fig.update_yaxes(rangemode="tozero")
    fig.update_traces(hovertemplate="<b>Month</b>: %{x}<br><b>Births</b>: %{y:,}<extra></extra>")
    fig.update_layout(xaxis_title="Month", yaxis_title="Birth Counts")
    return fig


def plot_sex_comparison(df: pd.DataFrame):
    """Side-by-side bar chart comparing female vs male births by month."""
    sex_monthly = df.groupby(["month", "sex_of_infant"], observed=False)["births"].sum().reset_index()
    fig = px.bar(
        sex_monthly,
        x="month",
        y="births",
        color="sex_of_infant",
        barmode="group",
        title="Birth Counts by Month and Infant Sex",
        labels={"month": "Month", "births": "Births", "sex_of_infant": "Infant Sex"},
        color_discrete_map={"Female": COLOR_FEMALE, "Male": COLOR_MALE}
    )
    fig.update_yaxes(rangemode="tozero")
    fig.update_traces(hovertemplate="<b>Month</b>: %{x}<br><b>Sex</b>: %{color}<br><b>Births</b>: %{y:,}<extra></extra>")
    return fig


def plot_state_ranking(df: pd.DataFrame):
    """Horizontal bar chart ranking selected states by total births."""
    state_data = df.groupby("state_of_residence")["births"].sum().reset_index().sort_values("births", ascending=True)
    fig = px.bar(
        state_data,
        x="births",
        y="state_of_residence",
        orientation="h",
        title="Total Births by State/Geography",
        labels={"state_of_residence": "State", "births": "Total Births"},
        color_discrete_sequence=[COLOR_PRIMARY]
    )
    fig.update_xaxes(rangemode="tozero")
    fig.update_traces(hovertemplate="<b>State</b>: %{y}<br><b>Births</b>: %{x:,}<extra></extra>")
    fig.update_layout(height=max(400, len(state_data) * 20))
    return fig


def plot_choropleth_map(df: pd.DataFrame):
    """US state choropleth map showing spatial birth count distribution."""
    state_map_data = df.groupby(["state_abbr", "state_of_residence"])["births"].sum().reset_index()
    fig = px.choropleth(
        state_map_data,
        locations="state_abbr",
        locationmode="USA-states",
        color="births",
        scope="usa",
        hover_name="state_of_residence",
        title="Geographic Distribution of Birth Counts across the US",
        labels={"births": "Total Births"},
        color_continuous_scale="Viridis"
    )
    fig.update_traces(hovertemplate="<b>%{hovertext}</b><br>Total Births: %{z:,}<extra></extra>")
    return fig


def plot_state_month_heatmap(df: pd.DataFrame):
    """Heatmap showing state-by-month birth distribution."""
    pivot_df = df.pivot_table(index="state_of_residence", columns="month", values="births", aggfunc="sum", observed=False).fillna(0)
    fig = px.imshow(
        pivot_df,
        labels=dict(x="Month", y="State", color="Births"),
        x=pivot_df.columns,
        y=pivot_df.index,
        aspect="auto",
        title="State-by-Month Birth Density Heatmap",
        color_continuous_scale="Viridis"
    )
    fig.update_traces(hovertemplate="<b>State</b>: %{y}<br><b>Month</b>: %{x}<br><b>Births</b>: %{z:,}<extra></extra>")
    return fig


def plot_top_bottom_geographies(df: pd.DataFrame, n: int = 5):
    """Top N and Bottom N geography comparisons."""
    state_totals = df.groupby("state_of_residence")["births"].sum().reset_index()
    if len(state_totals) <= n * 2:
        top_bottom = state_totals.sort_values("births", ascending=False)
    else:
        top_n = state_totals.nlargest(n, "births")
        bottom_n = state_totals.nsmallest(n, "births")
        top_bottom = pd.concat([top_n, bottom_n]).sort_values("births", ascending=True)

    fig = px.bar(
        top_bottom,
        x="births",
        y="state_of_residence",
        orientation="h",
        title=f"Top {n} and Bottom {n} Geographies by Birth Count",
        labels={"state_of_residence": "State", "births": "Total Births"},
        color_discrete_sequence=["#2ca02c"]
    )
    fig.update_xaxes(rangemode="tozero")
    fig.update_traces(hovertemplate="<b>State</b>: %{y}<br><b>Births</b>: %{x:,}<extra></extra>")
    return fig


# ==========================================
# MAIN APPLICATION ROUTINE
# ==========================================
def main():
    # Header Section
    st.title("👶 CDC Provisional Natality Analysis Dashboard (2025)")
    st.markdown("""
    Welcome! This dashboard provides an exploratory analysis of provisional U.S. birth statistics. 
    Designed for business analytics students, it demonstrates multi-dimensional geographic, temporal, and demographic data exploration.
    """)

    # Notice callout boxes
    col_notice1, col_notice2 = st.columns(2)
    with col_notice1:
        st.warning("⚠️ **Notice:** These data are **provisional** and subject to revision by the CDC.")
    with col_notice2:
        st.info("📊 **Note:** Figures represent absolute **birth counts**, not crude or adjusted birth rates.")

    st.caption("Source: CDC National Center for Health Statistics (NCHS) Provisional Natality Data.")
    st.markdown("---")

    # Load data with caching
    try:
        df = load_and_validate_data("Provisional_Natality_2025_CDC1.csv")
    except Exception as e:
        st.error(f"Error loading dataset: {e}")
        st.stop()

    # Render sidebar controls
    selected_states, selected_months, selected_sex = render_sidebar_filters(df)

    # Filter dataframe based on selections
    filtered_df = df[
        (df["state_of_residence"].isin(selected_states)) &
        (df["month"].isin(selected_months))
    ]
    if selected_sex != "All":
        filtered_df = filtered_df[filtered_df["sex_of_infant"] == selected_sex]

    # Handle Empty Observations
    if filtered_df.empty:
        st.error("⚠️ No observations match your selected filter criteria. Please adjust your sidebar settings.")
        st.stop()

    # KPI Section
    render_kpi_cards(filtered_df, selected_states, selected_months)
    st.markdown("---")

    # Tabbed View
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Overview",
        "🗺️ Geographic Analysis",
        "📅 Monthly & Sex Analysis",
        "📋 Data Table & Export",
        "ℹ️ About the Data"
    ])

    # Tab 1: Overview
    with tab1:
        st.subheader("High-Level Summary")
        col_map, col_trend = st.columns([1.2, 1])
        with col_map:
            st.plotly_chart(plot_choropleth_map(filtered_df), use_container_width=True)
        with col_trend:
            st.plotly_chart(plot_monthly_trend(filtered_df), use_container_width=True)

    # Tab 2: Geographic Analysis
    with tab2:
        st.subheader("Geographic Differences")
        col_rank, col_topbot = st.columns(2)
        with col_rank:
            st.plotly_chart(plot_state_ranking(filtered_df), use_container_width=True)
        with col_topbot:
            st.plotly_chart(plot_top_bottom_geographies(filtered_df), use_container_width=True)
        
        st.markdown("---")
        st.plotly_chart(plot_state_month_heatmap(filtered_df), use_container_width=True)

    # Tab 3: Monthly and Sex Analysis
    with tab3:
        st.subheader("Temporal & Sex Distribution Analysis")
        col_sex_trend, col_sex_bar = st.columns(2)
        with col_sex_trend:
            st.plotly_chart(plot_monthly_trend(filtered_df), use_container_width=True)
        with col_sex_bar:
            st.plotly_chart(plot_sex_comparison(filtered_df), use_container_width=True)

    # Tab 4: Data Table and Download
    with tab4:
        st.subheader("Filtered Data Inspection & Download")
        st.write(f"Displaying **{len(filtered_df):,}** matching rows:")
        
        display_df = filtered_df[["state_of_residence", "month", "sex_of_infant", "births"]].copy()
        st.dataframe(display_df, use_container_width=True)

        csv_data = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Filtered Data as CSV",
            data=csv_data,
            file_name="filtered_cdc_natality_2025.csv",
            mime="text/csv",
            type="primary"
        )

    # Tab 5: About the Data
    with tab5:
        st.subheader("About the Dataset & Analytical Context")
        st.markdown("""
        ### Background & Context
        This dataset reflects provisional vital statistics counts published by the **CDC National Center for Health Statistics (NCHS)**.

        ### Key Analytical Concepts for Business Students
        1. **Provisional vs. Final Data:**
           - Provisional data are incomplete and subject to ongoing reporting updates. Late registration of vital records can alter counts in final reporting releases.
        2. **Counts vs. Rates:**
           - **Birth Count:** The absolute number of live births recorded in a jurisdiction.
           - **Birth Rate:** The ratio of births to total population (e.g., crude birth rate per 1,000 residents).
           - *Caution:* Higher birth counts in states like California or Texas are primarily driven by larger base populations rather than inherently higher fertility rates.

        ### Column Definitions
        - **`state_of_residence`**: The US state or territory where the mother resides.
        - **`month` / `month_code`**: Calendar month in chronological sequence.
        - **`year_code`**: Reporting year (2025).
        - **`sex_of_infant`**: Biological sex of the infant registered at birth.
        - **`births`**: Aggregated count of registered live births.
        """)


if __name__ == "__main__":
    main()
