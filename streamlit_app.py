import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(
    page_title="Energy Tracking Portal",
    page_icon="🌿",
    layout="wide"
)

# --- Mock Database (for demonstration purposes) ---
def initialize_database():
    """Creates a DataFrame to simulate a database with historical data."""
    now = datetime.now()
    current_year = now.year
    current_month = now.month
    previous_month = current_month - 1 if current_month > 1 else 12
    
    data = {
        'id': [1, 2, 3, 4, 5, 6],
        'location': ['Site Alpha', 'Site Alpha', 'Site Beta', 'Site Gamma', 'Site Gamma', 'Site Gamma'],
        'division': ['North Division', 'North Division', 'South Division', 'North Division', 'North Division', 'North Division'],
        'year': [current_year - 1, current_year - 1, current_year - 1, current_year - 1, current_year, current_year - 1],
        'month': [current_month, previous_month, current_month, current_month, previous_month, previous_month],
        'category': ['Purchased electricity (Bundled)', 'Diesel B7 (on-road vehicle)', 'Purchased electricity (Bundled)', 'Purchased electricity (Bundled)', 'Natural gas', 'Natural gas'],
        'value_input': [15000, 550, 22000, 8000, 1200, 1150],
        'unit_input': ['kWh', 'liters', 'kWh', 'kWh', 'm³', 'm³'],
        'value_standardized': [15, 550, 22, 8, 1200, 1150],
        'unit_standardized': ['MWh', 'liters', 'MWh', 'MWh', 'm³', 'm³'],
        'status': ['Approved', 'Approved', 'Approved', 'Approved', 'Pending', 'Approved'],
        'submitted_by': ['user_alpha', 'user_alpha', 'user_beta', 'user_gamma', 'user_gamma', 'user_gamma'],
        'approved_by': ['manager_north', 'manager_north', 'manager_south', 'manager_north', None, 'manager_north'],
        'submission_date': [pd.to_datetime(now) - pd.DateOffset(years=1)] * 4 + [pd.to_datetime(now)] + [pd.to_datetime(now) - pd.DateOffset(years=1)]
    }
    df = pd.DataFrame(data)
    df['month'] = df['month'].astype('Float64')
    return df

# --- Category and Conversion Definitions ---
MONTHLY_CATEGORIES = {
    "Purchased electricity (Bundled)": "Energy",
    "Purchased electricity (Unbundled)": "Energy",
    "Natural gas": "Energy",
    "Heating oil": "Fuel",
    "District heating": "Energy",
    "Diesel B0 (stationary combustion)": "Fuel",
    "Water": "Water",
}

