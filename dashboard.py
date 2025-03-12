import tkinter as tk
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import os
import warnings
warnings.filterwarnings('ignore')

# Configure the Streamlit page
st.set_page_config(page_title="Market Insights Dashboard", page_icon="📊", layout="wide")

# Page title and styling
st.title("📊 Market Insights Dashboard")
st.markdown(
    """
    <style>
        div.block-container {
            padding-top: 40px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# File upload functionality
uploaded_file = st.file_uploader("📂 Upload a Dataset (CSV, Excel)", type=["csv", "xlsx", "xls"])
if uploaded_file:
    file_name = uploaded_file.name
    st.write(f"Uploaded File: {file_name}")
    if file_name.endswith(".csv"):
        data = pd.read_csv(uploaded_file)
    else:
        data = pd.read_excel(uploaded_file)
else:
    # Load default dataset
    default_path = r"C:\Users\HP\AppData\Roaming\Python\Python313\site-packages\FINAL PROJECT"
    os.chdir(default_path)
    data = pd.read_excel("Sample - Superstore.xls")

# Data preprocessing
data["Order Date"] = pd.to_datetime(data["Order Date"])
min_date = data["Order Date"].min()
max_date = data["Order Date"].max()

# Date filter UI
col1, col2 = st.columns(2)
with col1:
    start_date = pd.to_datetime(st.date_input("Select Start Date", min_date))
with col2:
    end_date = pd.to_datetime(st.date_input("Select End Date", max_date))

# Filter data by selected date range
filtered_data = data[(data["Order Date"] >= start_date) & (data["Order Date"] <= end_date)].copy()

# Sidebar filters for region, state, and city
st.sidebar.header("Filter Options")
selected_regions = st.sidebar.multiselect("Choose Regions", filtered_data["Region"].unique())
selected_states = st.sidebar.multiselect("Choose States", filtered_data["State"].unique())
selected_cities = st.sidebar.multiselect("Choose Cities", filtered_data["City"].unique())

# Apply filters
if selected_regions:
    filtered_data = filtered_data[filtered_data["Region"].isin(selected_regions)]
if selected_states:
    filtered_data = filtered_data[filtered_data["State"].isin(selected_states)]
if selected_cities:
    filtered_data = filtered_data[filtered_data["City"].isin(selected_cities)]

# Category-wise Sales
category_sales = filtered_data.groupby("Category")["Sales"].sum().reset_index()
col1, col2 = st.columns(2)

with col1:
    st.subheader("Sales by Category")
    bar_chart = px.bar(
        category_sales,
        x="Category",
        y="Sales",
        text_auto=True,
        template="seaborn",
    )
    st.plotly_chart(bar_chart, use_container_width=True)

# Region-wise Sales
with col2:
    st.subheader("Sales by Region")
    pie_chart = px.pie(
        filtered_data,
        values="Sales",
        names="Region",
        hole=0.5,
        title="Sales Distribution by Region",
    )
    st.plotly_chart(pie_chart, use_container_width=True)

# Time-series Analysis
st.subheader("📅 Time-Series Sales Analysis")
filtered_data["Month-Year"] = filtered_data["Order Date"].dt.to_period("M")
time_series = (
    filtered_data.groupby(filtered_data["Month-Year"].dt.strftime("%Y-%m"))["Sales"]
    .sum()
    .reset_index()
)
time_series_chart = px.line(
    time_series,
    x="Month-Year",
    y="Sales",
    title="Monthly Sales Trend",
    template="plotly_white",
)
st.plotly_chart(time_series_chart, use_container_width=True)

# Hierarchical TreeMap
st.subheader("🌲 Hierarchical Sales Analysis")
treemap = px.treemap(
    filtered_data,
    path=["Region", "Category", "Sub-Category"],
    values="Sales",
    color="Sub-Category",
)
st.plotly_chart(treemap, use_container_width=True)

# Pie Chart: Segment-wise and Category-wise Sales
chart1, chart2 = st.columns(2)
with chart1:
    st.subheader("Sales by Segment")
    segment_pie = px.pie(
        filtered_data, values="Sales", names="Segment", template="plotly_dark"
    )
    st.plotly_chart(segment_pie, use_container_width=True)

with chart2:
    st.subheader("Sales by Category")
    category_pie = px.pie(filtered_data, values="Sales", names="Category")
    st.plotly_chart(category_pie, use_container_width=True)

# Scatter Plot: Sales vs. Profit
st.subheader("📈 Sales vs. Profit")
scatter_plot = px.scatter(
    filtered_data,
    x="Sales",
    y="Profit",
    size="Quantity",
    color="Category",
    title="Relationship between Sales and Profit",
)
st.plotly_chart(scatter_plot, use_container_width=True)

# Data download buttons
st.download_button(
    label="Download Filtered Dataset",
    data=filtered_data.to_csv(index=False).encode("utf-8"),
    file_name="Filtered_Data.csv",
    mime="text/csv",
)

st.subheader("🔍 Explore Data")
with st.expander("View Filtered Data"):
    st.dataframe(filtered_data.style.background_gradient(cmap="coolwarm"))

with st.expander("View Sales Summary by Category"):
    st.dataframe(category_sales.style.background_gradient(cmap="viridis"))
