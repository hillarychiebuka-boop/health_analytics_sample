import streamlit as st
import plotly.express as px
from utils.pdf_exporter import generate_executive_pdf

def render_commissioner_view(df_encounters, df_pharmacy, df_lab):
    st.markdown("## 🏛️ State Health Command Center")
    st.caption("Macro Executive Surveillance across Nasarawa State Facilities")
    
    if df_encounters is None or df_encounters.empty:
        st.warning("⚠️ No encounter data available for the selected filters.")
        return

    # Core High-Level Aggregates
    total_visits = len(df_encounters)
    top_disease = df_encounters['Diagnosis'].mode()[0] if not df_encounters['Diagnosis'].dropna().empty else "N/A"
    
    nashia_count = len(df_encounters[df_encounters['Payer'] == 'Nasarawa Health Insurance Scheme (NASHIA)'])
    nashia_coverage = round((nashia_count / total_visits * 100), 1) if total_visits > 0 else 0.0
    avg_wait = round(df_encounters['Wait_Time_Mins'].mean(), 1) if total_visits > 0 else 0.0
    
    # Narrative Briefing Box
    narrative_html = (
        f"State health facilities logged <b>{total_visits:,} total patient visits</b>. "
        f"<b>{top_disease}</b> represents the leading burden of disease. "
        f"State Health Insurance (NASHIA) coverage stands at <b>{nashia_coverage}%</b> of total patient visits, "
        f"while average statewide consultation wait time is <b>{avg_wait} minutes</b>."
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
        "Leading Burden of Disease": top_disease,
        "NASHIA Insurance Coverage": f"{nashia_coverage}%",
        "Statewide Avg Wait Time": f"{avg_wait} mins"
    }
    
    pdf_bytes = generate_executive_pdf(
        title="State Ministry of Health Executive Brief",
        subtitle="Nasarawa State Macro Healthcare Performance Summary",
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
    
    # 4-Column Clean KPI Grid (No Active Practitioners)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Patients Visited", f"{total_visits:,}")
    c2.metric("Leading Disease Burden", top_disease)
    c3.metric("NASHIA Coverage Rate", f"{nashia_coverage}%")
    c4.metric("Avg Statewide Wait Time", f"{avg_wait} mins")
    
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
            yaxis_title="Clinical Diagnosis",
            height=380, margin=dict(l=20, r=20, t=30, b=20), 
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_disease, use_container_width=True)
        
    with col2:
        st.subheader("Facility Patient Share Distribution")
        df_facility = df_encounters.groupby('Hospital').size().reset_index(name='Patients Visited')
        
        if not df_facility.empty:
            fig_fac = px.pie(
                df_facility, names='Hospital', values='Patients Visited', hole=0.6,
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            fig_fac.update_traces(
                textposition='outside', 
                textinfo='percent',
                hovertemplate="<b>%{label}</b><br>Patients: %{value:,}<br>Share: %{percent}"
            )
            fig_fac.update_layout(
                height=380, 
                margin=dict(l=30, r=30, t=30, b=50), 
                showlegend=True, 
                legend=dict(orientation="h", xanchor="center", x=0.5),
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_fac, use_container_width=True)
        else:
            st.info("No facility data available for donut breakdown.")
