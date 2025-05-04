import pandas as pd
import plotly.express as px
import streamlit as st

# --- Load CSV ---
st.set_page_config(page_title="📊 Project Dashboard", layout="wide")
st.title("🚀 Central Procurment Board of Namibia: Monitoring and Evaluation Projects Dashboard")

# Replace 'your_file.csv' with your actual filename
df = pd.read_excel('Excel_Dashboard_Data_Prepared.xlsx')

# --- Clean Columns and Convert Data Types ---
df.columns = df.columns.str.strip()

df["Expected completion Percentage"] = pd.to_numeric(
    df["Expected completion Percentage"], errors="coerce"
)
df["Commencement (Contract Signing Date/site handover)"] = pd.to_datetime(
    df["Commencement (Contract Signing Date/site handover)"], errors="coerce"
)
df["Revised Completion"] = pd.to_datetime(
    df["Revised Completion"], errors="coerce"
)

# --- Sidebar Filters ---
st.sidebar.header("🔍 Filter Options")
status = st.sidebar.multiselect(
    "Select Project Status", options=df["Project Status"].dropna().unique()
)

# --- Filter Data ---
filtered_df = df.copy()

if status:
    filtered_df = filtered_df[filtered_df["Project Status"].isin(status)]

# --- Project Summary ---
st.markdown("### 🧾 Project Summary")
col1, col2, col3 = st.columns(3)
col1.metric("📁 Total Projects", len(filtered_df))
col2.metric("✅ Completed", len(filtered_df[filtered_df["Project Status"] == "Completed"]))
col3.metric("🚧 In Progress", len(filtered_df[filtered_df["Project Status"] == "In Progress"]))

# --- Chart 1: Project Status Distribution ---
fig1 = px.bar(
    filtered_df,
    x="Project Status",
    title="📌 Project Status Distribution",
    color="Project Status",
    labels={"count": "Number of Projects"},
)
st.plotly_chart(fig1, use_container_width=True)

# --- Chart 2: Time Lapse vs. Expected Completion ---
fig2 = px.scatter(
    filtered_df,
    x="Time Lapse in days",
    y="Expected completion Percentage",
    title="📈 Time Lapse vs Expected Completion",
    labels={"Time Lapse in days": "Days", "Expected completion Percentage": "% Complete"},
)
st.plotly_chart(fig2, use_container_width=True)

# --- Chart 3: Project Count by Entity ---
project_count = filtered_df["Public Entity's Name"].value_counts().reset_index()
project_count.columns = ["Public Entity", "Count"]
fig3 = px.pie(
    project_count,
    values="Count",
    names="Public Entity",
    title="🏛️ Projects by Public Entity",
)
st.plotly_chart(fig3, use_container_width=True)

# --- Chart 4: Budget vs Actual Cost ---
fig4 = px.scatter(
    filtered_df,
    x="Total Budget / Contract Value in N$",
    y="Actual Cost to Date (Mil)",
    title="💰 Budget vs Actual Cost",
    labels={
        "Total Budget / Contract Value in N$": "Budget (N$)",
        "Actual Cost to Date (Mil)": "Actual Cost (Mil)",
    },
)
st.plotly_chart(fig4, use_container_width=True)

# --- Chart 5: Project Duration Distribution ---
fig5 = px.histogram(
    filtered_df,
    x="Duration in days",
    nbins=20,
    title="⏱️ Project Duration Distribution",
)
st.plotly_chart(fig5, use_container_width=True)

# --- Chart 6: Total Projects by Contractor as Pie Chart with Counts ---
st.markdown("### 🥧 Total Projects by Contractor/Service Provider (Pie Chart - Counts)")

# Unique contractor list for filter
contractor_options = filtered_df["Contractor/ Service Provider"].dropna().unique()

# Multiselect dropdown to filter contractors
selected_contractors = st.multiselect(
    "Select Contractor(s) to View", options=contractor_options, default=contractor_options
)

# Filter the DataFrame based on selected contractors
contractor_filtered_df = filtered_df[
    filtered_df["Contractor/ Service Provider"].isin(selected_contractors)
]

# Count total projects per selected contractor
contractor_counts = (
    contractor_filtered_df["Contractor/ Service Provider"]
    .value_counts()
    .reset_index()
)
contractor_counts.columns = ["Contractor/Service Provider", "Total Projects"]

# Create pie chart with counts (no percentages)
fig6 = px.pie(
    contractor_counts,
    values="Total Projects",
    names="Contractor/Service Provider",
    title="🥧 Total Projects by Contractor/Service Provider",
)

# Show count only, no percentages
fig6.update_traces(textinfo="value")

# Display the chart
st.plotly_chart(fig6, use_container_width=True)

# --- View Data Table ---
with st.expander("🧮 View Filtered Data Table"):
    st.dataframe(filtered_df)

# --- Download Button ---
st.download_button(
    label="📥 Download Filtered Data",
    data=filtered_df.to_csv(index=False),
    file_name="filtered_projects.csv",
    mime="text/csv",
)

# --- Chart 7: Budget vs Actual Cost by Project (Stacked & Horizontal) ---
st.markdown("### 💰 Budget vs Actual Cost by Project")

# Filter out rows with missing or zero budget or cost
budget_vs_actual_df = filtered_df[
    (filtered_df["Projects in Execution"].notna()) &
    (filtered_df["Total Budget / Contract Value in N$"].notna()) &
    (filtered_df["Actual Cost to Date (Mil)"].notna())
]

# Melt the dataframe for stacked plotting
melted_df = budget_vs_actual_df.melt(
    id_vars="Projects in Execution",
    value_vars=["Total Budget / Contract Value in N$", "Actual Cost to Date (Mil)"],
    var_name="Metric",
    value_name="Amount"
)

# Create the stacked horizontal bar chart
fig7 = px.bar(
    melted_df,
    y="Projects in Execution",
    x="Amount",
    color="Metric",
    orientation="h",
    title="💰 Budget vs Actual Cost by Project (Stacked)",
    labels={"Amount": "Amount (N$ Mil)", "Projects in Execution": "Project"},
)

fig7.update_layout(
    yaxis=dict(title="Project"),
    xaxis=dict(title="Amount (N$ Mil)"),
    legend_title="Metric",
    barmode="stack",
    height=800
)

st.plotly_chart(fig7, use_container_width=True)
