import pandas as pd
from datetime import datetime, timedelta

def filter_data_by_duration(df, duration_option, custom_start=None, custom_end=None):
    """
    Standardized Duration Filter Engine.
    Filters any dataframe with a 'Date' column based on stakeholder selection.
    """
    if df.empty or 'Date' not in df.columns:
        return df

    max_date = df['Date'].max()
    
    if duration_option == "Last 7 Days (Weekly)":
        start_date = max_date - timedelta(days=7)
        return df[df['Date'] >= start_date]
        
    elif duration_option == "Last 30 Days (Monthly)":
        start_date = max_date - timedelta(days=30)
        return df[df['Date'] >= start_date]
        
    elif duration_option == "Last 90 Days (Quarterly)":
        start_date = max_date - timedelta(days=90)
        return df[df['Date'] >= start_date]
        
    elif duration_option == "Last 365 Days (Annually)":
        start_date = max_date - timedelta(days=365)
        return df[df['Date'] >= start_date]
        
    elif duration_option == "Full 2-Year Trend":
        return df
        
    elif duration_option == "Custom Date Range" and custom_start and custom_end:
        return df[(df['Date'] >= pd.to_datetime(custom_start)) & (df['Date'] <= pd.to_datetime(custom_end))]
        
    return df