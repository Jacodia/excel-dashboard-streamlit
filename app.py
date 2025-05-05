import pandas as pd
import plotly.express as px
import streamlit as st

# --- Load CSV ---
st.set_page_config(page_title="📊 Project Dashboard", layout="wide")
st.title("Central Procurment Board of Namibia: Monitoring and Evaluation Projects Dashboard")

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

# --- Custom Color Palette for all Charts ---
custom_colors = {
    "Completed": "#2ca02c",  # Green
    "In Progress": "#ff7f0e",  # Orange
    "Procurement Category": "#1f77b4",  # Blue
    "Planned Duration": "#636EFA",  # Blue
    "Actual Duration": "#EF553B",  # Red
    "Budget": "#D62728",  # Dark Red
    "Actual Cost": "#17BECF",  # Teal
}

# --- Chart 1: Project Status Distribution ---
fig1 = px.bar(
    filtered_df,
    x="Project Status",
    title="📌 Project Status Distribution",
    color="Project Status",
    color_discrete_map=custom_colors,
    labels={"count": "Number of Projects"},
)
st.plotly_chart(fig1, use_container_width=True)

# --- Horizontal Cards: Procurement Category Overview with Contract Value ---
st.markdown("### 📦 Procurement Categories Overview")

# Clean and convert contract value
filtered_df["Total Budget / Contract Value in N$"] = pd.to_numeric(
    filtered_df["Total Budget / Contract Value in N$"], errors="coerce"
)

# Group by Procurement Category
category_summary = filtered_df.groupby("Procurement Category").agg(
    Total_Projects=("Procurement Category", "count"),
    Total_Value=("Total Budget / Contract Value in N$", "sum")
).reset_index()

# Format total value as currency in millions
category_summary["Total_Value_Mil"] = category_summary["Total_Value"] / 1_000_000
category_summary["Total_Value_Mil"] = category_summary["Total_Value_Mil"].apply(lambda x: f"N$ {x:,.2f}M")

# Display as horizontal cards with color accents
cols = st.columns(len(category_summary))

for idx, row in category_summary.iterrows():
    with cols[idx]:
        st.markdown(
            f"""
            <div style='background-color:{custom_colors["Procurement Category"]}; padding: 1em; border-radius: 10px; text-align: center'>
                <h4 style='margin-bottom: 0.5em'>{row["Procurement Category"]}</h4>
                <p><strong>{row["Total_Projects"]} Projects</strong></p>
                <p><strong>{row["Total_Value_Mil"]}</strong></p>
            </div>
            """,
            unsafe_allow_html=True
        )

# --- Chart 3: Project Count by Entity ---
fig3 = px.pie(
    project_count,
    values="Count",
    names="Public Entity",
    title="🏛️ Projects by Public Entity",
    color_discrete_map=custom_colors
)
st.plotly_chart(fig3, use_container_width=True)

# --- Chart 8: Completion Percentage per Project ---
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

# --- Chart 6: Total Projects by Contractor ---
fig6 = px.bar(
    contractor_counts,
    x="Contractor/Service Provider",
    y="Total Projects",
    title="📊 Total Projects by Contractor/Service Provider",
    text="Total Projects",  # Label with count
    color="Contractor/Service Provider",  # Different color per contractor
    labels={"Total Projects": "Number of Projects"},
    color_discrete_map=custom_colors
)
fig6.update_traces(textposition="inside")
fig6.update_layout(
    xaxis_tickangle=-45,
    showlegend=False,
    height=600
)
st.plotly_chart(fig6, use_container_width=True)

# --- Chart: 📅 Project Duration (Planned vs Actual) ---
fig_duration = px.bar(
    melted_duration,
    x="Days",
    y="Projects in Execution",
    color="Type",
    barmode="group",
    orientation="h",
    title="📅 Project Duration: Planned vs Actual",
    labels={"Days": "Duration (days)", "Projects in Execution": "Project"},
    color_discrete_map={
        "Planned Duration": custom_colors["Planned Duration"],
        "Actual Duration": custom_colors["Actual Duration"]
    }
)
fig_duration.update_layout(height=800)
st.plotly_chart(fig_duration, use_container_width=True)

# --- Chart: Count of Service Provider Nationality ---
fig_nat = px.bar(
    nationality_counts,
    x="Nationality",
    y="Project Count",
    title="🌍 Projects by Contractor Nationality",
    text="Project Count",  # Show total count as data label
    labels={"Project Count": "Total Projects"},
    color_discrete_map=custom_colors
)
fig_nat.update_traces(textposition="inside")
fig_nat.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig_nat, use_container_width=True)

# --- Chart 7: Budget vs Actual Cost by Project ---
fig7 = px.bar(
    melted_df,
    y="Projects in Execution",
    x="Amount",
    color="Metric",
    orientation="h",
    title="💰 Budget vs Actual Cost by Project (Stacked)",
    labels={"Amount": "Amount (N$ Mil)", "Projects in Execution": "Project"},
    color_discrete_map={
        "Total Budget / Contract Value in N$": custom_colors["Budget"],
        "Actual Cost to Date (Mil)": custom_colors["Actual Cost"]
    },
    barmode="stack"
)
fig7.update_layout(
    yaxis=dict(title="Project"),
    xaxis=dict(title="Amount (N$ Mil)"),
    legend_title="Metric",
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
