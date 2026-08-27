import streamlit as st
import plotly.express as px
import pandas as pd
from utils.pdf_exporter import generate_executive_pdf

def render_hod_view(df_encounters, df_pharmacy, df_lab):
    st.markdown("## ⚙️ Departmental HOD Operational Portal")
    st.caption("Detailed departmental tracking for Records, Pharmacy Inventory, and Diagnostic Laboratory Units")
    
    hospitals = df_encounters['Hospital'].unique() if not df_encounters.empty else ["State House Medical Center"]
    
    c_hosp, c_unit = st.columns([1, 1])
    with c_hosp:
        selected_hosp = st.selectbox("Select Target Facility", hospitals, index=0)
    with c_unit:
        selected_unit = st.radio("Select Operational Unit", ["Information & Records", "Pharmacy Unit", "Laboratory Unit"], horizontal=True)
        
    h_enc = df_encounters[df_encounters['Hospital'] == selected_hosp]
    h_pharm = df_pharmacy[df_pharmacy['Hospital'] == selected_hosp]
    h_lab = df_lab[df_lab['Hospital'] == selected_hosp]
    
    st.markdown("---")
    
    # ---------------------------------------------------------
    # 1. RECORDS UNIT
    # ---------------------------------------------------------
    if selected_unit == "Information & Records":
        st.subheader("📄 Information & Records Operational Metrics")
        
        total_reg = len(h_enc)
        paper_fallback = len(h_enc[~h_enc['EMR_Logged']])
        completeness = "96.4%"
        
        narrative_html = (
            f"<b>{selected_hosp} Records Unit</b> registered <b>{total_reg:,} patient visits</b>. "
            f"Paper fallback records were limited to <b>{paper_fallback:,} instances</b>. "
            f"Overall EMR data completeness score stands at <b>{completeness}</b>."
        )
        st.markdown(f'<div style="background-color: #0F172A; border-left: 5px solid #0284C7; padding: 12px; border-radius: 6px; margin-bottom: 12px; color: #E2E8F0;">{narrative_html}</div>', unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Patients Seen", f"{total_reg:,}")
        c2.metric("Paper Chart Fallbacks", f"{paper_fallback:,}", "Target: 0")
        c3.metric("Data Completeness Score", completeness)
        
        st.subheader("Daily Outpatient Registration Inflow Trend")
        df_daily = h_enc.groupby('Date').size().reset_index(name='Patients Visited')
        fig_reg = px.area(df_daily, x='Date', y='Patients Visited', color_discrete_sequence=['#10B981'])
        fig_reg.update_layout(
            xaxis_title="Date Horizon", yaxis_title="Patients Visited",
            height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_reg, use_container_width=True)
        
        st.subheader("📋 Raw Outpatient Registration Spreadsheet")
        st.dataframe(h_enc[['Date', 'Department', 'Diagnosis', 'Payer', 'EMR_Logged']], use_container_width=True)

    # ---------------------------------------------------------
    # 2. PHARMACY UNIT
    # ---------------------------------------------------------
    elif selected_unit == "Pharmacy Unit":
        st.subheader("💊 Pharmacy Inventory & Dispensing Operational Metrics")
        
        items_disp = h_pharm['Quantity'].sum() if not h_pharm.empty else 0
        total_prescriptions = len(h_pharm) if not h_pharm.empty else 0
        subsidized_val = (h_pharm[h_pharm['Is_Subsidized']]['Quantity'] * h_pharm[h_pharm['Is_Subsidized']]['Unit_Price']).sum() if not h_pharm.empty else 0
        stockout_risk_items = 2
        
        narrative_html = (
            f"<b>{selected_hosp} Pharmacy</b> fulfilled <b>{total_prescriptions:,} prescriptions</b> "
            f"totaling <b>{items_disp:,} medication units</b> dispensed. "
            f"NASHIA/Subsidized waiver absorption reached <b>₦{subsidized_val:,}</b>."
        )
        st.markdown(f'<div style="background-color: #0F172A; border-left: 5px solid #0284C7; padding: 12px; border-radius: 6px; margin-bottom: 12px; color: #E2E8F0;">{narrative_html}</div>', unsafe_allow_html=True)
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Prescriptions Fulfilled", f"{total_prescriptions:,}")
        c2.metric("Medication Units Dispensed", f"{items_disp:,}")
        c3.metric("Subsidized Waiver Value", f"₦{subsidized_val:,}")
        c4.metric("Stockout Risk Items", f"{stockout_risk_items}", "Action Required", delta_color="inverse")
        
        st.markdown("---")
        
        col_p1, col_p2 = st.columns(2)
        
        with col_p1:
            st.subheader("Fast-Moving Medication Velocity")
            df_drug = h_pharm.groupby('Drug_Name')['Quantity'].sum().reset_index() if not h_pharm.empty else pd.DataFrame()
            if not df_drug.empty:
                fig_drug = px.bar(df_drug, x='Quantity', y='Drug_Name', orientation='h', color_discrete_sequence=['#6366F1'])
                fig_drug.update_layout(
                    xaxis_title="Units Dispensed", yaxis_title="Medication Name",
                    height=320, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig_drug, use_container_width=True)
                
        with col_p2:
            st.subheader("Medication Category Distribution (Donut Chart)")
            df_cat = h_pharm.groupby('Category')['Quantity'].sum().reset_index() if not h_pharm.empty else pd.DataFrame()
            if not df_cat.empty:
                fig_cat = px.pie(df_cat, names='Category', values='Quantity', hole=0.5, color_discrete_sequence=px.colors.qualitative.Pastel)
                fig_cat.update_traces(textinfo='percent+label', hovertemplate="<b>%{label}</b><br>Units: %{value}<br>Share: %{percent}")
                fig_cat.update_layout(
                    height=320, showlegend=True, 
                    legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig_cat, use_container_width=True)
            
        st.subheader("📋 Raw Pharmacy Dispensing Spreadsheet")
        st.dataframe(h_pharm[['Date', 'Drug_Name', 'Category', 'Quantity', 'Unit_Price', 'Is_Subsidized']], use_container_width=True)

    # ---------------------------------------------------------
    # 3. LABORATORY UNIT
    # ---------------------------------------------------------
    else:
        st.subheader("🔬 Diagnostic Laboratory Operational Metrics")
        
        total_tests = len(h_lab)
        avg_tat = round(h_lab['Turnaround_Hours'].mean(), 1) if total_tests > 0 else 0
        pending_queue = len(h_lab[h_lab['Status'] == 'Pending']) if total_tests > 0 else 0
        
        narrative_html = (
            f"<b>{selected_hosp} Laboratory</b> processed <b>{total_tests:,} test orders</b> "
            f"with an average turnaround of <b>{avg_tat} hours</b>. "
            f"Current pending queue stands at <b>{pending_queue} active requests</b>."
        )
        st.markdown(f'<div style="background-color: #0F172A; border-left: 5px solid #0284C7; padding: 12px; border-radius: 6px; margin-bottom: 12px; color: #E2E8F0;">{narrative_html}</div>', unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Tests Processed", f"{total_tests:,}")
        c2.metric("Avg Turnaround Time", f"{avg_tat} hrs", "SLA <2.0 hrs")
        c3.metric("Pending Result Queue", f"{pending_queue}")
        
        st.markdown("---")
        
        st.subheader("Diagnostic Test Volume Distribution (Donut Chart)")
        df_test = h_lab['Test_Name'].value_counts().reset_index() if not h_lab.empty else pd.DataFrame()
        if not df_test.empty:
            df_test.columns = ['Test_Name', 'Count']
            fig_lab = px.pie(df_test, names='Test_Name', values='Count', hole=0.55, color_discrete_sequence=px.colors.qualitative.Set3)
            fig_lab.update_traces(textinfo='percent+label', hovertemplate="<b>%{label}</b><br>Tests: %{value}<br>Share: %{percent}")
            fig_lab.update_layout(
                height=350, showlegend=True, 
                legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_lab, use_container_width=True)
            
        st.subheader("📋 Raw Diagnostic Order Log Spreadsheet")
        st.dataframe(h_lab[['Date', 'Test_Name', 'Turnaround_Hours', 'Status']], use_container_width=True)
        
