import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# --- Configuration de la Page ---
st.set_page_config(
    page_title="Portail de Suivi Énergétique",
    page_icon="🌿",
    layout="wide"
)

# --- Base de Données Fictive (pour la démonstration) ---
# Dans une application réelle, ceci serait remplacé par une connexion à une base de données (SQL, etc.)
def initialiser_la_base_de_donnees():
    """Crée un DataFrame pour simuler une base de données avec des données historiques."""
    now = datetime.now()
    annee_actuelle = now.year
    mois_actuel = now.month
    mois_precedent = mois_actuel - 1 if mois_actuel > 1 else 12
    annee_pour_mois_precedent = annee_actuelle if mois_actuel > 1 else annee_actuelle - 1

    data = {
        'id': [1, 2, 3, 4, 5, 6],
        'location': ['Site Alpha', 'Site Alpha', 'Site Bêta', 'Site Gamma', 'Site Gamma', 'Site Gamma'],
        'division': ['Division Nord', 'Division Nord', 'Division Sud', 'Division Nord', 'Division Nord', 'Division Nord'],
        'year': [annee_actuelle - 1, annee_actuelle - 1, annee_actuelle - 1, annee_actuelle - 1, annee_actuelle, annee_actuelle - 1],
        'month': [mois_actuel, mois_precedent, mois_actuel, mois_actuel, mois_precedent, mois_precedent],
        'category': ['Électricité', 'Gazole', 'Électricité', 'Électricité', 'Gaz Naturel', 'Gaz Naturel'],
        'value_input': [15000, 550, 22000, 8000, 1200, 1150],
        'unit_input': ['kWh', 'litres', 'kWh', 'kWh', 'm³', 'm³'],
        'value_standardized': [15, 550, 22, 8, 1200, 1150],
        'unit_standardized': ['MWh', 'litres', 'MWh', 'MWh', 'm³', 'm³'],
        'status': ['Approuvé', 'Approuvé', 'Approuvé', 'Approuvé', 'En attente', 'Approuvé'],
        'submitted_by': ['user_alpha', 'user_alpha', 'user_beta', 'user_gamma', 'user_gamma', 'user_gamma'],
        'approved_by': ['manager_nord', 'manager_nord', 'manager_sud', 'manager_nord', None, 'manager_nord'],
        'submission_date': [pd.to_datetime(now) - pd.DateOffset(years=1)] * 4 + [pd.to_datetime(now)] + [pd.to_datetime(now) - pd.DateOffset(years=1)]
    }
    df = pd.DataFrame(data)
    # S'assurer que 'month' peut contenir des NaN
    df['month'] = df['month'].astype('Float64')
    return df

# --- Définitions des Catégories et Conversions ---
CATEGORIES_MENSUELLES = {
    "Électricité": "Énergie",
    "Gaz Naturel": "Énergie",
    "Gazole": "Carburant",
    "Essence": "Carburant",
    "Consommation d'eau": "Eau"
}

ANNUAL_CATEGORIES = {
    "Réfrigérants (R410a)": "kg",
    "Extincteurs (CO2)": "kg",
    "Déchets (Papier)": "tonnes",
    "Déchets (Plastique)": "tonnes",
    "Flotte de véhicules (Diesel)": "litres",
    "Huiles usagées": "litres",
}

UNIT_CONVERSIONS = {
    "Énergie": {"MWh": 1, "kWh": 0.001, "GWh": 1000},
    "Carburant": {"litres": 1, "gallons (US)": 3.78541},
    "Eau": {"m³": 1, "litres": 0.001}
}

# --- Utilisateurs Fictifs (pour la démonstration) ---
USERS = {
    'user_alpha': {'role': 'Employé de site', 'location': 'Site Alpha', 'division': 'Division Nord'},
    'user_beta': {'role': 'Employé de site', 'location': 'Site Bêta', 'division': 'Division Sud'},
    'user_gamma': {'role': 'Employé de site', 'location': 'Site Gamma', 'division': 'Division Nord'},
    'manager_nord': {'role': 'Manager de division', 'division': 'Division Nord'},
    'manager_sud': {'role': 'Manager de division', 'division': 'Division Sud'},
    'admin': {'role': 'Administrateur', 'division': 'Toutes'}
}
LOCATIONS = sorted(['Site Alpha', 'Site Bêta', 'Site Gamma'] + [f"Site {i}" for i in range(4, 201)])

# --- Initialisation de l'état de la session ---
if 'data' not in st.session_state:
    st.session_state.data = initialiser_la_base_de_donnees()
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_info' not in st.session_state:
    st.session_state.user_info = None