ANNUAL_CATEGORIES_CONFIG = {
    # Refrigerants
    "Leakage R134a": {"standard_unit": "kg", "units": {"kg": 1, "lbs": 0.453592}, "group": "Refrigerants"},
    "Leakage R22": {"standard_unit": "kg", "units": {"kg": 1, "lbs": 0.453592}, "group": "Refrigerants"},
    "Leakage R290": {"standard_unit": "kg", "units": {"kg": 1, "lbs": 0.453592}, "group": "Refrigerants"},
    "Leakage R32": {"standard_unit": "kg", "units": {"kg": 1, "lbs": 0.453592}, "group": "Refrigerants"},
    "Leakage R404a": {"standard_unit": "kg", "units": {"kg": 1, "lbs": 0.453592}, "group": "Refrigerants"},
    "Leakage R407c": {"standard_unit": "kg", "units": {"kg": 1, "lbs": 0.453592}, "group": "Refrigerants"},
    "Leakage R410a": {"standard_unit": "kg", "units": {"kg": 1, "lbs": 0.453592}, "group": "Refrigerants"},
    "Leakage R507": {"standard_unit": "kg", "units": {"kg": 1, "lbs": 0.453592}, "group": "Refrigerants"},
    "Leakage R508b": {"standard_unit": "kg", "units": {"kg": 1, "lbs": 0.453592}, "group": "Refrigerants"},
    "Leakage R600": {"standard_unit": "kg", "units": {"kg": 1, "lbs": 0.453592}, "group": "Refrigerants"},
    "Leakage R600a": {"standard_unit": "kg", "units": {"kg": 1, "lbs": 0.453592}, "group": "Refrigerants"},
    # Vehicle Fuels
    "Diesel B0 (non-road vehicle)": {"standard_unit": "liters", "units": {"liters": 1, "gallons (US)": 3.78541}, "group": "Vehicle Fuels"},
    "Diesel B0 (on-road vehicle)": {"standard_unit": "liters", "units": {"liters": 1, "gallons (US)": 3.78541}, "group": "Vehicle Fuels"},
    "Diesel B7 (non-road vehicle)": {"standard_unit": "liters", "units": {"liters": 1, "gallons (US)": 3.78541}, "group": "Vehicle Fuels"},
    "Diesel B7 (on-road vehicle)": {"standard_unit": "liters", "units": {"liters": 1, "gallons (US)": 3.78541}, "group": "Vehicle Fuels"},
    "Diesel B30 (non-road vehicle)": {"standard_unit": "liters", "units": {"liters": 1, "gallons (US)": 3.78541}, "group": "Vehicle Fuels"},
    "Diesel B30 (on-road vehicle)": {"standard_unit": "liters", "units": {"liters": 1, "gallons (US)": 3.78541}, "group": "Vehicle Fuels"},
    "Gasoline E5 (non-road vehicle)": {"standard_unit": "liters", "units": {"liters": 1, "gallons (US)": 3.78541}, "group": "Vehicle Fuels"},
    "Gasoline E5 (on-road vehicle)": {"standard_unit": "liters", "units": {"liters": 1, "gallons (US)": 3.78541}, "group": "Vehicle Fuels"},
    "Gasoline E10 (non-road vehicle)": {"standard_unit": "liters", "units": {"liters": 1, "gallons (US)": 3.78541}, "group": "Vehicle Fuels"},
    "Gasoline E10 (on-road vehicle)": {"standard_unit": "liters", "units": {"liters": 1, "gallons (US)": 3.78541}, "group": "Vehicle Fuels"},
    "Ethanol E100 (non-road vehicle)": {"standard_unit": "liters", "units": {"liters": 1, "gallons (US)": 3.78541}, "group": "Vehicle Fuels"},
    "Ethanol E100 (on-road vehicle)": {"standard_unit": "liters", "units": {"liters": 1, "gallons (US)": 3.78541}, "group": "Vehicle Fuels"},
    "FAME / Diesel B100 (non-road vehicle)": {"standard_unit": "liters", "units": {"liters": 1, "gallons (US)": 3.78541}, "group": "Vehicle Fuels"},
    "FAME / Diesel B100 (on-road vehicle)": {"standard_unit": "liters", "units": {"liters": 1, "gallons (US)": 3.78541}, "group": "Vehicle Fuels"},
    "HVO100 (non-road vehicle)": {"standard_unit": "liters", "units": {"liters": 1, "gallons (US)": 3.78541}, "group": "Vehicle Fuels"},
    "HVO100 (on-road vehicle)": {"standard_unit": "liters", "units": {"liters": 1, "gallons (US)": 3.78541}, "group": "Vehicle Fuels"},
    "LPG - Liquefied propane gas (non-road vehicle)": {"standard_unit": "liters", "units": {"liters": 1, "gallons (US)": 3.78541}, "group": "Vehicle Fuels"},
    "LPG - Liquefied propane gas (on-road vehicle)": {"standard_unit": "liters", "units": {"liters": 1, "gallons (US)": 3.78541}, "group": "Vehicle Fuels"},
    # Other Fuels & Industrial Gases
    "Kerosene": {"standard_unit": "liters", "units": {"liters": 1, "gallons (US)": 3.78541}, "group": "Other Fuels & Industrial Gases"},
    "Propane": {"standard_unit": "liters", "units": {"liters": 1, "gallons (US)": 3.78541, "kg": 1.96}, "group": "Other Fuels & Industrial Gases"},
    "LNG - Liquefied natural gas": {"standard_unit": "tonnes", "units": {"tonnes": 1, "m³": 0.45}, "group": "Other Fuels & Industrial Gases"},
    "Acetylene": {"standard_unit": "kg", "units": {"kg": 1, "m³": 1.09}, "group": "Other Fuels & Industrial Gases"},
    "Liquid Nitrogen": {"standard_unit": "liters", "units": {"liters": 1}, "group": "Other Fuels & Industrial Gases"},
    "Grey hydrogen": {"standard_unit": "kg", "units": {"kg": 1}, "group": "Other Fuels & Industrial Gases"},
    "Green hydrogen": {"standard_unit": "kg", "units": {"kg": 1}, "group": "Other Fuels & Industrial Gases"},
    # Self-generated Energy
    "Self-generated electricity (Renewable)": {"standard_unit": "MWh", "units": {"MWh": 1, "kWh": 0.001}, "group": "Self-Generated Energy"},
    "Self-generated electricity (Non-Renewable)": {"standard_unit": "MWh", "units": {"MWh": 1, "kWh": 0.001}, "group": "Self-Generated Energy"},
    "Self-generated heat (Renewable)": {"standard_unit": "MWh", "units": {"MWh": 1, "kWh": 0.001}, "group": "Self-Generated Energy"},
    "Self-generated heat (Non-Renewable)": {"standard_unit": "MWh", "units": {"MWh": 1, "kWh": 0.001}, "group": "Self-Generated Energy"},
    # Agriculture
    "Beef cattle": {"standard_unit": "heads", "units": {"heads": 1}, "group": "Agriculture"},
}


