import os
from datetime import date

import pandas as pd
import streamlit as st

CSV_FILE = "cpb_cases.csv"

COLUMNS = [
    "date",              # YYYY-MM-DD
    "case_id",           
    "age_years",
    "weight_kg",
    "procedure_type",
    "bypass_time_min",
    "cross_clamp_time_min",
    "lowest_temp_c",
    "min_hematocrit_pct",
    "peak_ACT_sec",
    "highest_lactate_mmolL",
    "mean_arterial_pressure_mmHg",
    "flow_index_Lmin_m2",
]


# -----------------------------
# Data handling
# -----------------------------

def load_data() -> pd.DataFrame:
    """Load CSV into a DataFrame; if it doesn't exist, return empty with correct columns."""
    if not os.path.exists(CSV_FILE):
        return pd.DataFrame(columns=COLUMNS)
    df = pd.read_csv(CSV_FILE)
    # Ensure all columns exist (in case of older file)
    for col in COLUMNS:
        if col not in df.columns:
            df[col] = pd.NA
    return df[COLUMNS]


def save_data(df: pd.DataFrame):
    """Save DataFrame back to CSV."""
    df.to_csv(CSV_FILE, index=False)


def add_case_to_df(df: pd.DataFrame, case_dict: dict) -> pd.DataFrame:
    """Append a new case row to the DataFrame and return it."""
    new_row = pd.DataFrame([case_dict])
    df = pd.concat([df, new_row], ignore_index=True)
    return df


# -----------------------------
# App layout
# -----------------------------

st.set_page_config(
    page_title="CPB Case Tracker & QA Dashboard",
    layout="wide"
)

st.title("CPB Case Tracker & QA Dashboard")
st.caption(
    "Personal educational tool for tracking cardiopulmonary bypass (CPB) cases. "
    "Created by *Bande Hasan Sayed*."
)

# Load data once at start of app run
df = load_data()

# Sidebar navigation
page = st.sidebar.radio(
    "Navigation",
    ["Add new case", "View all cases", "Summary statistics", "Trends"]
)

# -----------------------------
# Page: Add new case
# -----------------------------

if page == "Add new case":
    st.header("Add New CPB Case")

    with st.form("add_case_form"):
        col1, col2, col3 = st.columns(3)

        with col1:
            date_input = st.date_input("Date of case", value=date.today())
            case_id = st.text_input("Case ID", value="Case_01")
            age_years = st.number_input("Patient age (years)", min_value=0, max_value=120, value=60, step=1)
            weight_kg = st.number_input("Weight (kg)", min_value=0.0, max_value=300.0, value=70.0, step=0.1)
            procedure_type = st.text_input("Procedure type", value="CABG")

        with col2:
            bypass_time_min = st.number_input("Bypass time (minutes)", min_value=0.0, value=90.0, step=1.0)
            cross_clamp_time_min = st.number_input("Cross-clamp time (minutes)", min_value=0.0, value=60.0, step=1.0)
            lowest_temp_c = st.number_input("Lowest temperature on bypass (°C)", min_value=15.0, max_value=40.0, value=32.0, step=0.1)
            min_hematocrit_pct = st.number_input("Minimum hematocrit (%)", min_value=10.0, max_value=50.0, value=25.0, step=0.1)

        with col3:
            peak_ACT_sec = st.number_input("Peak ACT (seconds)", min_value=0.0, value=600.0, step=10.0)
            highest_lactate_mmolL = st.number_input("Highest lactate (mmol/L)", min_value=0.0, value=2.0, step=0.1)
            mean_arterial_pressure_mmHg = st.number_input("Typical MAP on bypass (mmHg)", min_value=0.0, value=60.0, step=1.0)
            flow_index_Lmin_m2 = st.number_input("Typical flow index (L/min/m²)", min_value=0.0, value=2.4, step=0.1)

        submitted = st.form_submit_button("Save case")

        if submitted:
            case_dict = {
                "date": date_input.isoformat(),
                "case_id": case_id,
                "age_years": age_years,
                "weight_kg": weight_kg,
                "procedure_type": procedure_type,
                "bypass_time_min": bypass_time_min,
                "cross_clamp_time_min": cross_clamp_time_min,
                "lowest_temp_c": lowest_temp_c,
                "min_hematocrit_pct": min_hematocrit_pct,
                "peak_ACT_sec": peak_ACT_sec,
                "highest_lactate_mmolL": highest_lactate_mmolL,
                "mean_arterial_pressure_mmHg": mean_arterial_pressure_mmHg,
                "flow_index_Lmin_m2": flow_index_Lmin_m2,
            }

            df = add_case_to_df(df, case_dict)
            save_data(df)
            st.success("Case saved successfully.")


