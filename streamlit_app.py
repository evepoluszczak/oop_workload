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
    # Obtenir la date et l'heure actuelles pour les données
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
    return pd.DataFrame(data)

# --- Définitions des Catégories et Conversions ---
CATEGORIES = {
    "Électricité": "Énergie",
    "Gaz Naturel": "Énergie",
    "Gazole": "Carburant",
    "Essence": "Carburant",
    "Consommation d'eau": "Eau"
}

UNIT_CONVERSIONS = {
    "Énergie": {"MWh": 1, "kWh": 0.001, "GWh": 1000}, # Cible: MWh
    "Carburant": {"litres": 1, "gallons (US)": 3.78541}, # Cible: litres
    "Eau": {"m³": 1, "litres": 0.001} # Cible: m³
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

# --- Fonctions Utilitaires ---
def perform_conversion(value, unit, category):
    """Effectue la conversion d'unité vers le standard défini."""
    category_type = CATEGORIES[category]
    factor = UNIT_CONVERSIONS[category_type].get(unit, 1)
    standard_unit = list(UNIT_CONVERSIONS[category_type].keys())[0]
    
    # La conversion se fait en multipliant par le facteur pour atteindre l'unité cible
    # Par exemple, de kWh à MWh (cible), on multiplie par 0.001
    standard_value = value * factor
    return standard_value, standard_unit

def get_plausibility_check(record_to_check, full_data):
    """Vérifie la valeur de l'année précédente pour le même mois/site/catégorie."""
    previous_year_data = full_data[
        (full_data['location'] == record_to_check['location']) &
        (full_data['category'] == record_to_check['category']) &
        (full_data['month'] == record_to_check['month']) &
        (full_data['year'] == record_to_check['year'] - 1) &
        (full_data['status'] == 'Approuvé')
    ]
    if not previous_year_data.empty:
        previous_value = previous_year_data.iloc[0]['value_standardized']
        current_value = record_to_check['value_standardized']
        if previous_value == 0:
            return "N/A (valeur précédente nulle)", "info"
        
        diff = ((current_value - previous_value) / previous_value) * 100
        color = "error" if abs(diff) > 25 else "success" if abs(diff) < 10 else "warning"
        return f"{diff:+.1f}% vs. A-1", color
    return "Aucune donnée A-1", "info"

# --- Interface Utilisateur ---

# 1. Écran de Connexion
if not st.session_state.logged_in:
    st.title("Bienvenue sur le Portail de Suivi Énergétique 🌿")
    st.write("Veuillez vous identifier pour continuer.")

    username = st.selectbox("Sélectionnez votre nom d'utilisateur", list(USERS.keys()))
    
    if st.button("Se Connecter", type="primary"):
        st.session_state.logged_in = True
        st.session_state.user_info = USERS[username]
        st.session_state.username = username
        st.rerun()

# 2. Application Principale (après connexion)
else:
    user_info = st.session_state.user_info
    username = st.session_state.username
    role = user_info['role']

    # Barre latérale avec les informations utilisateur et la déconnexion
    with st.sidebar:
        st.header(f"Bienvenue, {username}")
        st.write(f"**Rôle:** {role}")
        if role == 'Employé de site':
            st.write(f"**Site:** {user_info['location']}")
        if role == 'Manager de division':
            st.write(f"**Division:** {user_info['division']}")
        
        if st.button("Se Déconnecter"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    # --- Vue pour les Employés de Site ---
    if role == 'Employé de site':
        st.title(f"📊 Saisie des données pour {user_info['location']}")
        
        st.info("ℹ️ **Comment ça marche ?** Entrez vos données de consommation mensuelles dans le formulaire ci-dessous. Elles seront ensuite envoyées à votre manager de division pour approbation.", icon="💡")

        with st.form("data_entry_form", clear_on_submit=True):
            st.header("Formulaire de saisie")
            
            c1, c2, c3 = st.columns(3)
            with c1:
                year = st.selectbox("Année", [datetime.now().year, datetime.now().year - 1], index=0)
            with c2:
                month = st.selectbox("Mois", range(1, 13), index=datetime.now().month - 1)
            with c3:
                category = st.selectbox("Catégorie", list(CATEGORIES.keys()))
            
            category_type = CATEGORIES[category]
            available_units = list(UNIT_CONVERSIONS[category_type].keys())

            c4, c5 = st.columns([2, 1])
            with c4:
                value = st.number_input("Valeur de consommation", min_value=0.0, format="%.2f")
            with c5:
                unit = st.selectbox("Unité", available_units)
            
            submitted = st.form_submit_button("Soumettre pour validation", type="primary")

            if submitted:
                # Vérifier si une entrée similaire existe déjà
                existing_entry = st.session_state.data[
                    (st.session_state.data['location'] == user_info['location']) &
                    (st.session_state.data['year'] == year) &
                    (st.session_state.data['month'] == month) &
                    (st.session_state.data['category'] == category)
                ]
                if not existing_entry.empty:
                    st.error(f"❌ Une entrée pour {category} en {month}/{year} existe déjà. Veuillez la modifier ou la supprimer si nécessaire.")
                else:
                    standard_value, standard_unit = perform_conversion(value, unit, category)
                    
                    new_id = st.session_state.data['id'].max() + 1 if not st.session_state.data.empty else 1
                    
                    new_data = pd.DataFrame([{
                        'id': new_id,
                        'location': user_info['location'],
                        'division': user_info['division'],
                        'year': year,
                        'month': month,
                        'category': category,
                        'value_input': value,
                        'unit_input': unit,
                        'value_standardized': standard_value,
                        'unit_standardized': standard_unit,
                        'status': 'En attente',
                        'submitted_by': username,
                        'approved_by': None,
                        'submission_date': pd.to_datetime('now')
                    }])
                    st.session_state.data = pd.concat([st.session_state.data, new_data], ignore_index=True)
                    st.success(f"✅ Données pour {category} soumises avec succès ! Valeur standardisée : {standard_value:.2f} {standard_unit}.")

        st.divider()
        st.header("Historique de vos saisies")
        
        location_data = st.session_state.data[st.session_state.data['location'] == user_info['location']].copy()
        location_data.sort_values(by=['year', 'month', 'submission_date'], ascending=False, inplace=True)
        
        if location_data.empty:
            st.write("Vous n'avez pas encore soumis de données.")
        else:
            st.dataframe(
                location_data[['year', 'month', 'category', 'value_input', 'unit_input', 'status']],
                use_container_width=True,
                hide_index=True
            )

    # --- Vue pour les Managers de Division ---
    elif role == 'Manager de division':
        st.title(f"📋 Validation des données pour la {user_info['division']}")

        pending_data = st.session_state.data[
            (st.session_state.data['division'] == user_info['division']) &
            (st.session_state.data['status'] == 'En attente')
        ].copy()

        st.header(f"Requêtes en attente ({len(pending_data)})")
        
        if pending_data.empty:
            st.success("🎉 Toutes les saisies sont à jour ! Aucun élément en attente de validation.")
        else:
            st.info("Examinez les saisies ci-dessous. La colonne 'Plausibilité' compare la valeur actuelle à celle du même mois de l'année précédente.", icon="🔍")
            for index, row in pending_data.iterrows():
                plausibility_text, color = get_plausibility_check(row, st.session_state.data)

                with st.container(border=True):
                    c1, c2, c3, c4 = st.columns([2, 3, 2, 2])
                    with c1:
                        st.write(f"**{row['location']}**")
                        st.caption(f"{row['month']}/{row['year']}")
                    with c2:
                        st.metric(
                            label=f"{row['category']} (standardisé)",
                            value=f"{row['value_standardized']:.2f} {row['unit_standardized']}",
                            help=f"Saisi : {row['value_input']} {row['unit_input']}"
                        )
                    with c3:
                        st.metric(
                            label="Plausibilité",
                            value=plausibility_text
                        )
                    
                    with c4:
                        st.write("") # Espace pour aligner les boutons
                        btn_c1, btn_c2 = st.columns(2)
                        with btn_c1:
                            if st.button("Approuver", key=f"approve_{row['id']}", type="primary", use_container_width=True):
                                st.session_state.data.loc[st.session_state.data['id'] == row['id'], 'status'] = 'Approuvé'
                                st.session_state.data.loc[st.session_state.data['id'] == row['id'], 'approved_by'] = username
                                st.toast(f"✅ Saisie de {row['location']} approuvée.", icon="👍")
                                st.rerun()
                        with btn_c2:
                            if st.button("Rejeter", key=f"reject_{row['id']}", use_container_width=True):
                                st.session_state.data.loc[st.session_state.data['id'] == row['id'], 'status'] = 'Rejeté'
                                st.session_state.data.loc[st.session_state.data['id'] == row['id'], 'approved_by'] = username
                                st.toast(f"❌ Saisie de {row['location']} rejetée.", icon="👎")
                                st.rerun()
        
        st.divider()
        st.header("📦 Export des données validées")
        st.write("Cette section permet de télécharger toutes les données approuvées pour les transférer vers votre base de données centrale ou Cozero.")

        approved_data = st.session_state.data[st.session_state.data['status'] == 'Approuvé'].copy()
        
        if approved_data.empty:
            st.warning("Aucune donnée approuvée n'est disponible pour l'export.")
        else:
            st.dataframe(approved_data, use_container_width=True, hide_index=True)
            
            csv = approved_data.to_csv(index=False).encode('utf-8')
            
            st.download_button(
                label="📥 Télécharger les données en CSV",
                data=csv,
                file_name="donnees_approuvees.csv",
                mime="text/csv",
                type="primary"
            )

    # --- Vue pour l'Administrateur (simple) ---
    elif role == 'Administrateur':
        st.title("Vue d'ensemble Administrateur")
        st.write("Toutes les données du système.")
        st.dataframe(st.session_state.data, use_container_width=True, hide_index=True)