UNIT_CONVERSIONS = {
    "Energy": {"MWh": 1, "kWh": 0.001, "GWh": 1000},
    "Fuel": {"liters": 1, "gallons (US)": 3.78541, "m³": 1000},
    "Water": {"m³": 1, "liters": 0.001}
}

# --- Mock Users ---
USERS = {
    'user_alpha': {'role': 'Site Employee', 'location': 'Site Alpha', 'division': 'North Division'},
    'user_beta': {'role': 'Site Employee', 'location': 'Site Beta', 'division': 'South Division'},
    'user_gamma': {'role': 'Site Employee', 'location': 'Site Gamma', 'division': 'North Division'},
    'manager_north': {'role': 'Division Manager', 'division': 'North Division'},
    'manager_south': {'role': 'Division Manager', 'division': 'South Division'},
    'admin': {'role': 'Administrator', 'division': 'All'}
}

# --- Session State Initialization ---
if 'data' not in st.session_state: st.session_state.data = initialize_database()
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_info' not in st.session_state: st.session_state.user_info = None
if 'annual_config' not in st.session_state:
    st.session_state.annual_config = {
        'Site Alpha': ["Leakage R410a", "Diesel B7 (on-road vehicle)"], 
        'Site Beta': ["Gasoline E5 (on-road vehicle)"],
        'Site Gamma': ["Leakage R134a", "Diesel B0 (non-road vehicle)"]
    }

# --- Utility Functions ---
def perform_conversion(value, unit, category, is_annual=False):
    """Performs unit conversion to the defined standard."""
    if is_annual:
        config = ANNUAL_CATEGORIES_CONFIG[category]
        factor = config["units"].get(unit, 1)
        standard_unit = config["standard_unit"]
        standard_value = value * factor
    else:
        category_type = MONTHLY_CATEGORIES[category]
        factor = UNIT_CONVERSIONS[category_type].get(unit, 1)
        standard_unit = list(UNIT_CONVERSIONS[category_type].keys())[0]
        standard_value = value * factor
    return standard_value, standard_unit

def get_plausibility_check(record_to_check, full_data):
    """Checks the value from the previous year for the same month/site/category."""
    is_annual = pd.isna(record_to_check['month'])
    query = ((full_data['location'] == record_to_check['location']) &
             (full_data['category'] == record_to_check['category']) &
             (full_data['year'] == record_to_check['year'] - 1) &
             (full_data['status'] == 'Approved'))
    query &= (pd.isna(full_data['month'])) if is_annual else (full_data['month'] == record_to_check['month'])
    previous_year_data = full_data[query]

    if not previous_year_data.empty:
        previous_value = previous_year_data.iloc[0]['value_standardized']
        current_value = record_to_check['value_standardized']
        if previous_value == 0: return "N/A (Prev. Year: 0)", "info"
        diff = ((current_value - previous_value) / previous_value) * 100
        return f"{diff:+.1f}% vs. Prev. Year", "success" if abs(diff) < 10 else "warning" if abs(diff) <= 25 else "error"
    return "No Prev. Year Data", "info"

