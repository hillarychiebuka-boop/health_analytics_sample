import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_synthetic_healthcare_data(num_records=1500):
    np.random.seed(42)
    
    # 1. Nasarawa State & FCT Facilities
    facilities = [
        "Dalhatu Araf Specialist Hospital (DASH), Lafia",
        "Federal Medical Centre, Keffi",
        "General Hospital, Karu",
        "Akwanga General Hospital"
    ]
    
    # 2. Specialties / Departments
    departments = [
        "General Outpatient (GOPD)",
        "Pediatrics",
        "Obstetrics & Gynecology (ANC)",
        "Internal Medicine",
        "Accident & Emergency (A&E)",
        "Immunization & Child Welfare"
    ]
    
    # 3. Disease Burden (Local Profile)
    diagnoses = [
        "Uncomplicated Malaria",
        "Essential Hypertension",
        "Acute Respiratory Infection",
        "Type 2 Diabetes Mellitus",
        "Gastroenteritis",
        "Antenatal Care Routine"
    ]
    
    # 4. Nigerian Payer Landscape
    payers = [
        "Nasarawa Health Insurance Scheme (NASHIA)",
        "NHIA (Federal Sector)",
        "Out-of-Pocket (Self-Pay)",
        "Private HMO Coverage"
    ]
    payer_probs = [0.35, 0.20, 0.35, 0.10]
    
    # 5. Age Groups & Gender Cohorts
    age_groups = ["0-5 yrs (Pediatric)", "6-17 yrs (Adolescent)", "18-45 yrs (Adult)", "46-60 yrs (Mature)", "60+ yrs (Geriatric)"]
    age_probs = [0.22, 0.13, 0.40, 0.15, 0.10]
    genders = ["Female", "Male"]
    
    # 6. Appointment Types & Engagement Status
    appointment_types = ["Scheduled Follow-up", "Walk-in Emergency", "Routine ANC/Immunization", "Referral Specialist"]
    engagement_status = ["Attended", "Attended", "Attended", "No-Show / Rescheduled"]
    
    # Timestamps over last 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    dates = [start_date + timedelta(seconds=np.random.randint(0, int((end_date - start_date).total_seconds()))) for _ in range(num_records)]
    dates.sort()
    
    # --- ENCOUNTERS DATAFRAME ---
    encounters = []
    for i in range(num_records):
        enc_id = f"ENC-NG-{10000 + i}"
        pat_id = f"PAT-NAS-{np.random.randint(1000, 4000)}"
        hosp = np.random.choice(facilities, p=[0.40, 0.30, 0.18, 0.12])
        dept = np.random.choice(departments)
        diag = np.random.choice(diagnoses, p=[0.30, 0.20, 0.15, 0.12, 0.13, 0.10])
        payer = np.random.choice(payers, p=payer_probs)
        
        age_group = np.random.choice(age_groups, p=age_probs)
        gender = np.random.choice(genders, p=[0.54, 0.46])
        appt_type = np.random.choice(appointment_types, p=[0.35, 0.30, 0.25, 0.10])
        status = np.random.choice(engagement_status, p=[0.75, 0.10, 0.05, 0.10])
        
        wait_time = int(np.random.normal(loc=42, scale=15)) # Avg wait in mins
        wait_time = max(10, min(wait_time, 140))
        
        billing = round(float(np.random.exponential(scale=8500) + 1500), 2) # NGN
        emr_logged = np.random.choice([True, False], p=[0.88, 0.12])
        
        encounters.append({
            "Encounter_ID": enc_id,
            "Patient_ID": pat_id,
            "Date": dates[i].date(),
            "Timestamp": dates[i],
            "Hospital": hosp,
            "Department": dept,
            "Diagnosis": diag,
            "Payer": payer,
            "Age_Group": age_group,
            "Gender": gender,
            "Appointment_Type": appt_type,
            "Engagement_Status": status,
            "Wait_Time_Mins": wait_time,
            "Billing_Amount": billing,
            "EMR_Logged": emr_logged
        })
        
    df_encounters = pd.DataFrame(encounters)
    
    # --- PHARMACY ORDERS DATAFRAME ---
    drugs = [
        ("Artemether-Lumefantrine 80/480mg", "Antimalarial", 2500.00),
        ("Paracetamol 500mg", "Analgesic", 500.00),
        ("Amlodipine 10mg", "Antihypertensive", 1800.00),
        ("Metformin 500mg", "Antidiabetic", 2200.00),
        ("Amoxicillin-Clavulanate 625mg", "Antibiotic", 4500.00)
    ]
    
    pharmacy_orders = []
    for idx, row in df_encounters.sample(frac=0.70).iterrows():
        drug_info = drugs[np.random.randint(0, len(drugs))]
        qty = np.random.choice([1, 2, 3, 4], p=[0.5, 0.3, 0.15, 0.05])
        pharmacy_orders.append({
            "Order_ID": f"RX-NG-{20000 + idx}",
            "Encounter_ID": row["Encounter_ID"],
            "Hospital": row["Hospital"],
            "Date": row["Date"],
            "Drug_Name": drug_info[0],
            "Category": drug_info[1],
            "Quantity": qty,
            "Unit_Price": drug_info[2],
            "Is_Subsidized": True if row["Payer"] in ["Nasarawa Health Insurance Scheme (NASHIA)", "NHIA (Federal Sector)"] else False
        })
        
    df_pharmacy = pd.DataFrame(pharmacy_orders)
    
    # --- LABORATORY ORDERS DATAFRAME ---
    labs = ["Malaria RDT / Microscopy", "Full Blood Count (FBC)", "Fasting Blood Sugar (FBS)", "Widal Test", "Urinalysis"]
    
    lab_orders = []
    for idx, row in df_encounters.sample(frac=0.55).iterrows():
        test = np.random.choice(labs)
        tat = round(float(np.random.normal(loc=1.5, scale=0.4)), 1)
        tat = max(0.3, tat)
        status = np.random.choice(["Completed", "Pending"], p=[0.90, 0.10])
        
        lab_orders.append({
            "Lab_ID": f"LAB-NG-{30000 + idx}",
            "Encounter_ID": row["Encounter_ID"],
            "Hospital": row["Hospital"],
            "Date": row["Date"],
            "Test_Name": test,
            "Turnaround_Hours": tat,
            "Status": status
        })
        
    df_lab = pd.DataFrame(lab_orders)
    
    return df_encounters, df_pharmacy, df_lab
