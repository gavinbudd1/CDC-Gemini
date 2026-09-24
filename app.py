import streamlit as st
import pandas as pd

from utils.data_loader import load_and_validate_data
from utils.components import render_sidebar_filters, render_kpi_cards
from utils.plots import (
    plot_monthly_trend,
    plot_sex_comparison,
    plot_state_ranking,
    plot_choropleth_map,
    plot_state_month_heatmap,
    plot_top_bottom_geographies
)

# Set page layout configuration
st.set_page_config(
    page_title="CDC Provisional Natality Dashboard",
    page_icon="👶",
    layout="wide"
)

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
