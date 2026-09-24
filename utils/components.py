import streamlit as st

def render_sidebar_filters(df):
    """
    Renders filter controls in the sidebar and updates session state cleanly.
    """
    st.sidebar.header("🔍 Data Filters")

    # Reset button trigger
    if st.sidebar.button("🔄 Reset All Filters", use_container_width=True):
        st.session_state["selected_states"] = df["state_of_residence"].unique().tolist()
        st.session_state["selected_months"] = df["month"].cat.categories.tolist()
        st.session_state["selected_sex"] = "All"
        st.rerun()

    all_states = sorted(df["state_of_residence"].unique().tolist())
    all_months = df["month"].cat.categories.tolist()

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
    """
    Renders 5 top-level KPI summary cards with thousands separators.
    """
    total_births = filtered_df["births"].sum()
    num_states = len(selected_states)
    
    # Calculate average births per selected month
    num_months = len(selected_months) if len(selected_months) > 0 else 1
    avg_births_per_month = total_births / num_months if not filtered_df.empty else 0

    # Top Geography calculation
    if not filtered_df.empty:
        top_geo_series = filtered_df.groupby("state_of_residence")["births"].sum()
        top_geo = top_geo_series.idxmax() if not top_geo_series.empty else "N/A"
        top_geo_count = top_geo_series.max() if not top_geo_series.empty else 0
        
        # Top Month calculation
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
