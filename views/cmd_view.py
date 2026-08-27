import streamlit as st
import plotly.express as px
import plotly.figure_factory as ff
from utils.pdf_exporter import generate_executive_pdf

def render_cmd_view(df_encounters, df_pharmacy, df_lab):
    st.markdown("## 🏥 Hospital CMD Executive Command View")
    st.caption("Operational Throughput, Financial Billings, and Clinical Specialty Capacity")
    
    hospitals = df_encounters['Hospital'].unique() if not df_encounters.empty else ["State House Medical Center"]
    selected_hosp = st.selectbox("Select Target Hospital Facility", hospitals, index=0)
    
    h_enc = df_encounters[df_encounters['Hospital'] == selected_hosp]
    h_pharm = df_pharmacy[df_pharmacy['Hospital'] == selected_hosp]
    h_lab = df_lab[df_lab['Hospital'] == selected_hosp]
    
    if h_enc.empty:
        st.warning(f"No clinical activity logged for {selected_hosp} in selected horizon.")
        return

    total_visits = len(h_enc)
    emr_adoption = round((h_enc['EMR_Logged'].sum() / total_visits * 100), 1) if total_visits > 0 else 0
    total_billing = f"₦{h_enc['Billing_Amount'].sum():,}"
    prescriptions_count = len(h_pharm)
    avg_lab_tat = round(h_lab['Turnaround_Hours'].mean(), 1) if not h_lab.empty else 0.0
    
    narrative_html = (
        f"<b>{selected_hosp}</b> recorded <b>{total_visits:,} total patient visits</b>. "
        f"The EMR digital logging rate stands at <b>{emr_adoption}%</b>. "
        f"Gross billings reached <b>{total_billing}</b> across <b>{prescriptions_count:,} pharmacy prescriptions</b>, "
        f"with diagnostic laboratory turnaround averaging <b>{avg_lab_tat} hours</b>."
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
    
    pdf_plain = narrative_html.replace('<b>', '').replace('</b>', '')
    pdf_kpis = {
        "Facility Name": selected_hosp,
        "Total Patients Visited": f"{total_visits:,}",
        "EMR Adoption Rate": f"{emr_adoption}%",
        "Gross Revenue Billing": total_billing,
        "Prescriptions Fulfilled": f"{prescriptions_count:,}",
        "Avg Diagnostic Turnaround": f"{avg_lab_tat} Hours"
    }
    
    pdf_bytes = generate_executive_pdf(
        title=f"CMD Operational Brief: {selected_hosp}",
        subtitle="Facility Revenue, Clinical Appointments, and Care Quality Report",
        kpi_dict=pdf_kpis,
        narrative_summary=pdf_plain
    )
    
    st.download_button(
        label="📄 Export CMD Operational PDF Brief",
        data=pdf_bytes,
        file_name=f"CMD_Brief_{selected_hosp.replace(' ', '_')}.pdf",
        mime="application/pdf"
    )
    
    st.markdown("---")
    
    # Detailed Operational Metrics
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Patients Visited", f"{total_visits:,}")
    k2.metric("EMR Adoption Rate", f"{emr_adoption}%", "Target >85%")
    k3.metric("Gross Billings", total_billing)
    k4.metric("Prescriptions Issued", f"{prescriptions_count:,}")
    k5.metric("Lab Turnaround", f"{avg_lab_tat} hrs", "SLA <2.0 hrs")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Appointments & Patient Inflow per Clinic Unit")
        df_dept = h_enc['Department'].value_counts().reset_index()
        df_dept.columns = ['Clinic Specialty', 'Appointments / Patients Visited']
        fig_dept = px.bar(
            df_dept, x='Clinic Specialty', y='Appointments / Patients Visited', 
            color='Appointments / Patients Visited', color_continuous_scale='greens', text='Appointments / Patients Visited'
        )
        fig_dept.update_layout(
            xaxis_title="Clinic Department Unit",
            yaxis_title="Total Patients Visited",
            height=340, margin=dict(l=20, r=20, t=30, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_dept, use_container_width=True)
        
    with col2:
        st.subheader("Consultation Wait Time Distribution Density")
        hist_data = [h_enc['Wait_Time_Mins'].dropna().tolist()]
        group_labels = ['Consultation Wait Time']
        
        fig_wait = ff.create_distplot(hist_data, group_labels, show_hist=False, show_rug=False, colors=['#0284C7'])
        # Fully labeled axes for professional clarity
        fig_wait.update_layout(
            xaxis_title="Consultation Wait Time (Minutes)",
            yaxis_title="Density Probability Distribution",
            height=340, margin=dict(l=20, r=20, t=30, b=20), 
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False
        )
        st.plotly_chart(fig_wait, use_container_width=True)
