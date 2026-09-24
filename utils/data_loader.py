import os
import pandas as pd
import streamlit as st

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

@st.cache_data
def load_and_validate_data(file_path: str = "Provisional_Natality_2025_CDC1.csv") -> pd.DataFrame:
    """
    Loads natality dataset, enforces categorical month order, maps state abbreviations,
    and performs basic data validation.
    """
    if not os.path.exists(file_path):
        # Fallback check for relative paths depending on working directory
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