# --- User Interface ---
if not st.session_state.logged_in:
    st.title("Welcome to the Energy Tracking Portal 🌿")
    username = st.selectbox("Select your username", list(USERS.keys()))
    if st.button("Log In", type="primary"):
        st.session_state.logged_in = True
        st.session_state.user_info = USERS[username]
        st.session_state.username = username
        st.rerun()
else:
    user_info = st.session_state.user_info
    username = st.session_state.username
    role = user_info['role']

    with st.sidebar:
        st.header(f"Welcome, {username}")
        st.write(f"**Role:** {role}")
        if role == 'Site Employee': st.write(f"**Site:** {user_info['location']}")
        if role == 'Division Manager': st.write(f"**Division:** {user_info['division']}")
        
        page_selection = "Overview"
        if role == 'Site Employee':
            page_selection = st.radio("Navigation", ["Monthly Entry", "Annual Entry", "Annual Configuration"])
        
        if st.button("Log Out"):
            for key in list(st.session_state.keys()): del st.session_state[key]
            st.rerun()

    if role == 'Site Employee':
        if page_selection == "Monthly Entry":
            st.title(f"📊 Monthly Data Entry for {user_info['location']}")
            with st.form("data_entry_form", clear_on_submit=True):
                c1, c2, c3 = st.columns(3)
                year = c1.selectbox("Year", [datetime.now().year, datetime.now().year - 1], index=0)
                month = c2.selectbox("Month", range(1, 13), index=datetime.now().month - 1)
                category = c3.selectbox("Category", list(MONTHLY_CATEGORIES.keys()))
                
                available_units = list(UNIT_CONVERSIONS[MONTHLY_CATEGORIES[category]].keys())
                c4, c5 = st.columns([2, 1])
                value = c4.number_input("Value", min_value=0.0, format="%.2f")
                unit = c5.selectbox("Unit", available_units)
                
                if st.form_submit_button("Submit", type="primary"):
                    std_val, std_unit = perform_conversion(value, unit, category)
                    new_id = st.session_state.data['id'].max() + 1 if not st.session_state.data.empty else 1
                    new_data = pd.DataFrame([{'id': new_id, 'location': user_info['location'], 'division': user_info['division'], 'year': year, 'month': float(month), 'category': category, 'value_input': value, 'unit_input': unit, 'value_standardized': std_val, 'unit_standardized': std_unit, 'status': 'Pending', 'submitted_by': username, 'approved_by': None, 'submission_date': pd.to_datetime('now')}])
                    st.session_state.data = pd.concat([st.session_state.data, new_data], ignore_index=True)
                    st.success(f"Data for {category} submitted successfully!")
            st.header("Submission History")
            location_data = st.session_state.data[st.session_state.data['location'] == user_info['location']].copy()
            st.dataframe(location_data[['year', 'month', 'category', 'value_input', 'unit_input', 'status']].sort_values(by=['year', 'month'], ascending=False), hide_index=True, use_container_width=True)

        elif page_selection == "Annual Configuration":
            st.title(f"⚙️ Annual Configuration for {user_info['location']}")
            st.info("Enable the categories for which you need to enter data once a year.")
            location = user_info['location']
            current_selection = st.session_state.annual_config.get(location, [])
            
            toggled_fields = []
            
            group_order = ["Refrigerants", "Vehicle Fuels", "Other Fuels & Industrial Gases", "Self-Generated Energy", "Agriculture"]

            for group in group_order:
                with st.expander(group):
                    items_in_group = {item: config for item, config in ANNUAL_CATEGORIES_CONFIG.items() if config.get("group") == group}
                    
                    for field in items_in_group:
                        is_active = st.toggle(field, value=(field in current_selection), key=field)
                        if is_active:
                            toggled_fields.append(field)

            if st.button("Save Configuration", type="primary"):
                st.session_state.annual_config[location] = toggled_fields
                st.success("Configuration saved!")

        elif page_selection == "Annual Entry":
            st.title(f"🗓️ Annual Data Entry for {user_info['location']}")
            active_fields = st.session_state.annual_config.get(user_info['location'], [])
            if not active_fields:
                st.warning("No annual fields are configured. Go to the 'Annual Configuration' page to select them.")
            else:
                with st.form("annual_data_form"):
                    year = st.selectbox("Reporting Year", [datetime.now().year, datetime.now().year - 1], index=0)
                    st.divider()
                    
                    form_data = {}
                    for field in active_fields:
                        config = ANNUAL_CATEGORIES_CONFIG[field]
                        cols = st.columns([2, 1])
                        value = cols[0].number_input(f"{field}", min_value=0.0, format="%.2f", key=f"val_{field}")
                        unit = cols[1].selectbox("Unit", list(config["units"].keys()), key=f"unit_{field}")
                        form_data[field] = {'value': value, 'unit': unit}

                    if st.form_submit_button("Submit Annual Data", type="primary"):
                        for category, data in form_data.items():
                            if data['value'] > 0:
                                std_val, std_unit = perform_conversion(data['value'], data['unit'], category, is_annual=True)
                                new_id = st.session_state.data['id'].max() + 1 if not st.session_state.data.empty else 1
                                new_data = pd.DataFrame([{'id': new_id, 'location': user_info['location'], 'division': user_info['division'], 'year': year, 'month': np.nan, 'category': category, 'value_input': data['value'], 'unit_input': data['unit'], 'value_standardized': std_val, 'unit_standardized': std_unit, 'status': 'Pending', 'submitted_by': username, 'approved_by': None, 'submission_date': pd.to_datetime('now')}])
                                st.session_state.data = pd.concat([st.session_state.data, new_data], ignore_index=True)
                        st.success("Annual data submitted for validation!")

    elif role == 'Division Manager':
        st.title(f"📋 Data Validation for {user_info['division']}")
        pending_data = st.session_state.data[(st.session_state.data['division'] == user_info['division']) & (st.session_state.data['status'] == 'Pending')].copy()

        st.header(f"Pending Requests ({len(pending_data)})")
        if pending_data.empty: st.success("🎉 All entries are up to date!")
        else:
            for index, row in pending_data.iterrows():
                plausibility_text, _ = get_plausibility_check(row, st.session_state.data)
                with st.container(border=True):
                    c1, c2, c3, c4 = st.columns([2, 3, 2, 2])
                    with c1:
                        st.write(f"**{row['location']}**")
                        caption = f"Year {row['year']}" if pd.isna(row['month']) else f"{int(row['month'])}/{row['year']}"
                        st.caption(caption)
                    c2.metric(f"{row['category']}", f"{row['value_standardized']:.2f} {row['unit_standardized']}", help=f"Input: {row['value_input']} {row['unit_input']}")
                    c3.metric("Plausibility", plausibility_text)
                    with c4:
                        st.write("") # Spacer for alignment
                        if c4.columns(2)[0].button("Approve", key=f"approve_{row['id']}", type="primary", use_container_width=True):
                            st.session_state.data.loc[st.session_state.data['id'] == row['id'], ['status', 'approved_by']] = ['Approved', username]
                            st.rerun()
                        if c4.columns(2)[1].button("Reject", key=f"reject_{row['id']}", use_container_width=True):
                            st.session_state.data.loc[st.session_state.data['id'] == row['id'], ['status', 'approved_by']] = ['Rejected', username]
                            st.rerun()
        
        st.divider()
        st.header("📦 Export Validated Data")
        approved_data = st.session_state.data[st.session_state.data['status'] == 'Approved'].copy()
        if approved_data.empty: st.warning("No approved data is available.")
        else:
            st.dataframe(approved_data, use_container_width=True, hide_index=True)
            csv = approved_data.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download as CSV", csv, "approved_data.csv", "text/csv", type="primary")
            
    elif role == 'Administrator':
        st.title("Administrator Overview")
        st.dataframe(st.session_state.data, use_container_width=True, hide_index=True)

