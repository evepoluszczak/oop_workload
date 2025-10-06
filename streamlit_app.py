import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(
    page_title="Portail de Suivi Carbone Liebherr",
    page_icon="🏗️",
    layout="wide"
)

# --- Mock Database (for demonstration purposes) ---
def initialize_database():
    """Creates a DataFrame to simulate a database with historical data."""
    now = datetime.now()
    current_year = now.year
    
    data = {
        'id': [1, 2, 3],
        'location': ['Site de Colmar (France)', 'Site de Newport News (USA)', 'Site de Toulouse (France)'],
        'division': ['Division Minière', 'Division Minière', 'Division Aéronautique'],
        'year': [current_year - 1, current_year - 1, current_year],
        'month': [np.nan, np.nan, np.nan],
        'category': ['Diesel B7 (on-road vehicle)', 'Gasoline E5 (on-road vehicle)', 'Leakage R134a'],
        'value_input': [12550, 8500, 15],
        'unit_input': ['liters', 'liters', 'kg'],
        'value_standardized': [12550, 8500, 15],
        'unit_standardized': ['liters', 'liters', 'kg'],
        'status': ['Approuvé', 'Approuvé', 'En attente'],
        'submitted_by': ['user_colmar', 'user_newport', 'user_toulouse'],
        'approved_by': ['manager_mining', 'manager_mining', None],
        'submission_date': [pd.to_datetime(now) - pd.DateOffset(years=1)] * 2 + [pd.to_datetime(now)]
    }
    df = pd.DataFrame(data)
    df['month'] = df['month'].astype('Float64')
    return df