if 'annual_config' not in st.session_state:
    st.session_state.annual_config = {
        'Site Alpha': ["Réfrigérants (R410a)", "Déchets (Papier)"],
        'Site Bêta': ["Déchets (Plastique)"],
        'Site Gamma': ["Réfrigérants (R410a)", "Extincteurs (CO2)", "Flotte de véhicules (Diesel)"]
    }

# --- Fonctions Utilitaires ---
def perform_conversion(value, unit, category):
    category_type = CATEGORIES_MENSUELLES[category]
    factor = UNIT_CONVERSIONS[category_type].get(unit, 1)
    standard_unit = list(UNIT_CONVERSIONS[category_type].keys())[0]
    standard_value = value * factor
    return standard_value, standard_unit

def get_plausibility_check(record_to_check, full_data):
    is_annual = pd.isna(record_to_check['month'])
    
    query = (
        (full_data['location'] == record_to_check['location']) &
        (full_data['category'] == record_to_check['category']) &
        (full_data['year'] == record_to_check['year'] - 1) &
        (full_data['status'] == 'Approuvé')
    )
    if is_annual:
        query &= (pd.isna(full_data['month']))
    else:
        query &= (full_data['month'] == record_to_check['month'])

    previous_year_data = full_data[query]

    if not previous_year_data.empty:
        previous_value = previous_year_data.iloc[0]['value_standardized']
        current_value = record_to_check['value_standardized']
        if previous_value == 0: return "N/A (A-1: 0)", "info"
        
        diff = ((current_value - previous_value) / previous_value) * 100
        return f"{diff:+.1f}% vs. A-1", "success" if abs(diff) < 10 else "warning" if abs(diff) <= 25 else "error"
    return "Aucune donnée A-1", "info"

