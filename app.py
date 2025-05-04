import pandas as pd
import plotly.express as px
import streamlit as st

# Load CSV data
df = pd.read_csv('your_file.csv')

# --- Clean Data ---
# Strip column names to ensure no extra spaces
df.columns = df.columns.str.strip()

# Convert 'Expected completion Percentage' to numeric (handle non-numeric as NaN)
df['Expected completion Percentage'] = pd.to_numeric(df['Expected completion Percentage'], errors='coerce')

# Convert 'Commencement' and 'Revised Completion' to datetime
df['Commencement (Contract Signing Date/site handover)'] = pd.to_datetime(df['Commencement (Contract Signing Date/site handover)'], errors='coerce')
df['Revised Completion'] = pd.to_datetime(df['Revised Completion'], errors='coerce')

# --- Streamlit Sidebar ---
st.sidebar.title("Project Dashboard")
status = st.sidebar.multiselect("Select Project Status", options=df["Project Status"].dropna().unique())

# --- Filter Data Based on Status ---
filtered_df = df.copy()

if status:
    filtered_df = filtered_df[filtered_df["Project Status"].isin(status)]

# --- View Data ---
if st.sidebar.checkbox("Show Data"):
    st.write(filtered_df)

# --- Basic Visuals ---

# Total Projects Count
total_projects = len(filtered_df)
completed_projects = len(filtered_df[filtered_df["Project Status"] == "Completed"])
in_progress_projects = len(filtered_df[filtered_df["Project Status"] == "In Progress"])

st.subheader(f"Total Projects: {total_projects}")
st.subheader(f"Completed Projects: {completed_projects}")
st.subheader(f"In Progress Projects: {in_progress_projects}")

# Bar Chart: Project Status Distribution
fig1 = px.bar(
    filtered_df, 
    x="Project Status",  # Project Status
    title="Project Status Distribution",
    labels={"Project Status": "Status", "count": "Number of Projects"},
    color="Project Status",
    category_orders={"Project Status": ["Completed", "In Progress", "Not Started"]}  # Custom order if needed
)
st.plotly_chart(fig1)

# Line Chart: Time Lapse vs. Expected Completion
fig2 = px.line(
    filtered_df, 
    x="Time Lapse in days", 
    y="Expected completion Percentage", 
    title="Time Lapse vs Expected Completion Percentage"
)
st.plotly_chart(fig2)

# Budget vs Actual Cost
fig3 = px.scatter(
    filtered_df,
    x="Total Budget / Contract Value in N$",
    y="Actual Cost to Date (Mil)",
    title="Budget vs Actual Cost",
    labels={"Total Budget / Contract Value in N$": "Total Budget (N$)", "Actual Cost to Date (Mil)": "Actual Cost (Mil)"}
)
st.plotly_chart(fig3)

# --- Duration Overview ---
fig4 = px.histogram(
    filtered_df,
    x="Duration in days",
    title="Project Duration Distribution",
    nbins=20
)
st.plotly_chart(fig4)

# --- Date Range: Projects Started in a Specific Year ---
year_filter = st.sidebar.slider(
    "Select Year for Projects Commenced",
    min_value=int(df["Commencement (Contract Signing Date/site handover)"].dt.year.min()),
    max_value=int(df["Commencement (Contract Signing Date/site handover)"].dt.year.max()),
    value=(int(df["Commencement (Contract Signing Date/site handover)"].dt.year.min()), int(df["Commencement (Contract Signing Date/site handover)"].dt.year.max()))
)

filtered_year_df = filtered_df[
    (filtered_df["Commencement (Contract Signing Date/site handover)"].dt.year >= year_filter[0]) &
    (filtered_df["Commencement (Contract Signing Date/site handover)"].dt.year <= year_filter[1])
]

# Show filtered projects based on year selection
st.subheader(f"Projects Commenced Between {year_filter[0]} and {year_filter[1]}")
st.write(filtered_year_df)

