import streamlit as st
from data_loader import generate_synthetic_healthcare_data
from utils.filters import filter_data_by_duration
from views.commissioner_view import render_commissioner_view
from views.cmd_view import render_cmd_view
from views.hod_view import render_hod_view

# Page Config
st.set_page_config(
    page_title="State Healthcare Executive Portal",
    page_icon="🏥",
    layout="wide"
)

# Load Data Pipeline
df_encounters, df_pharmacy, df_lab = generate_synthetic_healthcare_data()

# Sidebar Navigation
st.sidebar.image("https://img.icons8.com/color/96/hospital-2.png", width=70)
st.sidebar.title("Health Analytics Engine")

role = st.sidebar.selectbox(
    "Select Stakeholder Portal Access",
    ["1. State Commissioner (Macro View)", "2. Hospital CMD (Executive View)", "3. Department HODs (Unit View)"]
)

st.sidebar.markdown("---")
st.sidebar.subheader("📅 Time Duration Filter")

duration = st.sidebar.selectbox(
    "Select Reporting Horizon",
    ["Last 7 Days (Weekly)", "Last 30 Days (Monthly)", "Last 90 Days (Quarterly)", "Last 365 Days (Annually)", "Full 2-Year Trend"]
)

# Apply Time Filter across all Datasets
filtered_encounters = filter_data_by_duration(df_encounters, duration)
filtered_pharmacy = filter_data_by_duration(df_pharmacy, duration)
filtered_lab = filter_data_by_duration(df_lab, duration)

# Route to Selected View
if "1. State Commissioner" in role:
    render_commissioner_view(filtered_encounters, filtered_pharmacy, filtered_lab)
elif "2. Hospital CMD" in role:
    render_cmd_view(filtered_encounters, filtered_pharmacy, filtered_lab)
else:
    render_hod_view(filtered_encounters, filtered_pharmacy, filtered_lab)
    
