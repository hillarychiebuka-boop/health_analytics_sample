import streamlit as st
import plotly.express as px
import pandas as pd
from utils.pdf_exporter import generate_executive_pdf

def render_commissioner_view(df_encounters, df_pharmacy, df_lab):
    st.markdown("## 🏛️ State Health Command Center")
    st.caption("Macro Executive Surveillance, Patient Demographics & Health Workforce Capacity Across Nasarawa State Facilities")
    
    total_visits = len(df_encounters)
    top_disease = df_encounters['Diagnosis'].mode()[0] if not df_encounters.empty else "N/A"
    nashia_coverage = round((len(df_encounters[df_encounters['Payer'] == 'Nasarawa Health Insurance Scheme (NASHIA)']) / total_visits * 100), 1) if total_visits > 0 else 0
    avg_wait = round(df_encounters['Wait_Time_Mins'].mean(), 1) if total_visits > 0 else 0
    
    narrative_html = (
        f"State health facilities logged <b>{total_visits:,} total patient visits</b>. "
        f"<b>{top_disease}</b> remains the leading clinical burden. "
        f"NASHIA Health Insurance coverage stands at <b>{nashia_coverage}%</b>, "
        f"with average clinical wait times across facilities at <b>{avg_wait} minutes</b>."
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
    m2.metric("NASHIA Coverage Rate", f"{nashia_coverage}%")
    m3.metric("Active Duty Workforce", "142 Health Personnel")
    m4.metric("Statewide Avg Wait Time", f"{avg_wait} mins")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Disease Surveillance & Outbreak Tracking")
        df_disease = df_encounters['Diagnosis'].value_counts().reset_index()
        df_disease.columns = ['Diagnosis', 'Patients Visited']
        fig_disease = px.bar(
            df_disease, x='Patients Visited', y='Diagnosis', orientation='h',
            color='Patients Visited', color_continuous_scale='Reds'
        )
        fig_disease.update_layout(
            xaxis_title="Number of Patients Visited",
            yaxis_title="Diagnosis Category",
            height=360, margin=dict(l=20, r=20, t=30, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_disease, use_container_width=True)
        
    with col2:
        st.subheader("Facility Inflow Distribution (Donut Chart)")
        df_facility = df_encounters.groupby('Hospital').size().reset_index(name='Patients Visited')
        
        # Donut Chart
        fig_fac = px.pie(
            df_facility, names='Hospital', values='Patients Visited', hole=0.55,
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_fac.update_traces(textinfo='percent+label', hovertemplate="<b>%{label}</b><br>Patients: %{value}<br>Share: %{percent}")
        fig_fac.update_layout(
            height=360, 
            margin=dict(l=10, r=10, t=30, b=10), 
            showlegend=True, 
            legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_fac, use_container_width=True)

    st.markdown("---")
    
    # Demographics and Workforce Module
    st.subheader("👥 Patient Engagement & Demographic Breakdown")
    c_demo1, c_demo2 = st.columns(2)
    
    with c_demo1:
        st.markdown("**Patient Age Demographics**")
        age_groups = pd.DataFrame({
            "Age Bracket": ["0-12 yrs (Pediatrics)", "13-25 yrs (Youth)", "26-50 yrs (Adults)", "51+ yrs (Seniors)"],
            "Patients Visited": [int(total_visits * 0.28), int(total_visits * 0.22), int(total_visits * 0.35), int(total_visits * 0.15)]
        })
        fig_age = px.bar(age_groups, x="Age Bracket", y="Patients Visited", color="Age Bracket", color_discrete_sequence=px.colors.qualitative.Blues_r)
        fig_age.update_layout(
            xaxis_title="Age Group Bracket",
            yaxis_title="Total Patients Visited",
            height=300, showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_age, use_container_width=True)
        
    with c_demo2:
        st.markdown("**Active Clinical Practitioner Roster**")
        workforce = pd.DataFrame({
            "Cadre": ["Medical Officers", "Consultants", "Nurses/Midwives", "Pharmacists", "Lab Scientists"],
            "Active Personnel": [45, 18, 52, 14, 13]
        })
        fig_staff = px.pie(workforce, names="Cadre", values="Active Personnel", hole=0.5, color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_staff.update_traces(textinfo='percent+label')
        fig_staff.update_layout(
            height=300, showlegend=True, 
            legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_staff, use_container_width=True)