# --- Category and Conversion Definitions ---
ANNUAL_CATEGORIES_CONFIG = {
    # Refrigerants
    "Fuite R134a": {"standard_unit": "kg", "units": {"kg": 1, "lbs": 0.453592}, "group": "Réfrigérants"},
    "Fuite R22": {"standard_unit": "kg", "units": {"kg": 1, "lbs": 0.453592}, "group": "Réfrigérants"},
    "Fuite R290": {"standard_unit": "kg", "units": {"kg": 1, "lbs": 0.453592}, "group": "Réfrigérants"},
    "Fuite R32": {"standard_unit": "kg", "units": {"kg": 1, "lbs": 0.453592}, "group": "Réfrigérants"},
    "Fuite R404a": {"standard_unit": "kg", "units": {"kg": 1, "lbs": 0.453592}, "group": "Réfrigérants"},
    "Fuite R407c": {"standard_unit": "kg", "units": {"kg": 1, "lbs": 0.453592}, "group": "Réfrigérants"},
    "Fuite R410a": {"standard_unit": "kg", "units": {"kg": 1, "lbs": 0.453592}, "group": "Réfrigérants"},
    "Fuite R507": {"standard_unit": "kg", "units": {"kg": 1, "lbs": 0.453592}, "group": "Réfrigérants"},
    "Fuite R508b": {"standard_unit": "kg", "units": {"kg": 1, "lbs": 0.453592}, "group": "Réfrigérants"},
    "Fuite R600": {"standard_unit": "kg", "units": {"kg": 1, "lbs": 0.453592}, "group": "Réfrigérants"},
    "Fuite R600a": {"standard_unit": "kg", "units": {"kg": 1, "lbs": 0.453592}, "group": "Réfrigérants"},
    # Vehicle Fuels
    "Gazole B0 (non routier)": {"standard_unit": "litres", "units": {"litres": 1, "gallons (US)": 3.78541}, "group": "Carburants Véhicules"},
    "Gazole B0 (routier)": {"standard_unit": "litres", "units": {"litres": 1, "gallons (US)": 3.78541}, "group": "Carburants Véhicules"},
    "Gazole B7 (non routier)": {"standard_unit": "litres", "units": {"litres": 1, "gallons (US)": 3.78541}, "group": "Carburants Véhicules"},
    "Gazole B7 (routier)": {"standard_unit": "litres", "units": {"litres": 1, "gallons (US)": 3.78541}, "group": "Carburants Véhicules"},
    "Gazole B30 (non routier)": {"standard_unit": "litres", "units": {"litres": 1, "gallons (US)": 3.78541}, "group": "Carburants Véhicules"},
    "Gazole B30 (routier)": {"standard_unit": "litres", "units": {"litres": 1, "gallons (US)": 3.78541}, "group": "Carburants Véhicules"},
    "Essence E5 (non routier)": {"standard_unit": "litres", "units": {"litres": 1, "gallons (US)": 3.78541}, "group": "Carburants Véhicules"},
    "Essence E5 (routier)": {"standard_unit": "litres", "units": {"litres": 1, "gallons (US)": 3.78541}, "group": "Carburants Véhicules"},
    "Essence E10 (non routier)": {"standard_unit": "litres", "units": {"litres": 1, "gallons (US)": 3.78541}, "group": "Carburants Véhicules"},
    "Essence E10 (routier)": {"standard_unit": "litres", "units": {"litres": 1, "gallons (US)": 3.78541}, "group": "Carburants Véhicules"},
    "Éthanol E100 (non routier)": {"standard_unit": "litres", "units": {"litres": 1, "gallons (US)": 3.78541}, "group": "Carburants Véhicules"},
    "Éthanol E100 (routier)": {"standard_unit": "litres", "units": {"litres": 1, "gallons (US)": 3.78541}, "group": "Carburants Véhicules"},
    "FAME / Gazole B100 (non routier)": {"standard_unit": "litres", "units": {"litres": 1, "gallons (US)": 3.78541}, "group": "Carburants Véhicules"},
    "FAME / Gazole B100 (routier)": {"standard_unit": "litres", "units": {"litres": 1, "gallons (US)": 3.78541}, "group": "Carburants Véhicules"},
    "HVO100 (non routier)": {"standard_unit": "litres", "units": {"litres": 1, "gallons (US)": 3.78541}, "group": "Carburants Véhicules"},
    "HVO100 (routier)": {"standard_unit": "litres", "units": {"litres": 1, "gallons (US)": 3.78541}, "group": "Carburants Véhicules"},
    "GPL (non routier)": {"standard_unit": "litres", "units": {"litres": 1, "gallons (US)": 3.78541}, "group": "Carburants Véhicules"},
    "GPL (routier)": {"standard_unit": "litres", "units": {"litres": 1, "gallons (US)": 3.78541}, "group": "Carburants Véhicules"},
    # Industrial Processes
    "Kérosène": {"standard_unit": "litres", "units": {"litres": 1, "gallons (US)": 3.78541}, "group": "Processus Industriels et Fabrication"},
    "Propane": {"standard_unit": "litres", "units": {"litres": 1, "gallons (US)": 3.78541, "kg": 1.96}, "group": "Processus Industriels et Fabrication"},
    "GNL - Gaz Naturel Liquéfié": {"standard_unit": "tonnes", "units": {"tonnes": 1, "m³": 0.45}, "group": "Processus Industriels et Fabrication"},
    "Acétylène": {"standard_unit": "kg", "units": {"kg": 1, "m³": 1.09}, "group": "Processus Industriels et Fabrication"},
    "Azote Liquide": {"standard_unit": "litres", "units": {"litres": 1}, "group": "Processus Industriels et Fabrication"},
    "Hydrogène gris": {"standard_unit": "kg", "units": {"kg": 1}, "group": "Processus Industriels et Fabrication"},
    "Hydrogène vert": {"standard_unit": "kg", "units": {"kg": 1}, "group": "Processus Industriels et Fabrication"},
    # Self-generated Energy
    "Électricité auto-générée (Renouvelable)": {"standard_unit": "MWh", "units": {"MWh": 1, "kWh": 0.001}, "group": "Énergie Auto-Générée"},
    "Électricité auto-générée (Non-renouvelable)": {"standard_unit": "MWh", "units": {"MWh": 1, "kWh": 0.001}, "group": "Énergie Auto-Générée"},
    "Chaleur auto-générée (Renouvelable)": {"standard_unit": "MWh", "units": {"MWh": 1, "kWh": 0.001}, "group": "Énergie Auto-Générée"},
    "Chaleur auto-générée (Non-renouvelable)": {"standard_unit": "MWh", "units": {"MWh": 1, "kWh": 0.001}, "group": "Énergie Auto-Générée"},
}

