import streamlit as st
import pandas as pd
import plotly.express as px

# --- Page Configuration ---
st.set_page_config(page_title="Strategic Implementation Dashboard", layout="wide", page_icon="📈")

# --- Custom Styling ---
st.markdown("""
    <style>
        .main {
            background-color: #f8f9fa;
        }
        .stMetric {
            background-color: #ffffff;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            border-left: 5px solid #4e73df;
        }
        div[data-testid="stExpander"] {
            border: none;
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
            border-radius: 5px;
            margin-bottom: 10px;
            background-color: white;
        }
        h1, h2, h3 {
            color: #2c3e50;
        }
    </style>
""", unsafe_allow_html=True)

# --- Load Data ---
@st.cache_data
def load_data():
    try:
        # Load the CSV
        df = pd.read_csv('project_data.csv')
        # Ensure numeric conversion
        df['Completion (%)'] = pd.to_numeric(df['Completion (%)'], errors='coerce').fillna(0)
        # Ensure strings are handled correctly
        df = df.astype(object).fillna("")
        return df
    except FileNotFoundError:
        st.error("The file 'project_data.csv' was not found. Please ensure it is in the same directory.")
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.stop()

# --- Header ---
st.title("📋 Board Directives Implementation Tracker")
st.markdown("### Strategic Implementation Plan & Progress Monitoring")
st.markdown("---")

# --- Sidebar Filters ---
st.sidebar.header("🔍 Filter Options")

# Filter by Priority
priority_options = sorted(list(set(df["Priority"].astype(str))))
selected_priority = st.sidebar.multiselect(
    "Select Priority Level",
    options=priority_options,
    default=priority_options
)

# Filter by Status
status_options = sorted(list(set(df["Status"].astype(str))))
selected_status = st.sidebar.multiselect(
    "Select Status",
    options=status_options,
    default=status_options
)

# Filter by Action Item (Parent Category)
action_options = sorted(list(set(df["Action Item"].astype(str))))
selected_action = st.sidebar.multiselect(
    "Select Strategic Goal",
    options=action_options,
    default=action_options
)

# --- Apply Filters ---
filtered_df = df[
    (df["Priority"].isin(selected_priority)) & 
    (df["Action Item"].isin(selected_action)) &
    (df["Status"].isin(selected_status))
]

# --- Key Metrics ---
col1, col2, col3, col4 = st.columns(4)

total_tasks = len(filtered_df)
avg_completion = filtered_df["Completion (%)"].mean()
delayed_tasks = len(filtered_df[filtered_df["Status"] == "Delayed"])
completed_tasks = len(filtered_df[filtered_df["Status"] == "Completed"])

col1.metric("✅ Total Tasks", total_tasks)
col2.metric("📊 Avg Completion", f"{avg_completion:.1f}%")
col3.metric("⚠️ Delayed Tasks", delayed_tasks, delta=-delayed_tasks if delayed_tasks > 0 else 0, delta_color="inverse")
col4.metric("🏆 Completed Tasks", completed_tasks)

st.markdown("---")

# --- Dashboard Layout ---

# Row 1: Charts
c1, c2 = st.columns((2, 1))

with c1:
    st.subheader("Progress by Strategic Goal")
    # Calculate average progress per Action Item
    progress_summary = filtered_df.groupby("Action Item")["Completion (%)"].mean().reset_index().sort_values("Completion (%)", ascending=True)
    
    fig_prog = px.bar(
        progress_summary,
        x="Completion (%)",
        y="Action Item",
        orientation='h',
        title="Average Completion Percentage per Goal",
        color="Completion (%)",
        color_continuous_scale="RdYlGn",
        text_auto='.0f'
    )
    fig_prog.update_layout(xaxis_range=[0, 100])
    st.plotly_chart(fig_prog, use_container_width=True)

with c2:
    st.subheader("Project Status")
    status_counts = filtered_df["Status"].value_counts().reset_index()
    fig_status = px.pie(
        status_counts,
        values='count',
        names='Status',
        title="Task Status Distribution",
        color='Status',
        color_discrete_map={
            "Completed": "#2ecc71",
            "In Progress": "#3498db",
            "Not Started": "#95a5a6",
            "Delayed": "#e74c3c"
        },
        hole=0.4
    )
    st.plotly_chart(fig_status, use_container_width=True)

# Row 2: Detailed Task List with Progress Bars
st.subheader("📝 Detailed Action Plan & Monitoring")

st.dataframe(
    filtered_df[[
        "RAG Rating", "Priority", "Action Item", "Specific Action", "Status", "Completion (%)", "Progress Notes"
    ]], 
    use_container_width=True,
    column_config={
        "RAG Rating": st.column_config.TextColumn(
            "Health",
            help="Red (Critical), Amber (Warning), Green (On Track)",
            width="small"
        ),
        "Priority": st.column_config.TextColumn("Priority", width="small"),
        "Action Item": st.column_config.TextColumn("Goal", width="medium"),
        "Specific Action": st.column_config.TextColumn("Specific Task", width="large"),
        "Status": st.column_config.SelectboxColumn(
            "Status",
            options=["Not Started", "In Progress", "Completed", "Delayed"],
            width="medium"
        ),
        "Completion (%)": st.column_config.ProgressColumn(
            "Progress",
            format="%d%%",
            min_value=0,
            max_value=100,
            width="medium"
        ),
        "Progress Notes": st.column_config.TextColumn("Latest Notes", width="large"),
    },
    hide_index=True
)

# --- Download ---
st.markdown("---")
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Download Updated Data (with Status)",
    data=csv,
    file_name="project_data_monitored.csv",
    mime="text/csv",
)
