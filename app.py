import pandas as pd
import plotly.express as px
import streamlit as st

# --- Page Configuration ---
st.set_page_config(page_title="📊 Project Dashboard", layout="wide")
st.title("Central Procurement Board of Namibia: Monitoring and Evaluation Projects Dashboard")

# --- Load Data ---
df = pd.read_excel('Excel_Dashboard_Data_Prepared.xlsx')

# --- Clean Columns and Convert Data Types ---
df.columns = df.columns.str.strip()
df["Expected completion Percentage"] = pd.to_numeric(df["Expected completion Percentage"], errors="coerce")
df["Commencement (Contract Signing Date/site handover)"] = pd.to_datetime(df["Commencement (Contract Signing Date/site handover)"], errors="coerce")
df["Revised Completion"] = pd.to_datetime(df["Revised Completion"], errors="coerce")

# --- Sidebar Filters ---
st.sidebar.header("🔍 Filter Options")

status = st.sidebar.multiselect(
    "Select Project Status", options=df["Project Status"].dropna().unique()
)

filtered_df = df.copy()
if status:
    filtered_df = filtered_df[filtered_df["Project Status"].isin(status)]
    
entities = st.sidebar.multiselect(
    "Select Public Entity",
    options=df["Public Entity's Name"].dropna().unique(),
    default=df["Public Entity's Name"].dropna().unique()
)

#--categories = st.sidebar.multiselect(
#--    "Select Procurement Category",
#--    options=df["Procurement Category"].dropna().unique(),
#--    default=df["Procurement Category"].dropna().unique()
#--)

#--nationalities = st.sidebar.multiselect(
 #--   "Select Contractor Nationality",
 #--   options=df["Contractor/ Service Provider Nationality"].dropna().unique(),
#--    default=df["Contractor/ Service Provider Nationality"].dropna().unique()
#--)--

# --- Apply Filters ---
filtered_df = df[
    (df["Project Status"].isin(status)) &
    (df["Public Entity's Name"].isin(entities))
   #-- (df["Procurement Category"].isin(categories)) &--
   #-- (df["Contractor/ Service Provider Nationality"].isin(nationalities))--
]

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
    title="Project Status Distribution",
    color="Project Status",
    labels={"count": "Number of Projects"},
    color_discrete_sequence=["#F79646", "#C0C0C0", "#000000", "#FFFFFF"]
)
st.plotly_chart(fig1, use_container_width=True)

# --- Procurement Categories Overview ---
st.markdown("Procurement Categories Overview")

filtered_df["Total Budget / Contract Value in N$"] = pd.to_numeric(
    filtered_df["Total Budget / Contract Value in N$"], errors="coerce"
)

category_summary = filtered_df.groupby("Procurement Category").agg(
    Total_Projects=("Procurement Category", "count"),
    Total_Value=("Total Budget / Contract Value in N$", "sum")
).reset_index()

category_summary["Total_Value_Mil"] = category_summary["Total_Value"] / 1_000_000
category_summary["Total_Value_Mil"] = category_summary["Total_Value_Mil"].apply(lambda x: f"N$ {x:,.2f}M")

cols = st.columns(len(category_summary))
colors = ["#F79646"]

for idx, row in category_summary.iterrows():
    with cols[idx]:
        st.markdown(
            f"""
            <div style='background: linear-gradient(145deg, {colors[idx % len(colors)]}, #ffffff20); padding: 1em; border-radius: 10px; text-align: center'>
                <h4 style='margin-bottom: 0.5em'>{row["Procurement Category"]}</h4>
                <p><strong>{row["Total_Projects"]} Projects</strong></p>
                <p><strong>{row["Total_Value_Mil"]}</strong></p>
            </div>
            """,
            unsafe_allow_html=True
        )

# --- Chart 3: Projects by Public Entity ---
project_count = filtered_df["Public Entity's Name"].value_counts().reset_index()
project_count.columns = ["Public Entity", "Count"]

fig3 = px.pie(
    project_count,
    values="Count",
    names="Public Entity",
    title="Projects by Public Entity",
    color_discrete_sequence=["#F79646", "#C0C0C0", "#FFFFFF", "#000000"]
)
fig3.update_traces(textinfo="label+value", textposition="inside")
st.plotly_chart(fig3, use_container_width=True)

# --- Chart 8: Completion Percentage per Project ---
st.markdown("Completion Percentage per Project")
completion_df = filtered_df[
    (filtered_df["Projects in Execution"].notna()) &
    (filtered_df["Average completion Percentage"].notna())
]
completion_df["Average completion Percentage"] = pd.to_numeric(
    completion_df["Average completion Percentage"], errors="coerce"
)

