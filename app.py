
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from io import BytesIO

st.set_page_config(page_title="Air Board Program Summary Dashboard", layout="wide")
st.title("Air Board Program Summary Dashboard")
st.caption("Interactive dashboard with filters, tables, and charts")

@st.cache_data(show_spinner=False)
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_excel(path, sheet_name="Air Board Program Summary", engine="openpyxl")
    # Normalize column names (strip/consistent spacing)
    df.columns = [c.strip() for c in df.columns]
    # Parse dates
    if "Project Completed" in df.columns:
        df["Project Completed"] = pd.to_datetime(df["Project Completed"], errors="coerce")
    # Coerce numeric
    if "Incentive Amount" in df.columns:
        df["Incentive Amount"] = pd.to_numeric(df["Incentive Amount"], errors="coerce")
    return df

df = load_data("data/Airboard Program Summary Data.xlsx")

# Sidebar filters
st.sidebar.header("Filters")

# Date range
if df["Project Completed"].notna().any():
    min_date = pd.to_datetime(df["Project Completed"].min()).date()
    max_date = pd.to_datetime(df["Project Completed"].max()).date()
    date_range = st.sidebar.date_input(
        "Project Completed Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )
else:
    date_range = None

# Multiselects
def sorted_unique(col):
    vals = df[col].dropna().astype(str).unique().tolist()
    vals.sort()
    return vals

program_sel = st.sidebar.multiselect(
    "Incentive Program", options=sorted_unique("Incentive Program")
)
equip_type_sel = st.sidebar.multiselect(
    "Equipment Type", options=sorted_unique("Equipment Type")
)
old_make_sel = st.sidebar.multiselect(
    "Old Equipment Make", options=sorted_unique("Old Equipment Make")
)
new_make_sel = st.sidebar.multiselect(
    "New Equipment Make", options=sorted_unique("New Equipment Make")
)

# Incentive Amount range
min_amt = float(np.nanmin(df["Incentive Amount"])) if df["Incentive Amount"].notna().any() else 0.0
max_amt = float(np.nanmax(df["Incentive Amount"])) if df["Incentive Amount"].notna().any() else 0.0
amt_range = st.sidebar.slider(
    "Incentive Amount Range",
    min_value=float(np.floor(min_amt)),
    max_value=float(np.ceil(max_amt)),
    value=(float(np.floor(min_amt)), float(np.ceil(max_amt))),
    step=100.0,
)

# Apply filters
filtered = df.copy()
if date_range and isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1]) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
    filtered = filtered[filtered["Project Completed"].between(start, end, inclusive="both")]
if program_sel:
    filtered = filtered[filtered["Incentive Program"].astype(str).isin(program_sel)]
if equip_type_sel:
    filtered = filtered[filtered["Equipment Type"].astype(str).isin(equip_type_sel)]
if old_make_sel:
    filtered = filtered[filtered["Old Equipment Make"].astype(str).isin(old_make_sel)]
if new_make_sel:
    filtered = filtered[filtered["New Equipment Make"].astype(str).isin(new_make_sel)]
if amt_range:
    filtered = filtered[filtered["Incentive Amount"].between(amt_range[0], amt_range[1], inclusive="both")]

# KPI metrics
total_projects = int(len(filtered))
total_incentive = float(filtered["Incentive Amount"].sum()) if not filtered.empty else 0.0
avg_incentive = float(filtered["Incentive Amount"].mean()) if not filtered.empty else 0.0

m1, m2, m3 = st.columns(3)
m1.metric("Projects", f"{total_projects:,}")
m2.metric("Total Incentive", f"${total_incentive:,.0f}")
m3.metric("Avg Incentive", f"${avg_incentive:,.0f}")

st.markdown("---")

# Charts
if not filtered.empty:
    # Incentive by Year
    ydf = filtered.copy()
    ydf["Year"] = ydf["Project Completed"].dt.year
    by_year = ydf.groupby("Year", as_index=False)["Incentive Amount"].sum()
    chart_year = (
        alt.Chart(by_year)
        .mark_bar()
        .encode(
            x=alt.X("Year:O", title="Year"),
            y=alt.Y("Incentive Amount:Q", title="Total Incentive"),
            tooltip=["Year", alt.Tooltip("Incentive Amount:Q", format=",.0f")]
        )
        .properties(title="Total Incentive by Year", height=300)
    )

    # Incentive by Equipment Type
    by_type = filtered.groupby("Equipment Type", as_index=False)["Incentive Amount"].sum().sort_values("Incentive Amount", ascending=False)
    chart_type = (
        alt.Chart(by_type)
        .mark_bar()
        .encode(
            y=alt.Y("Equipment Type:N", sort="-x", title="Equipment Type"),
            x=alt.X("Incentive Amount:Q", title="Total Incentive"),
            tooltip=["Equipment Type", alt.Tooltip("Incentive Amount:Q", format=",.0f")]
        )
        .properties(title="Total Incentive by Equipment Type", height=300)
    )

    # Top New Equipment Makes by count
    top_new = (
        filtered["New Equipment Make"]
        .value_counts()
        .reset_index()
        .rename(columns={"index":"New Equipment Make", "New Equipment Make":"Count"})
        .head(10)
    )
    chart_new = (
        alt.Chart(top_new)
        .mark_bar()
        .encode(
            x=alt.X("Count:Q"),
            y=alt.Y("New Equipment Make:N", sort="-x"),
            tooltip=["New Equipment Make", "Count"]
        )
        .properties(title="Top 10 New Equipment Makes (by Project Count)", height=300)
    )

    # Boxplot of Incentive by Incentive Program
    box_df = filtered.copy()
    chart_box = (
        alt.Chart(box_df)
        .mark_boxplot()
        .encode(
            x=alt.X("Incentive Program:N", title="Incentive Program"),
            y=alt.Y("Incentive Amount:Q", title="Incentive Amount"),
            tooltip=["Incentive Program"]
        )
        .properties(title="Incentive Amount Distribution by Program", height=300)
    )

    c1, c2 = st.columns(2)
    with c1:
        st.altair_chart(chart_year, use_container_width=True)
    with c2:
        st.altair_chart(chart_type, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        st.altair_chart(chart_new, use_container_width=True)
    with c4:
        st.altair_chart(chart_box, use_container_width=True)

st.markdown("---")
st.subheader("Filtered Data")
st.dataframe(filtered, use_container_width=True, hide_index=True)

# Download helpers
def to_excel_bytes(df: pd.DataFrame) -> bytes:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Filtered")
    return output.getvalue()

colA, colB = st.columns(2)
with colA:
    st.download_button(
        "Download CSV",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name="filtered_data.csv",
        mime="text/csv",
    )
with colB:
    st.download_button(
        "Download Excel",
        data=to_excel_bytes(filtered),
        file_name="filtered_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

st.caption("Data source: Air Board Program Summary Data.xlsx")
