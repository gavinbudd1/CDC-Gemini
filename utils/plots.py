import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

COLOR_PRIMARY = "#1f77b4"
COLOR_FEMALE = "#e377c2"
COLOR_MALE = "#1f77b4"

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
