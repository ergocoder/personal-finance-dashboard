import streamlit as st
import pandas as pd
import plotly.express as px

# PAGE CONFIG
st.set_page_config(
    page_title="Finance Dashboard",
    page_icon="💰",
    layout="wide"
)

# TITLE
st.title("💰 Personal Finance Insights Dashboard")
st.markdown("Analyze spending trends and financial insights")

# LOAD DATA
uploaded_file = st.sidebar.file_uploader(
    "Upload CSV or Excel File",
    type=["csv", "xlsx"]
)

if uploaded_file is not None:

    st.sidebar.success("File uploaded successfully!")

    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)

    else:
        df = pd.read_excel(uploaded_file)

else:

    st.sidebar.info("Using default finance dataset")

    df = pd.read_excel("expenses.xlsx")

# CLEAN DATA

df["Category"] = df["Category"].str.strip()
df["Category"] = df["Category"].str.title()

df["Sub category"] = df["Sub category"].astype(str).str.strip()

df["Debit/Credit"] = pd.to_numeric(
    df["Debit/Credit"],
    errors="coerce"
)

df = df.dropna(subset=["Debit/Credit"])

# Convert date column to datetime
df["Date / Time"] = pd.to_datetime(df["Date / Time"])

# Create separate date columns
df["Date"] = pd.to_datetime(df["Date / Time"]).dt.date
df["Month"] = df["Date / Time"].dt.strftime("%B")
df["YearMonth"] = df["Date / Time"].dt.strftime("%Y-%m")
# Clean category names
df["Category"] = df["Category"].str.title()

# SIDEBAR
st.sidebar.header("Filters")
st.sidebar.markdown("## 💰 Finance Analytics App")

selected_category = st.sidebar.multiselect(
    "Select Category",
    options=df["Category"].unique(),
    default=df["Category"].unique()
)

if len(selected_category) == 0:
    st.warning("Please select at least one category.")
    st.stop()

# Date filters
start_date = st.sidebar.date_input(
    "Start Date",
    df["Date"].min()
)

end_date = st.sidebar.date_input(
    "End Date",
    df["Date"].max()
)

# Apply filters
filtered_df = df[
    (df["Category"].isin(selected_category)) &
    (df["Income/Expense"] == "Expense") &
    (df["Date"] >= start_date) &
    (df["Date"] <= end_date)
]

# METRICS
total_spending = filtered_df["Debit/Credit"].sum()
avg_spending = filtered_df["Debit/Credit"].mean()
if filtered_df.empty:

    max_category = "No data"

else:

    max_category = (
        filtered_df.groupby("Category")["Debit/Credit"]
        .sum()
        .idxmax()
    )

col1, col2, col3 = st.columns(3)

col1.metric("Total Spending", f"₹{total_spending:,.0f}")
col2.metric("Average Transaction", f"₹{avg_spending:,.2f}")
col3.metric("Highest Spending Category", max_category)

st.divider()

# DATASET VIEW
st.subheader("📄 Expense Dataset")
st.dataframe(filtered_df, use_container_width=True)

# CATEGORY DATA
category_data = (
    filtered_df.groupby("Category")["Debit/Credit"]
    .sum()
    .reset_index()
)

# CHARTS
col4, col5 = st.columns(2)

with col4:
    pie_fig = px.pie(
        category_data,
        values="Debit/Credit",
        names="Category",
        title="Category-wise Spending",
        hole=0.4
    )

    st.plotly_chart(pie_fig, use_container_width=True)

with col5:
    bar_fig = px.bar(
        category_data,
        x="Category",
        y="Debit/Credit",
        title="Spending by Category",
        text_auto=True
    )

    st.plotly_chart(bar_fig, use_container_width=True)

# LINE CHART
st.subheader("📈 Spending Trend")

trend_data = (
    filtered_df.groupby("Date / Time")["Debit/Credit"]
    .sum()
    .reset_index()
)

line_fig = px.line(
    trend_data,
    x="Date / Time",
    y="Debit/Credit",
    markers=True
)

st.plotly_chart(
    line_fig,
    use_container_width=True,
    key="monthly_trend_chart"
)

# Monthly Spending Trend
st.markdown("## 📈 Monthly Spending Trend")

monthly_spending = (
    filtered_df.groupby("YearMonth")["Debit/Credit"]
    .sum()
    .reset_index()
)

monthly_spending = monthly_spending.sort_values("YearMonth")

fig3 = px.line(
    monthly_spending,
    x="YearMonth",
    y="Debit/Credit",
    markers=True,
    title="Monthly Expense Trend"
)

st.plotly_chart(
    fig3,
    use_container_width=True,
    key="expense_line_chart"
)

# SMART INSIGHTS
st.markdown("## 🧠 Smart Insights")

if filtered_df.empty:

    st.warning("No data available for selected filters.")

else:

    top_category = (
        filtered_df.groupby("Category")["Debit/Credit"]
        .sum()
        .idxmax()
    )

    top_amount = (
        filtered_df.groupby("Category")["Debit/Credit"]
        .sum()
        .max()
    )

    st.info(
        f"Highest spending category is '{top_category}' with total spending of ₹{top_amount:.2f}"
    )