# --- Mock Users ---
USERS = {
    'user_colmar': {'role': 'Employé de site', 'location': 'Site de Colmar (France)', 'division': 'Division Minière'},
    'user_newport': {'role': 'Employé de site', 'location': 'Site de Newport News (USA)', 'division': 'Division Minière'},
    'user_toulouse': {'role': 'Employé de site', 'location': 'Site de Toulouse (France)', 'division': 'Division Aéronautique'},
    'manager_mining': {'role': 'Manager de division', 'division': 'Division Minière'},
    'manager_aero': {'role': 'Manager de division', 'division': 'Division Aéronautique'},
    'admin': {'role': 'Administrateur', 'division': 'Toutes'}
}

# --- Session State Initialization ---
if 'data' not in st.session_state: st.session_state.data = initialize_database()
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_info' not in st.session_state: st.session_state.user_info = None
if 'annual_config' not in st.session_state:
    st.session_state.annual_config = {
        'Site de Colmar (France)': ["Fuite R410a", "Gazole B7 (routier)"], 
        'Site de Newport News (USA)': ["Essence E5 (routier)"],
        'Site de Toulouse (France)': ["Fuite R134a", "Kérosène"]
    }

# --- Utility Functions ---
def perform_conversion(value, unit, category):
    """Performs unit conversion to the defined standard."""
    config = ANNUAL_CATEGORIES_CONFIG[category]
    factor = config["units"].get(unit, 1)
    standard_unit = config["standard_unit"]
    standard_value = value * factor
    return standard_value, standard_unit

def get_plausibility_check(record_to_check, full_data):
    """Checks the value from the previous year for the same site/category."""
    query = ((full_data['location'] == record_to_check['location']) &
             (full_data['category'] == record_to_check['category']) &
             (full_data['year'] == record_to_check['year'] - 1) &
             (full_data['status'] == 'Approuvé'))
    previous_year_data = full_data[query]

    if not previous_year_data.empty:
        previous_value = previous_year_data.iloc[0]['value_standardized']
        current_value = record_to_check['value_standardized']
        if previous_value == 0: return "N/A (A-1: 0)", "info"
        diff = ((current_value - previous_value) / previous_value) * 100
        return f"{diff:+.1f}% vs. A-1", "success" if abs(diff) < 10 else "warning" if abs(diff) <= 25 else "error"
    return "Pas de donnée A-1", "info"

# --- User Interface ---
if not st.session_state.logged_in:
    st.image("https://www.liebherr.com/external/layout/logo_liebherr.svg", width=300)
    st.title("Bienvenue sur le Portail de Suivi Carbone 🏗️")
    username = st.selectbox("Sélectionnez votre nom d'utilisateur", list(USERS.keys()))
    if st.button("Se Connecter", type="primary"):
        st.session_state.logged_in = True
        st.session_state.user_info = USERS[username]
        st.session_state.username = username
        st.rerun()
