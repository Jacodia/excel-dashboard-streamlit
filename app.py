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

# --- Horizontal Cards: Procurement Category Counts ---
st.markdown("### 📦 Procurement Categories Overview")

# Count procurement categories
procurement_counts = filtered_df["Procurement Category"].value_counts().reset_index()
procurement_counts.columns = ["Category", "Total"]

# Display counts as horizontal metrics
cols = st.columns(len(procurement_counts))

for idx, row in procurement_counts.iterrows():
    with cols[idx]:
        st.metric(label=row["Category"], value=row["Total"])


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

# --- Chart 8: Completion Percentage per Project ---
st.markdown("### 📊 Completion Percentage per Project")

# Filter out rows without completion percentage or project names
completion_df = filtered_df[
    (filtered_df["Projects in Execution"].notna()) &
    (filtered_df["Average completion Percentage"].notna())
]

# Ensure the percentage column is numeric
completion_df["Average completion Percentage"] = pd.to_numeric(
    completion_df["Average completion Percentage"], errors="coerce"
)

# Create the horizontal bar chart
fig8 = px.bar(
    completion_df,
    x="Average completion Percentage",
    y="Projects in Execution",
    orientation="h",
    title="📈 Completion Percentage per Project",
    labels={
        "Average completion Percentage": "Completion (%)",
        "Projects in Execution": "Project"
    },
    color="Average completion Percentage",
    color_continuous_scale="Blues"
)

fig8.update_layout(
    xaxis=dict(title="Completion (%)"),
    yaxis=dict(title="Project"),
    height=800
)

st.plotly_chart(fig8, use_container_width=True)


# --- Chart 6: Total Projects by Contractor as Bar Chart with Count Labels ---
st.markdown("### 📊 Total Projects by Contractor/Service Provider")

# Count total projects per contractor
contractor_counts = (
    filtered_df["Contractor/ Service Provider"]
    .value_counts()
    .reset_index()
)
contractor_counts.columns = ["Contractor/Service Provider", "Total Projects"]

# Create bar chart with count labels inside the bars
fig6 = px.bar(
    contractor_counts,
    x="Contractor/Service Provider",
    y="Total Projects",
    title="📊 Total Projects by Contractor/Service Provider",
    text="Total Projects",  # Label with count
    color="Contractor/Service Provider",  # Different color per contractor
    labels={"Total Projects": "Number of Projects"},
)

# Customize the text to be inside the bars
fig6.update_traces(textposition="inside")
fig6.update_layout(
    xaxis_tickangle=-45,
    showlegend=False,
    height=600
)

# Display the chart
st.plotly_chart(fig6, use_container_width=True)



# --- Chart: Count of Service Provider Nationality ---
st.markdown("### 🌍 Count of Service Provider Nationalities")

# Count occurrences
nationality_counts = filtered_df["Contractor/ Service Provider Nationality"].value_counts().reset_index()
nationality_counts.columns = ["Nationality", "Project Count"]

# Create bar chart with data labels
fig_nat = px.bar(
    nationality_counts,
    x="Nationality",
    y="Project Count",
    title="🌍 Projects by Contractor Nationality",
    text="Project Count",  # Show total count as data label
    labels={"Project Count": "Total Projects"},
)

# Update layout for better readability
fig_nat.update_traces(textposition="inside")
fig_nat.update_layout(xaxis_tickangle=-45)

st.plotly_chart(fig_nat, use_container_width=True)



# --- Chart 7: Budget vs Actual Cost by Project  ---
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
