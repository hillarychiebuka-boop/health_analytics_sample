import streamlit as st
import plotly.express as px
import numpy as np
import pandas as pd
from utils.pdf_exporter import generate_executive_pdf

def render_commissioner_view(df_encounters, df_pharmacy, df_lab):
    st.markdown("## 🏛️ State Health Command Center")
    st.caption("Macro Executive Surveillance & Health Workforce Capacity Across Nasarawa State Facilities")
    
    total_visits = len(df_encounters)
    top_disease = df_encounters['Diagnosis'].mode()[0] if not df_encounters.empty else "N/A"
    nashia_coverage = round((len(df_encounters[df_encounters['Payer'] == 'Nasarawa Health Insurance Scheme (NASHIA)']) / total_visits * 100), 1) if total_visits > 0 else 0
    avg_wait = round(df_encounters['Wait_Time_Mins'].mean(), 1) if total_visits > 0 else 0
    
    narrative_html = (
        f"State health facilities logged <b>{total_visits:,} total patient visits</b>. "
        f"<b>{top_disease}</b> remains the primary clinical burden. "
        f"NASHIA Health Insurance coverage is currently at <b>{nashia_coverage}%</b>, "
        f"with average consultation wait times standing at <b>{avg_wait} minutes</b>."
    )
    
    st.markdown(
        f"""
        <div style="background-color: #0F172A; border-left: 5px solid #0284C7; padding: 14px; border-radius: 6px; margin-bottom: 15px;">
            <span style="color: #38BDF8; font-weight: bold;">EXECUTIVE BRIEFING:</span> 
            <span style="color: #E2E8F0;">{narrative_html}</span>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # PDF Generator
    pdf_plain = narrative_html.replace('<b>', '').replace('</b>', '')
    pdf_kpis = {
        "Total Patients Seen": f"{total_visits:,}",
        "Leading Diagnosis": top_disease,
        "NASHIA Insurance Coverage": f"{nashia_coverage}%",
        "Statewide Avg Wait Time": f"{avg_wait} mins"
    }
    
    pdf_bytes = generate_executive_pdf(
        title="State Ministry of Health Executive Brief",
        subtitle="Nasarawa State Healthcare Performance Summary",
        kpi_dict=pdf_kpis,
        narrative_summary=pdf_plain
    )
    
    st.download_button(
        label="📄 Export State Executive Brief (PDF)",
        data=pdf_bytes,
        file_name="State_Executive_Brief.pdf",
        mime="application/pdf"
    )
    
    st.markdown("---")
    
    # State Macro KPIs
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Patients Visited", f"{total_visits:,}")
    m2.metric("NASHIA Coverage", f"{nashia_coverage}%")
    m3.metric("Active Duty Practitioners", "142")
    m4.metric("Avg Statewide Wait Time", f"{avg_wait} mins")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Disease Surveillance & Outbreak Tracking")
        df_disease = df_encounters['Diagnosis'].value_counts().reset_index()
        df_disease.columns = ['Diagnosis', 'Patients Seen']
        fig_disease = px.bar(
            df_disease, x='Patients Seen', y='Diagnosis', orientation='h',
            color='Patients Seen', color_continuous_scale='Reds'
        )
        fig_disease.update_layout(
            xaxis_title="Number of Patients Visited",
            yaxis_title="Clinical Diagnosis",
            height=360, margin=dict(l=20, r=20, t=30, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_disease, use_container_width=True)
        
    with col2:
        # Replaced Donut with Clean Horizontal Bar Chart for Facility Inflow
        st.subheader("Facility Patient Inflow & Share Distribution")
        df_facility = df_encounters.groupby('Hospital').size().reset_index(name='Patients Visited').sort_values('Patients Visited', ascending=True)
        
        if not df_facility.empty:
            fig_fac = px.bar(
                df_facility, x='Patients Visited', y='Hospital', orientation='h',
                color='Patients Visited', color_continuous_scale='Blues'
            )
            fig_fac.update_layout(
                xaxis_title="Patients Visited",
                yaxis_title="Facility / Hospital",
                height=380, margin=dict(l=20, r=20, t=30, b=20), 
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_fac, use_container_width=True)
        else:
            st.info("No facility data available.")
        
    st.markdown("---")
    
    # Demographic & Patient Engagement Module
    st.subheader("👥 Patient Demographics & Health Workforce Distribution")
    c_demo1, c_demo2 = st.columns(2)
    
    with c_demo1:
        # Age Distribution
        age_groups = pd.DataFrame({
            "Age Bracket": ["0-12 yrs (Pediatrics)", "13-25 yrs (Youth)", "26-50 yrs (Adults)", "51+ yrs (Seniors)"],
            "Patients": [int(total_visits * 0.28), int(total_visits * 0.22), int(total_visits * 0.35), int(total_visits * 0.15)]
        })
        fig_age = px.bar(
            age_groups, 
            x="Age Bracket", 
            y="Patients", 
            color="Age Bracket", 
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        st.plotly_chart(fig_age, use_container_width=True)
        
    with c_demo2:
        # Active Health Workforce Breakdown
        workforce = pd.DataFrame({
            "Cadre": ["Medical Officers", "Consultants", "Nurses/Midwives", "Pharmacists", "Lab Scientists"],
            "Active On-Duty": [45, 18, 52, 14, 13]
        })
        fig_staff = px.pie(workforce, names="Cadre", values="Active On-Duty", hole=0.45, color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_staff.update_layout(
            height=300, showlegend=True, 
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_staff, use_container_width=True)