else:
    user_info = st.session_state.user_info
    username = st.session_state.username
    role = user_info['role']

    with st.sidebar:
        st.header(f"Bienvenue, {username}")
        st.write(f"**Rôle:** {role}")
        if role == 'Employé de site': st.write(f"**Site:** {user_info['location']}")
        if role == 'Manager de division': st.write(f"**Division:** {user_info['division']}")
        
        page_selection = "Aperçu"
        if role == 'Employé de site':
            page_selection = st.radio("Navigation", ["Configuration Annuelle", "Saisie Annuelle"])
        
        if st.button("Se Déconnecter"):
            for key in list(st.session_state.keys()): del st.session_state[key]
            st.rerun()

    if role == 'Employé de site':
        if page_selection == "Configuration Annuelle":
            st.title(f"⚙️ Configuration Annuelle pour {user_info['location']}")
            st.info("Activez les catégories pour lesquelles vous devez saisir des données une fois par an.")
            location = user_info['location']
            current_selection = st.session_state.annual_config.get(location, [])
            
            toggled_fields = []
            
            group_order = ["Réfrigérants", "Carburants Véhicules", "Processus Industriels et Fabrication", "Énergie Auto-Générée"]

            for group in group_order:
                with st.expander(group):
                    items_in_group = {item: config for item, config in ANNUAL_CATEGORIES_CONFIG.items() if config.get("group") == group}
                    
                    for field in items_in_group:
                        is_active = st.toggle(field, value=(field in current_selection), key=field)
                        if is_active:
                            toggled_fields.append(field)

            if st.button("Sauvegarder la Configuration", type="primary"):
                st.session_state.annual_config[location] = toggled_fields
                st.success("Configuration sauvegardée !")

        elif page_selection == "Saisie Annuelle":
            st.title(f"🗓️ Saisie Annuelle pour {user_info['location']}")
            active_fields = st.session_state.annual_config.get(user_info['location'], [])
            if not active_fields:
                st.warning("Aucun champ annuel n'est configuré. Allez à la page 'Configuration Annuelle' pour en sélectionner.")
            else:
                with st.form("annual_data_form"):
                    year = st.selectbox("Année de reporting", [datetime.now().year, datetime.now().year - 1], index=0)
                    st.divider()
                    
                    form_data = {}
                    for field in active_fields:
                        config = ANNUAL_CATEGORIES_CONFIG[field]
                        cols = st.columns([2, 1])
                        value = cols[0].number_input(f"{field}", min_value=0.0, format="%.2f", key=f"val_{field}")
                        unit = cols[1].selectbox("Unité", list(config["units"].keys()), key=f"unit_{field}")
                        form_data[field] = {'value': value, 'unit': unit}

                    if st.form_submit_button("Soumettre les Données Annuelles", type="primary"):
                        for category, data in form_data.items():
                            if data['value'] > 0:
                                std_val, std_unit = perform_conversion(data['value'], data['unit'], category)
                                new_id = st.session_state.data['id'].max() + 1 if not st.session_state.data.empty else 1
                                new_data = pd.DataFrame([{'id': new_id, 'location': user_info['location'], 'division': user_info['division'], 'year': year, 'month': np.nan, 'category': category, 'value_input': data['value'], 'unit_input': data['unit'], 'value_standardized': std_val, 'unit_standardized': std_unit, 'status': 'En attente', 'submitted_by': username, 'approved_by': None, 'submission_date': pd.to_datetime('now')}])
                                st.session_state.data = pd.concat([st.session_state.data, new_data], ignore_index=True)
                        st.success("Données annuelles soumises pour validation !")
                
                st.header("Historique des Soumissions")
                location_data = st.session_state.data[st.session_state.data['location'] == user_info['location']].copy()
                st.dataframe(location_data[['year', 'category', 'value_input', 'unit_input', 'status']].sort_values(by=['year'], ascending=False), hide_index=True, use_container_width=True)


    elif role == 'Manager de division':
        st.title(f"📋 Validation des Données pour la {user_info['division']}")
        pending_data = st.session_state.data[(st.session_state.data['division'] == user_info['division']) & (st.session_state.data['status'] == 'En attente')].copy()

        st.header(f"Demandes en attente ({len(pending_data)})")
        if pending_data.empty: st.success("🎉 Toutes les saisies sont à jour !")
        else:
            for index, row in pending_data.iterrows():
                plausibility_text, _ = get_plausibility_check(row, st.session_state.data)
                with st.container(border=True):
                    c1, c2, c3, c4 = st.columns([3, 3, 2, 2])
                    with c1:
                        st.write(f"**{row['location']}**")
                        st.caption(f"Année {row['year']}")
                    c2.metric(f"{row['category']}", f"{row['value_standardized']:.2f} {row['unit_standardized']}", help=f"Saisi: {row['value_input']} {row['unit_input']}")
                    c3.metric("Plausibilité", plausibility_text)
                    with c4:
                        st.write("") # Spacer for alignment
                        if c4.columns(2)[0].button("Approuver", key=f"approve_{row['id']}", type="primary", use_container_width=True):
                            st.session_state.data.loc[st.session_state.data['id'] == row['id'], ['status', 'approved_by']] = ['Approuvé', username]
                            st.rerun()
                        if c4.columns(2)[1].button("Rejeter", key=f"reject_{row['id']}", use_container_width=True):
                            st.session_state.data.loc[st.session_state.data['id'] == row['id'], ['status', 'approved_by']] = ['Rejeté', username]
                            st.rerun()
        
        st.divider()
        st.header("📦 Exporter les Données Validées")
        approved_data = st.session_state.data[st.session_state.data['status'] == 'Approuvé'].copy()
        if approved_data.empty: st.warning("Aucune donnée approuvée disponible.")
        else:
            st.dataframe(approved_data, use_container_width=True, hide_index=True)
            csv = approved_data.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Télécharger en CSV", csv, "donnees_approuvees_liebherr.csv", "text/csv", type="primary")
            
    elif role == 'Administrateur':
        st.title("Vue d'Ensemble Administrateur")
        st.dataframe(st.session_state.data, use_container_width=True, hide_index=True)