fig8 = px.bar(
    completion_df,
    x="Average completion Percentage",
    y="Projects in Execution",
    orientation="h",
    title="Completion Percentage per Project",
    labels={"Average completion Percentage": "Completion (%)", "Projects in Execution": "Project"},
    color="Average completion Percentage",
    color_continuous_scale=["#FFFFFF", "#C0C0C0", "#F79646", "#000000"]
)
fig8.update_layout(height=800)
st.plotly_chart(fig8, use_container_width=True)

# --- Chart 6: Projects by Contractor ---
st.markdown("Total Projects by Contractor/Service Provider")
contractor_counts = filtered_df["Contractor/ Service Provider"].value_counts().reset_index()
contractor_counts.columns = ["Contractor/Service Provider", "Total Projects"]

fig6 = px.bar(
    contractor_counts,
    x="Contractor/Service Provider",
    y="Total Projects",
    title="Total Projects by Contractor/Service Provider",
    text="Total Projects",
    color="Contractor/Service Provider",
    color_discrete_sequence=["#F79646", "#C0C0C0", "#000000", "#FFFFFF"]
)
fig6.update_traces(textposition="inside")
fig6.update_layout(xaxis_tickangle=-45, showlegend=False, height=600)
st.plotly_chart(fig6, use_container_width=True)

# --- Chart: Project Duration ---
st.markdown("Project Duration: Planned vs Actual (Days)")
duration_df = filtered_df[
    (filtered_df["Projects in Execution"].notna()) &
    (filtered_df["Duration in days"].notna()) &
    (filtered_df["Time Lapse in days"].notna())
].copy()
duration_df["Duration in days"] = pd.to_numeric(duration_df["Duration in days"], errors="coerce")
duration_df["Time Lapse in days"] = pd.to_numeric(duration_df["Time Lapse in days"], errors="coerce")

melted_duration = duration_df.melt(
    id_vars=["Projects in Execution"],
    value_vars=["Duration in days", "Time Lapse in days"],
    var_name="Type",
    value_name="Days"
)
melted_duration["Type"] = melted_duration["Type"].replace({
    "Duration in days": "Planned Duration",
    "Time Lapse in days": "Actual Duration"
})

fig_duration = px.bar(
    melted_duration,
    x="Days",
    y="Projects in Execution",
    color="Type",
    barmode="group",
    orientation="h",
    title="Project Duration: Planned vs Actual",
    labels={"Days": "Duration (days)", "Projects in Execution": "Project"},
    color_discrete_map={
        "Planned Duration": "#F79646",
        "Actual Duration": "#C0C0C0"
    }
)
fig_duration.update_layout(height=800)
st.plotly_chart(fig_duration, use_container_width=True)

# --- Chart: Contractor Nationality ---
st.markdown("Count of Service Provider Nationalities")
nationality_counts = filtered_df["Contractor/ Service Provider Nationality"].value_counts().reset_index()
nationality_counts.columns = ["Nationality", "Project Count"]

fig_nat = px.bar(
    nationality_counts,
    x="Nationality",
    y="Project Count",
    title="Projects by Contractor Nationality",
    text="Project Count",
    color_discrete_sequence=["#F79646", "#C0C0C0", "#FFFFFF", "#000000"]
)
fig_nat.update_traces(textposition="inside")
fig_nat.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig_nat, use_container_width=True)

# --- Chart 7: Budget vs Actual ---
st.markdown("Budget vs Actual Cost by Project")
budget_vs_actual_df = filtered_df[
    (filtered_df["Projects in Execution"].notna()) &
    (filtered_df["Total Budget / Contract Value in N$"].notna()) &
    (filtered_df["Actual Cost to Date (Mil)"].notna())
]

melted_df = budget_vs_actual_df.melt(
    id_vars="Projects in Execution",
    value_vars=["Total Budget / Contract Value in N$", "Actual Cost to Date (Mil)"],
    var_name="Metric",
    value_name="Amount"
)

fig7 = px.bar(
    melted_df,
    y="Projects in Execution",
    x="Amount",
    color="Metric",
    orientation="h",
    title="Budget vs Actual Cost by Project (Stacked)",
    labels={"Amount": "Amount (N$ Mil)", "Projects in Execution": "Project"},
    color_discrete_map={
        "Total Budget / Contract Value in N$": "#F79646",
        "Actual Cost to Date (Mil)": "#C0C0C0"
    }
)
fig7.update_layout(barmode="stack", height=800)
st.plotly_chart(fig7, use_container_width=True)

# --- View Filtered Data ---
with st.expander("🧮 View Filtered Data Table"):
    st.dataframe(filtered_df)

# --- Download Button ---
st.download_button(
    label="📥 Download Filtered Data",
    data=filtered_df.to_csv(index=False),
    file_name="filtered_projects.csv",
    mime="text/csv",
)
