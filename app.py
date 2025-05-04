import streamlit as st
import pandas as pd
import plotly.express as px

# Page config
st.set_page_config(page_title="Interactive Excel Dashboard", layout="wide")

# Title
st.title("📊 Interactive Dashboard from Excel")

# Upload or use local Excel
df = pd.read_excel("Excel_Dashboard_Data_Prepared.xlsx")

# Sidebar filters
st.sidebar.header("🔍 Filters")
if 'Region' in df.columns:
    region = st.sidebar.multiselect("Region", options=df['Region'].unique(), default=df['Region'].unique())
    df = df[df['Region'].isin(region)]

if 'Category' in df.columns:
    category = st.sidebar.multiselect("Category", options=df['Category'].unique(), default=df['Category'].unique())
    df = df[df['Category'].isin(category)]

# Show data
st.subheader("📄 Preview Data")
st.dataframe(df, use_container_width=True)

# Charts
st.subheader("📈 Charts")

# Example Chart 1: Sales by Region
if 'Region' in df.columns and 'Sales' in df.columns:
    fig1 = px.bar(df.groupby('Region')['Sales'].sum().reset_index(), x='Region', y='Sales', title="Sales by Region")
    st.plotly_chart(fig1, use_container_width=True)

# Example Chart 2: Sales over Time
if 'Date' in df.columns and 'Sales' in df.columns:
    df['Date'] = pd.to_datetime(df['Date'])
    time_df = df.groupby('Date')['Sales'].sum().reset_index()
    fig2 = px.line(time_df, x='Date', y='Sales', title="Sales Over Time")
    st.plotly_chart(fig2, use_container_width=True)

# Export data
st.download_button("📥 Download Filtered Data", df.to_csv(index=False), file_name="filtered_data.csv")
