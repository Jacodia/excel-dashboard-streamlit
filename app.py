import pandas as pd
import plotly.express as px
import streamlit as st

# Assuming you have loaded the data into a pandas DataFrame named df
df = pd.read_excel('your_excel_file.xlsx')

# --- Sidebar filter ---
status = st.sidebar.multiselect("Select Status", options=df["Project Status"].dropna().unique())

# --- Data filtering ---
filtered_df = df.copy()

if status:
    filtered_df = filtered_df[filtered_df["Project Status"].isin(status)]

# --- Check Data before Plotting ---
st.write(filtered_df.head())  # Show the first few rows to verify data

# --- Ensure that 'Expected completion Percentage' is numeric ---
filtered_df["Expected completion Percentage"] = pd.to_numeric(filtered_df["Expected completion Percentage"], errors='coerce')

# --- Plotting with Plotly ---
fig1 = px.bar(
    filtered_df, 
    x="Projects in Execution",  # Column for x-axis
    y="Expected completion Percentage",  # Column for y-axis
    color="Project Status",  # Grouping by Project Status
    title="Project Status Overview"
)

st.plotly_chart(fig1)