# --- Interface Utilisateur ---
if not st.session_state.logged_in:
    st.title("Bienvenue sur le Portail de Suivi Énergétique 🌿")
    st.write("Veuillez vous identifier pour continuer.")
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
            page_selection = st.radio("Navigation", ["Saisie Mensuelle", "Saisie Annuelle", "Configuration Annuelle"])
        
        if st.button("Se Déconnecter"):
            for key in list(st.session_state.keys()): del st.session_state[key]
            st.rerun()

    # --- Vues pour les Employés de Site ---
    if role == 'Employé de site':
        if page_selection == "Saisie Mensuelle":
            st.title(f"📊 Saisie Mensuelle pour {user_info['location']}")
            with st.form("data_entry_form", clear_on_submit=True):
                c1, c2, c3 = st.columns(3)
                year = c1.selectbox("Année", [datetime.now().year, datetime.now().year - 1], index=0)
                month = c2.selectbox("Mois", range(1, 13), index=datetime.now().month - 1)
                category = c3.selectbox("Catégorie", list(CATEGORIES_MENSUELLES.keys()))
                
                category_type = CATEGORIES_MENSUELLES[category]
                available_units = list(UNIT_CONVERSIONS[category_type].keys())
                c4, c5 = st.columns([2, 1])
                value = c4.number_input("Valeur", min_value=0.0, format="%.2f")
                unit = c5.selectbox("Unité", available_units)
                
                if st.form_submit_button("Soumettre", type="primary"):
                    standard_value, standard_unit = perform_conversion(value, unit, category)
                    new_id = st.session_state.data['id'].max() + 1
                    new_data = pd.DataFrame([{'id': new_id, 'location': user_info['location'], 'division': user_info['division'], 'year': year, 'month': float(month), 'category': category, 'value_input': value, 'unit_input': unit, 'value_standardized': standard_value, 'unit_standardized': standard_unit, 'status': 'En attente', 'submitted_by': username, 'approved_by': None, 'submission_date': pd.to_datetime('now')}])
                    st.session_state.data = pd.concat([st.session_state.data, new_data], ignore_index=True)
                    st.success(f"Données pour {category} soumises avec succès !")
            st.header("Historique des saisies")
            location_data = st.session_state.data[st.session_state.data['location'] == user_info['location']].copy()
            st.dataframe(location_data[['year', 'month', 'category', 'value_input', 'unit_input', 'status']].sort_values(by=['year', 'month'], ascending=False), hide_index=True, use_container_width=True)

        elif page_selection == "Configuration Annuelle":
            st.title(f"⚙️ Configuration Annuelle pour {user_info['location']}")
            st.info("Cochez toutes les catégories pour lesquelles vous devez saisir des données une fois par an. Cette sélection peut être modifiée à tout moment.")
            location = user_info['location']
            current_selection = st.session_state.annual_config.get(location, [])
            
            new_selection = st.multiselect(
                "Sélectionnez les champs annuels pertinents pour votre site :",
                options=list(ANNUAL_CATEGORIES.keys()),
                default=current_selection
            )
            if st.button("Sauvegarder la configuration", type="primary"):
                st.session_state.annual_config[location] = new_selection
                st.success("Configuration sauvegardée !")

        elif page_selection == "Saisie Annuelle":
            st.title(f"🗓️ Saisie Annuelle pour {user_info['location']}")
            active_fields = st.session_state.annual_config.get(user_info['location'], [])
            if not active_fields:
                st.warning("Aucun champ annuel n'est configuré. Allez à la page 'Configuration Annuelle' pour en sélectionner.")
            else:
                with st.form("annual_data_form"):
                    st.info(f"Veuillez remplir les valeurs pour les {len(active_fields)} champs configurés pour votre site.")
                    year = st.selectbox("Année de déclaration", [datetime.now().year, datetime.now().year - 1], index=0)
                    st.divider()
                    
                    entered_values = {}
                    for field in active_fields:
                        unit = ANNUAL_CATEGORIES[field]
                        entered_values[field] = st.number_input(f"{field} ({unit})", min_value=0.0, format="%.2f")

                    if st.form_submit_button("Soumettre les données annuelles", type="primary"):
                        for category, value in entered_values.items():
                            if value > 0:
                                new_id = st.session_state.data['id'].max() + 1
                                unit = ANNUAL_CATEGORIES[category]
                                new_data = pd.DataFrame([{'id': new_id, 'location': user_info['location'], 'division': user_info['division'], 'year': year, 'month': np.nan, 'category': category, 'value_input': value, 'unit_input': unit, 'value_standardized': value, 'unit_standardized': unit, 'status': 'En attente', 'submitted_by': username, 'approved_by': None, 'submission_date': pd.to_datetime('now')}])
                                st.session_state.data = pd.concat([st.session_state.data, new_data], ignore_index=True)
                        st.success("Données annuelles soumises pour validation !")

    # --- Vue pour les Managers de Division ---
    elif role == 'Manager de division':
        st.title(f"📋 Validation des données pour la {user_info['division']}")
        pending_data = st.session_state.data[(st.session_state.data['division'] == user_info['division']) & (st.session_state.data['status'] == 'En attente')].copy()

        st.header(f"Requêtes en attente ({len(pending_data)})")
        if pending_data.empty: st.success("🎉 Toutes les saisies sont à jour !")
        else:
            for index, row in pending_data.iterrows():
                plausibility_text, _ = get_plausibility_check(row, st.session_state.data)
                with st.container(border=True):
                    c1, c2, c3, c4 = st.columns([2, 3, 2, 2])
                    with c1:
                        st.write(f"**{row['location']}**")
                        caption = f"Année {row['year']}" if pd.isna(row['month']) else f"{int(row['month'])}/{row['year']}"
                        st.caption(caption)
                    c2.metric(f"{row['category']}", f"{row['value_standardized']:.2f} {row['unit_standardized']}", help=f"Saisi: {row['value_input']} {row['unit_input']}")
                    c3.metric("Plausibilité", plausibility_text)
                    with c4:
                        st.write("")
                        if c4.columns(2)[0].button("Approuver", key=f"approve_{row['id']}", type="primary", use_container_width=True):
                            st.session_state.data.loc[st.session_state.data['id'] == row['id'], ['status', 'approved_by']] = ['Approuvé', username]
                            st.rerun()
                        if c4.columns(2)[1].button("Rejeter", key=f"reject_{row['id']}", use_container_width=True):
                            st.session_state.data.loc[st.session_state.data['id'] == row['id'], ['status', 'approved_by']] = ['Rejeté', username]
                            st.rerun()
        
        st.divider()
        st.header("📦 Export des données validées")
        approved_data = st.session_state.data[st.session_state.data['status'] == 'Approuvé'].copy()
        if approved_data.empty: st.warning("Aucune donnée approuvée n'est disponible.")
        else:
            st.dataframe(approved_data, use_container_width=True, hide_index=True)
            csv = approved_data.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Télécharger en CSV", csv, "donnees_approuvees.csv", "text/csv", type="primary")

    # --- Vue pour l'Administrateur ---
    elif role == 'Administrateur':
        st.title("Vue d'ensemble Administrateur")
        st.dataframe(st.session_state.data, use_container_width=True, hide_index=True)

