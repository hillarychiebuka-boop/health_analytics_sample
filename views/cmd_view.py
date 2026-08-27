import streamlit as st
import plotly.express as px
import plotly.figure_factory as ff
from utils.pdf_exporter import generate_executive_pdf

def render_cmd_view(df_encounters, df_pharmacy, df_lab):
    st.markdown("## 🏥 Hospital CMD Operational & Patient Engagement View")
    st.caption("Facility Capacity, Demographics Breakdown, Patient Engagement & Billings Surveillance")
    
    hospitals = df_encounters['Hospital'].unique() if not df_encounters.empty else ["Dalhatu Araf Specialist Hospital (DASH), Lafia"]
    selected_hosp = st.selectbox("Select Target Health Facility", hospitals, index=0)
    
    h_enc = df_encounters[df_encounters['Hospital'] == selected_hosp]
    h_pharm = df_pharmacy[df_pharmacy['Hospital'] == selected_hosp]
    h_lab = df_lab[df_lab['Hospital'] == selected_hosp]
    
    if h_enc.empty:
        st.warning(f"No clinical activity recorded for {selected_hosp}.")
        return

    # Key Performance Metrics
    total_visits = len(h_enc)
    emr_adoption = round((h_enc['EMR_Logged'].sum() / total_visits * 100), 1) if total_visits > 0 else 0
    total_billing = f"₦{h_enc['Billing_Amount'].sum():,.2f}"
    no_show_rate = round((len(h_enc[h_enc['Engagement_Status'] == 'No-Show / Rescheduled']) / total_visits * 100), 1)
    avg_wait = round(h_enc['Wait_Time_Mins'].mean(), 1)
    
    narrative_html = (
        f"<b>{selected_hosp}</b> recorded <b>{total_visits:,} total patient visits</b>. "
        f"Appointment no-show rate stands at <b>{no_show_rate}%</b>, with an average consultation wait time of <b>{avg_wait} minutes</b>. "
        f"EMR digitization rate is <b>{emr_adoption}%</b>, with total billing volume reaching <b>{total_billing}</b>."
    )
    
    st.markdown(
        f"""
        <div style="background-color: #0F172A; border-left: 5px solid #0284C7; padding: 14px; border-radius: 6px; margin-bottom: 15px;">
            <span style="color: #38BDF8; font-weight: bold;">CMD EXECUTIVE SUMMARY:</span> 
            <span style="color: #E2E8F0;">{narrative_html}</span>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # PDF Brief Exporter
    pdf_plain = narrative_html.replace('<b>', '').replace('</b>', '')
    pdf_kpis = {
        "Facility Name": selected_hosp,
        "Total Patients Seen": f"{total_visits:,}",
        "Appointment No-Show Rate": f"{no_show_rate}%",
        "Average Consultation Wait": f"{avg_wait} mins",
        "EMR Digitization Rate": f"{emr_adoption}%",
        "Gross Revenue Billings": total_billing
    }
    
    pdf_bytes = generate_executive_pdf(
        title=f"CMD Operational Brief: {selected_hosp}",
        subtitle="Facility Revenue, Demographics & Patient Engagement Report",
        kpi_dict=pdf_kpis,
        narrative_summary=pdf_plain
    )
    
    st.download_button(
        label="📄 Export CMD Operational Brief (PDF)",
        data=pdf_bytes,
        file_name=f"CMD_Brief_{selected_hosp.replace(' ', '_')}.pdf",
        mime="application/pdf"
    )
    
    st.markdown("---")
    
    # Executive KPI Cards
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Patients Visited", f"{total_visits:,}")
    k2.metric("No-Show Rate", f"{no_show_rate}%", "Target <10%")
    k3.metric("Avg Wait Time", f"{avg_wait} mins")
    k4.metric("EMR Adoption", f"{emr_adoption}%")
    k5.metric("Gross Billings", total_billing)
    
    st.markdown("---")
    
    # SECTION 1: DEMOGRAPHICS & PATIENT ENGAGEMENT
    st.subheader("👥 Patient Demographics & Engagement Profiles")
    
    d_col1, d_col2, d_col3 = st.columns(3)
    
    with d_col1:
        st.markdown("**Age Distribution**")
        df_age = h_enc['Age_Group'].value_counts().reset_index()
        df_age.columns = ['Age Group', 'Patients Visited']
        fig_age = px.bar(df_age, x='Patients Visited', y='Age Group', orientation='h', color_discrete_sequence=['#38BDF8'])
        fig_age.update_layout(height=300, margin=dict(l=10, r=10, t=20, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_age, use_container_width=True)
        
    with d_col2:
        st.markdown("**Gender Distribution**")
        df_gender = h_enc['Gender'].value_counts().reset_index()
        df_gender.columns = ['Gender', 'Count']
        fig_gen = px.pie(df_gender, names='Gender', values='Count', hole=0.6, color_discrete_sequence=['#F43F5E', '#0EA5E9'])
        fig_gen.update_traces(textposition='outside', textinfo='percent+label')
        fig_gen.update_layout(height=300, margin=dict(l=10, r=10, t=20, b=30), showlegend=False, paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_gen, use_container_width=True)
        
    with d_col3:
        st.markdown("**Appointment Types**")
        df_appt = h_enc['Appointment_Type'].value_counts().reset_index()
        df_appt.columns = ['Type', 'Count']
        fig_appt = px.pie(df_appt, names='Type', values='Count', hole=0.6, color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_appt.update_traces(textposition='outside', textinfo='percent')
        fig_appt.update_layout(height=300, margin=dict(l=10, r=10, t=20, b=50), showlegend=True, legend=dict(orientation="h", xanchor="center", x=0.5), paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_appt, use_container_width=True)

    st.markdown("---")
    
    # SECTION 2: CLINICAL & WAIT TIME SURVEILLANCE
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Departmental Patient Inflow")
        df_dept = h_enc['Department'].value_counts().reset_index()
        df_dept.columns = ['Clinic Department', 'Patients Visited']
        fig_dept = px.bar(df_dept, x='Clinic Department', y='Patients Visited', color='Patients Visited', color_continuous_scale='Blues')
        fig_dept.update_layout(xaxis_title="Clinical Department", yaxis_title="Patients Visited", height=340, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_dept, use_container_width=True)
        
    with col2:
        st.subheader("Consultation Wait Time Profile")
        hist_data = [h_enc['Wait_Time_Mins'].dropna().tolist()]
        fig_wait = ff.create_distplot(hist_data, ['Wait Time (Mins)'], show_hist=False, show_rug=False, colors=['#0284C7'])
        fig_wait.update_layout(xaxis_title="Wait Time (Minutes)", yaxis_title="Probability Density", height=340, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
        st.plotly_chart(fig_wait, use_container_width=True)
