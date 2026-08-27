import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime, timedelta

# TOGGLE THIS SWITCH WHEN ON-PREMISES CLOUD ACCESS IS PROVIDED
USE_LIVE_DATABASE = False  

@st.cache_data
def load_healthcare_data():
    """
    Decoupled Healthcare Data Architecture.
    Swaps between synthetic mock data and live database connectors seamlessly.
    """
    if USE_LIVE_DATABASE:
        return _fetch_live_cloud_data()
    else:
        return _generate_synthetic_data()

def _fetch_live_cloud_data():
    """
    Placeholder for live MongoDB / SQL cloud database connector.
    Uncomment and insert credentials once SHMC on-premises connection is verified.
    """
    # Example MongoDB Connection pattern:
    # from pymongo import MongoClient
    # client = MongoClient("mongodb://username:password@on-premises-cloud-ip:27017/")
    # db = client["shmc_healthcare_db"]
    # df_encounters = pd.DataFrame(list(db.encounters.find()))
    # df_pharmacy = pd.DataFrame(list(db.pharmacy.find()))
    # df_lab = pd.DataFrame(list(db.laboratory.find()))
    # return df_encounters, df_pharmacy, df_lab
    pass

def generate_synthetic_healthcare_data(num_records=1500):
    np.random.seed(42)
    
    end_date = datetime(2026, 8, 26)
    start_date = end_date - timedelta(days=730)
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    hospitals = [
        "State House Medical Center", 
        "Lafia Specialist Hospital", 
        "Keffi General Hospital", 
        "Akwanga General Hospital"
    ]
    
    departments = ["General Outpatient", "Pediatrics", "Obstetrics & Gynecology", "Accident & Emergency", "Internal Medicine"]
    pay_types = ["Nasarawa Health Insurance Scheme (NASHIA)", "NHIS", "Out-of-Pocket", "Private HMO"]
    
    diseases = [
        "Malaria (P. falciparum)", 
        "Acute Upper Respiratory Infection", 
        "Gastroenteritis / Diarrhea", 
        "Hepatitis B Surface Antigen (HBsAg)", 
        "Typhoid Fever", 
        "Hypertension / Cardiovascular", 
        "Lassa Fever (Suspected/Confirmed)", 
        "Dermatitis / Scabies"
    ]
    disease_weights = [0.48, 0.15, 0.12, 0.08, 0.07, 0.05, 0.02, 0.03]
    
    drugs_catalog = [
        {"name": "Artemether/Lumefantrine 80/480mg", "price": 1800, "category": "Antimalarial"},
        {"name": "Paracetamol 500mg Tabs", "price": 300, "category": "Analgesic"},
        {"name": "Amoxicillin/Clavulanate 625mg", "price": 3500, "category": "Antibiotic"},
        {"name": "Ciprofloxacin 500mg", "price": 1200, "category": "Antibiotic"},
        {"name": "Metformin 500mg", "price": 1500, "category": "Antidiabetic"},
        {"name": "Amlodipine 5mg", "price": 1000, "category": "Antihypertensive"}
    ]
    
    encounter_records = []
    pharmacy_records = []
    lab_records = []
    
    for single_date in date_range:
        is_rainy = single_date.month in [5, 6, 7, 8, 9, 10]
        
        for hosp in hospitals:
            daily_count = np.random.randint(50, 140)
            
            for _ in range(daily_count):
                weights = disease_weights.copy()
                if is_rainy:
                    weights[0] = 0.55  # Increase malaria weight
                    # Re-normalize weights so the sum strictly equals 1.0
                    total_w = sum(weights)
                    weights = [w / total_w for w in weights]
                
                diagnosis = np.random.choice(diseases, p=weights)
                payer = np.random.choice(pay_types, p=[0.45, 0.25, 0.20, 0.10])
                wait_time = max(10, int(np.random.normal(45, 15)))
                billing = np.random.choice([0, 1500, 3500, 8500, 25000], p=[0.25, 0.35, 0.25, 0.10, 0.05])
                
                encounter_records.append({
                    "Date": single_date,
                    "Hospital": hosp,
                    "Department": np.random.choice(departments),
                    "Diagnosis": diagnosis,
                    "Payer": payer,
                    "Wait_Time_Mins": wait_time,
                    "Billing_Amount": billing,
                    "EMR_Logged": np.random.choice([True, False], p=[0.88, 0.12])
                })
                
                if np.random.rand() < 0.70:
                    selected_drug = np.random.choice(drugs_catalog)
                    pharmacy_records.append({
                        "Date": single_date,
                        "Hospital": hosp,
                        "Drug_Name": selected_drug["name"],
                        "Category": selected_drug["category"],
                        "Quantity": np.random.randint(1, 4),
                        "Unit_Price": selected_drug["price"],
                        "Is_Subsidized": (payer in ["Nasarawa Health Insurance Scheme (NASHIA)", "NHIS"])
                    })
                
                if np.random.rand() < 0.50:
                    lab_records.append({
                        "Date": single_date,
                        "Hospital": hosp,
                        "Test_Name": "Malaria MP Microscopy" if diagnosis == "Malaria (P. falciparum)" else np.random.choice(["FBC", "Urinalysis", "LFT", "HBsAg Screening"]),
                        "Turnaround_Hours": round(np.random.uniform(0.5, 3.5), 1),
                        "Status": np.random.choice(["Completed", "Pending"], p=[0.94, 0.06])
                    })

    return pd.DataFrame(encounter_records), pd.DataFrame(pharmacy_records), pd.DataFrame(lab_records)