# -----------------------------
# Page: View all cases
# -----------------------------

elif page == "View all cases":
    st.header("All Recorded Cases")

    if df.empty:
        st.info("No cases recorded yet.")
    else:
        st.dataframe(df, use_container_width=True)

        # Download button
        csv_data = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name="cpb_cases.csv",
            mime="text/csv"
        )


# -----------------------------
# Page: Summary statistics
# -----------------------------

elif page == "Summary statistics":
    st.header("Summary Statistics")

    if df.empty:
        st.info("No cases recorded yet.")
    else:
        numeric_cols = [
            "bypass_time_min",
            "cross_clamp_time_min",
            "lowest_temp_c",
            "min_hematocrit_pct",
            "highest_lactate_mmolL",
        ]

        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        total_cases = len(df)
        st.subheader(f"Total cases: {total_cases}")

        col1, col2, col3 = st.columns(3)

        def show_stats(label, series, column):
            valid = series.dropna()
            if valid.empty:
                st.write(f"{label}: no data")
            else:
                st.write(
                    f"{label}: mean={valid.mean():.1f}, "
                    f"min={valid.min():.1f}, max={valid.max():.1f}"
                )

        with col1:
            show_stats("Bypass time (min)", df["bypass_time_min"], "bypass_time_min")
            show_stats("Cross-clamp time (min)", df["cross_clamp_time_min"], "cross_clamp_time_min")

        with col2:
            show_stats("Lowest temperature (°C)", df["lowest_temp_c"], "lowest_temp_c")
            show_stats("Min hematocrit (%)", df["min_hematocrit_pct"], "min_hematocrit_pct")

        with col3:
            show_stats("Highest lactate (mmol/L)", df["highest_lactate_mmolL"], "highest_lactate_mmolL")

        # Simple QA flags
        st.subheader("Simple QA Flags (educational only)")

        long_bypass_count = df[df["bypass_time_min"] > 120].shape[0]
        low_temp_count = df[df["lowest_temp_c"] < 28].shape[0]
        high_lactate_count = df[df["highest_lactate_mmolL"] > 4].shape[0]

        st.write(f"Cases with bypass time > 120 min: **{long_bypass_count}**")
        st.write(f"Cases with lowest temp < 28°C: **{low_temp_count}**")
        st.write(f"Cases with highest lactate > 4 mmol/L: **{high_lactate_count}**")


# -----------------------------
# Page: Trends
# -----------------------------

elif page == "Trends":
    st.header("Trends Over Cases")

    if df.empty:
        st.info("No cases recorded yet.")
    else:
        df_plot = df.copy()
        df_plot["date"] = pd.to_datetime(df_plot["date"], errors="coerce")
        df_plot = df_plot.dropna(subset=["date"])
        df_plot = df_plot.sort_values("date")

        if df_plot.empty:
            st.info("No valid dates available to plot.")
        else:
            for col in ["bypass_time_min", "lowest_temp_c", "highest_lactate_mmolL"]:
                df_plot[col] = pd.to_numeric(df_plot[col], errors="coerce")

            st.write("All plots use **date** on the x-axis.")

            # Bypass time
            if df_plot["bypass_time_min"].notna().any():
                st.subheader("Bypass time (min)")
                st.line_chart(df_plot.set_index("date")["bypass_time_min"])
            else:
                st.write("No bypass time data to plot.")

            # Lowest temperature
            if df_plot["lowest_temp_c"].notna().any():
                st.subheader("Lowest temperature (°C)")
                st.line_chart(df_plot.set_index("date")["lowest_temp_c"])
            else:
                st.write("No temperature data to plot.")

            # Highest lactate
            if df_plot["highest_lactate_mmolL"].notna().any():
                st.subheader("Highest lactate (mmol/L)")
                st.line_chart(df_plot.set_index("date")["highest_lactate_mmolL"])
            else:
                st.write("No lactate data to plot.")


