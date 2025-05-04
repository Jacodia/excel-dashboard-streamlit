import streamlit as st
import pandas as pd
import plotly.express as px

# Title
st.set_page_config(page_title="📊 Project Dashboard", layout="wide")
st.title("📊 Project Dashboard - Streamlit Web App")

# Load data
@st.cache_data
def load_data():
    df = pd.read_excel("Excel_Dashboard_Data_Prepared.xlsx")
    df.columns = df.columns.str.strip()  # remove any extra spaces
    return df

df = load_data()

# Show preview
st.subheader("🗂️ Data Preview")
st.dataframe(df.head(10), use_container_width=True)

# Sidebar filters
st.sidebar.header("🔍 Filters")
entities = df["Public Entity's Name"].dropna().unique()
categories = df["Procurement Category"].dropna().unique()

selected_entities = st.sidebar.multiselect("Select Public Entities", options=entities, default=entities)
selected_categories = st.sidebar.multiselect("Select Procurement Categories", options=categories, default=categories)

# Apply filters
filtered_df = df[
    (df["Public Entity's Name"].isin(selected_entities)) &
    (df["Procurement Category"].isin(selected_categories))
]

# Check if filtered data is empty
if filtered_df.empty:
    st.warning("⚠️ No data found for the selected filters.")
    st.stop()

# Charts Section
st.subheader("📈 Visual Insights")

# Chart 1: Avg Completion % by Category
if "Average completion Percentage" in filtered_df.columns:
    avg_completion = filtered_df.groupby("Procurement Category")["Average completion Percentage"].mean().reset_index()
    fig1 = px.bar(avg_completion, x="Procurement Category", y="Average completion Percentage",
                  title="🔧 Avg Completion % by Procurement Category", color="Procurement Category")
    st.plotly_chart(fig1, use_container_width=True)
else:
    st.info("ℹ️ Column 'Average completion Percentage' not found.")

# Chart 2: Actual Cost Over Time
if "Commencement (Contract Signing Date/site handover)" in filtered_df.columns:
    filtered_df["Commencement Date"] = pd.to_datetime(filtered_df["Commencement (Contract Signing Date/site handover)"], errors='coerce')
    cost_data = filtered_df.dropna(subset=["Commencement Date", "Actual Cost to Date (Mil)"])
    if not cost_data.empty:
        fig2 = px.line(cost_data, x="Commencement Date", y="Actual Cost to Date (Mil)",
                       color="Projects in Execution", title="💰 Cost to Date Over Time")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("ℹ️ Not enough data for Cost to Date Over Time chart.")
else:
    st.info("ℹ️ 'Commencement Date' column missing.")

# Chart 3: Project Count by Entity
project_count = filtered_df["Public Entity's Name"].value_counts().reset_index()
project_count.columns = ["Public Entity", "Count"]
fig3 = px.pie(project_count, values="Count", names="Public Entity", title="🏛️ Projects by Public Entity")
st.plotly_chart(fig3, use_container_width=True)

# Download button
st.download_button(
    label="📥 Download Filtered Data",
    data=filtered_df.to_csv(index=False),
    file_name="filtered_projects.csv",
    mime="text/csv"
)
