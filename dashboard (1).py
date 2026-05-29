import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Sales & Revenue Dashboard",
    page_icon="📊",
    layout="wide"
)

# Title
st.title("📊 Sales & Revenue Analysis Dashboard")
st.markdown("---")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("sales_data.csv")
    df["Order_Date"] = pd.to_datetime(df["Order_Date"])
    df["Revenue"] = df["Sales"] * (1 - df["Discount"] / 100)
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("❌ sales_data.csv file not found! Please make sure the file is in the same folder as this script.")
    st.stop()

# Sidebar filters
st.sidebar.header("🔍 Filter Data")

# Category filter
all_categories = ["All"] + list(df["Category"].unique())
selected_categories = st.sidebar.multiselect(
    "Select Categories",
    options=df["Category"].unique(),
    default=df["Category"].unique()
)

# Date range filter
min_date = df["Order_Date"].min()
max_date = df["Order_Date"].max()

date_range = st.sidebar.date_input(
    "Select Date Range",
    [min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

# Apply filters
filtered_df = df[df["Category"].isin(selected_categories)]

if len(date_range) == 2:
    filtered_df = filtered_df[
        (filtered_df["Order_Date"] >= pd.to_datetime(date_range[0])) &
        (filtered_df["Order_Date"] <= pd.to_datetime(date_range[1]))
    ]

# KPI Cards
col1, col2, col3, col4 = st.columns(4)

total_sales = filtered_df["Sales"].sum()
total_revenue = filtered_df["Revenue"].sum()
total_quantity = filtered_df["Quantity"].sum()
avg_discount = filtered_df["Discount"].mean()

col1.metric("💰 Total Sales", f"₹{total_sales:,.0f}")
col2.metric("📈 Total Revenue", f"₹{total_revenue:,.0f}")
col3.metric("📦 Total Items Sold", f"{total_quantity:,}")
col4.metric("🏷️ Avg Discount", f"{avg_discount:.1f}%")

st.markdown("---")

# Row 1: Revenue Trend
st.subheader("📅 Revenue Trend Over Time")
daily_revenue = filtered_df.groupby("Order_Date")["Revenue"].sum().reset_index()

fig_line = px.line(
    daily_revenue, 
    x="Order_Date", 
    y="Revenue",
    title="Revenue Trend",
    markers=True,
    template="plotly_white"
)
fig_line.update_layout(
    xaxis_title="Date",
    yaxis_title="Revenue (₹)",
    hovermode="x unified"
)
st.plotly_chart(fig_line, use_container_width=True)

# Row 2: Two columns for charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("🏆 Top 5 Products by Sales")
    product_sales = filtered_df.groupby("Product")["Sales"].sum().sort_values(ascending=False).head(5).reset_index()
    fig_bar = px.bar(
        product_sales,
        x="Sales",
        y="Product",
        orientation="h",
        text="Sales",
        title="Top Performing Products",
        template="plotly_white",
        color="Sales",
        color_continuous_scale="Viridis"
    )
    fig_bar.update_traces(texttemplate="₹%{text:,.0f}", textposition="outside")
    fig_bar.update_layout(height=400)
    st.plotly_chart(fig_bar, use_container_width=True)

with col2:
    st.subheader("📊 Sales by Category")
    category_sales = filtered_df.groupby("Category")["Sales"].sum().reset_index()
    fig_pie = px.pie(
        category_sales,
        values="Sales",
        names="Category",
        title="Category-wise Sales Distribution",
        hole=0.4,
        template="plotly_white"
    )
    fig_pie.update_traces(textposition="inside", textinfo="percent+label")
    fig_pie.update_layout(height=400)
    st.plotly_chart(fig_pie, use_container_width=True)

# Row 3: Sales by Product Category (Bar Chart)
st.subheader("📊 Monthly Sales Performance")
filtered_df["Month"] = filtered_df["Order_Date"].dt.strftime("%B")
monthly_sales = filtered_df.groupby("Month")["Sales"].sum().reset_index()
fig_month = px.bar(
    monthly_sales,
    x="Month",
    y="Sales",
    title="Monthly Sales",
    template="plotly_white",
    color="Sales",
    color_continuous_scale="Blues"
)
st.plotly_chart(fig_month, use_container_width=True)

# Raw data view
with st.expander("📄 View Raw Data"):
    st.dataframe(filtered_df)
    st.caption(f"Showing {len(filtered_df)} rows out of {len(df)} total rows")

# Download filtered data
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Download Filtered Data as CSV",
    data=csv,
    file_name="filtered_sales_data.csv",
    mime="text/csv",
)

st.markdown("---")
st.caption("✅ Dashboard is interactive! Use the filters on the left to explore the data.")