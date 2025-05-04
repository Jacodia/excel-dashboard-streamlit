import streamlit as st
import pandas as pd
import plotly.express as px

# --- Page setup ---
st.set_page_config(page_title="📊 Project Dashboard", layout="wide")

# --- Load data ---
@st.cache_data
def load_data():
    return pd.read_excel("Excel_Dashboard_Data_Prepared.xlsx")

df = load_data()

# --- Clean column names to remove any extra spaces or hidden characters ---
df.columns = df.columns.str.strip()  # Removes leading/trailing spaces

# --- Generate "Projects in Execution" column if it doesn't exist ---
if "Projects in Execution" not in df.columns:
    # Example: Generate a new column based on "Project Status" or other columns
    df['Projects in Execution'] = df['Project Status'].apply(lambda x: 'In Execution' if x == 'In Progress' else 'Not in Execution')

# --- Display column names to help with debugging ---
st.subheader("🧾 Column Names in Excel")
st.write(df.columns.tolist())

# --- Sidebar filters ---
st.sidebar.header("🔍 Filter")
projects = st.sidebar.multiselect("Select Projects", options=df["Projects in Execution"].dropna().unique())
status = st.sidebar.multiselect("Select Status", options=df["Project Status"].dropna().unique())

# --- Filter logic ---
filtered_df = df.copy()
if projects:
    filtered_df = filtered_df[filtered_df["Projects in Execution"].isin(projects)]
if status:
    filtered_df = filtered_df[filtered_df["Project Status"].isin(status)]

# --- Title ---
st.title("🚀 Project Dashboard")
st.markdown("Visualizing execution, status, and timeline metrics from the uploaded Excel data.")

# --- Show DataFrame preview ---
with st.expander("🔍 View Data"):
    st.dataframe(filtered_df, use_container_width=True)

# --- KPI Summary ---
col1, col2, col3 = st.columns(3)
col1.metric("📁 Total Projects", len(filtered_df))
col2.metric("✅ Completed", int((filtered_df["Project Status"] == "Completed").sum()))
col3.metric("🚧 In Progress", int((filtered_df["Project Status"] == "In Progress").sum()))

# --- Chart 1: Project Count by Status ---
if "Project Status" in filtered_df.columns:
    fig1 = px.bar(
        filtered_df["Project Status"].value_counts().reset_index(),
        x="index", y="Project Status",
        labels={"index": "Status", "Project Status": "Count"},
        title="📌 Project Count by Status"
    )
    st.plotly_chart(fig1, use_container_width=True)

# --- Chart 2: Projects by Department (if available) ---
if "Department" in filtered_df.columns:
    fig2 = px.pie(
        filtered_df,
        names="Department",
        title="🏢 Projects by Department"
    )
    st.plotly_chart(fig2, use_container_width=True)

# --- Chart 3: Duration Histogram (if available) ---
if "Duration in Days" in filtered_df.columns:
    fig3 = px.histogram(
        filtered_df,
        x="Duration in Days",
        nbins=20,
        title="⏳ Distribution of Project Durations"
    )
    st.plotly_chart(fig3, use_container_width=True)

# --- Chart 4: Duration vs Time Lapse per Project ---
if "Duration in Days" in filtered_df.columns and "Time lapse in Days" in filtered_df.columns:
    comparison_df = filtered_df[["Projects in Execution", "Duration in Days", "Time lapse in Days"]].dropna()

    if not comparison_df.empty:
        fig4 = px.bar(
            comparison_df.melt(id_vars="Projects in Execution", value_vars=["Duration in Days", "Time lapse in Days"]),
            x="Projects in Execution",
            y="value",
            color="variable",
            barmode="group",
            title="📊 Duration vs Time Lapse per Project",
            labels={"value": "Days", "variable": "Metric"},
        )
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("ℹ️ Not enough data to compare Duration and Time Lapse.")
else:
    st.info("ℹ️ Columns for Duration or Time Lapse are missing.")

# --- Download Option ---
with st.expander("⬇️ Download Filtered Data"):
    st.download_button(
        label="Download as Excel",
        data=filtered_df.to_excel(index=False),
        file_name="filtered_projects.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
