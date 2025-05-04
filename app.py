
import streamlit as st
import pandas as pd
import plotly.express as px

# Load data
df = pd.read_excel("Excel_Dashboard_Data_Prepared.xlsx")

# Title
st.title("📊 Project Dashboard - Streamlit Web App")

# Sidebar filters
entity_filter = st.sidebar.multiselect("Filter by Public Entity", options=df["Public Entity's Name"].unique(), default=df["Public Entity's Name"].unique())
category_filter = st.sidebar.multiselect("Filter by Procurement Category", options=df["Procurement Category"].dropna().unique(), default=df["Procurement Category"].dropna().unique())

# Apply filters
filtered_df = df[
    (df["Public Entity's Name"].isin(entity_filter)) &
    (df["Procurement Category"].isin(category_filter))
]

# Bar chart - Average completion % by Procurement Category
if not filtered_df.empty:
    bar_chart = filtered_df.groupby("Procurement Category")["Average completion Percentage"].mean().reset_index()
    fig1 = px.bar(bar_chart, x="Procurement Category", y="Average completion Percentage", title="🔧 Avg Completion % by Procurement Category")
    st.plotly_chart(fig1)

    # Line chart - Actual Cost over time
    cost_time_df = filtered_df.copy()
    cost_time_df["Commencement Date"] = pd.to_datetime(cost_time_df["Commencement (Contract Signing Date/site handover)"], errors='coerce')
    cost_time_df = cost_time_df.sort_values("Commencement Date")
    fig2 = px.line(cost_time_df, x="Commencement Date", y="Actual Cost to Date (Mil)", color="Projects in Execution", title="💰 Cost to Date Over Time")
    st.plotly_chart(fig2)

    # Pie chart - Project distribution by Public Entity
    pie_df = filtered_df["Public Entity's Name"].value_counts().reset_index()
    pie_df.columns = ["Public Entity", "Count"]
    fig3 = px.pie(pie_df, values="Count", names="Public Entity", title="🏛️ Project Count by Public Entity")
    st.plotly_chart(fig3)

    # Download filtered data
    st.download_button("📥 Download Filtered Data", filtered_df.to_csv(index=False), file_name="filtered_projects.csv", mime="text/csv")

else:
    st.warning("⚠️ No data matches the selected filters.")
