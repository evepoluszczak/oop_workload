import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from datetime import timedelta, datetime
import io

# ==============================================================================
# Configuration de la page Streamlit
# ==============================================================================
st.set_page_config(
    page_title="Tableau de Bord - Charge de Travail",
    page_icon="📊",
    layout="wide"
)

# ==============================================================================
# Fonction de chargement et de traitement des données
# ==============================================================================
@st.cache_data
def get_and_process_data():
    """
    Génère un DataFrame basé sur la structure du fichier Excel, puis le transforme
    en un format "tidy" (long) utilisable pour les graphiques.
    """
    # Données brutes simulant le fichier CSV.
    # Dans une application réelle, cela pourrait venir d'une base de données.
    # CORRECTION : Les guillemets dans les noms de projet ont été corrigés pour éviter les erreurs de syntaxe.
    raw_data = """
,,,,,,,2025-01-01,2025-01-06,2025-01-13,2025-01-20,2025-01-27,2025-02-03
Anita,,Congé,,Congé,,,,100,100,0,0,0,0
,,Temps Partiel,,Temps Partiel,,,,20,20,20,20,20,20
,,Département A,,POC,,"New POC ""Red""",,20,30,40,0,0,0
,,Département A,,Projet,,"New Projet ""Green""",,10,50,40,0,0,0
Eve,,Support,,Support,,,,80,80,80,80,80,80
,,Département B,,Projet,,"New Milk Report",,20,20,20,20,20,20
Bruno,,Congé,,Congé,,,,0,0,0,100,100,0
,,Département C,,POC,,"New POC ""Blue""",,60,60,60,0,0,60
,,Département A,,Support,,Support,,,,40,40,40,0,0,40
Florian,,Support,,Support,,,,100,100,100,100,100,100
Joss,,Département B,,Projet,,"New Projet ""Orange""",,50,50,0,0,0,0
,,Département A,,Projet,,"New Projet ""Yellow""",,50,50,100,100,100,100
Sébastien,,Temps Partiel,,Temps Partiel,,,,20,20,20,20,20,20
,,Support,,Support,,,,80,80,80,80,80,80
"""

    try:
        # Utiliser io.StringIO pour lire la chaîne de caractères comme un fichier
        df = pd.read_csv(io.StringIO(raw_data), header=None)
        
        # 1. La ligne de date est la première ligne (index 0)
        date_row_index = 0
        
        # 2. Extraire les en-têtes de date et les données brutes
        date_headers = pd.to_datetime(df.iloc[date_row_index], errors='coerce')
        df_data = df.iloc[date_row_index + 1:].copy()
        
        # 3. Identifier les colonnes de métadonnées et de dates
        first_date_col_index = date_headers.first_valid_index()
        meta_cols = {0: 'Employé', 2: 'Projet', 4: 'Tâche'}
        
        # 4. Construire un DataFrame propre avec les bonnes colonnes
        df_clean = df_data[list(meta_cols.keys())].copy()
        df_clean.columns = list(meta_cols.values())
        
        df_dates = df_data.iloc[:, first_date_col_index:]
        df_dates.columns = date_headers[first_date_col_index:]
        
        df_full = pd.concat([df_clean, df_dates], axis=1)

        # 5. Remplir les informations manquantes (Employé, Projet)
        df_full['Employé'] = df_full['Employé'].replace(['', ' ', np.nan]).ffill()
        df_full['Projet'] = df_full['Projet'].replace(['', ' ', np.nan]).ffill()
        
        # 6. Supprimer les lignes non pertinentes
        df_full.dropna(subset=['Tâche'], inplace=True)
        df_full = df_full[~df_full['Tâche'].astype(str).str.contains('total', case=False, na=False)]
        
        # 7. Pivoter les données (Melt) pour passer au format long
        id_vars = ['Employé', 'Projet', 'Tâche']
        df_long = pd.melt(df_full, id_vars=id_vars, var_name='Date', value_name='Pourcentage')

        # 8. Nettoyage final
        df_long.dropna(subset=['Pourcentage'], inplace=True)
        df_long['Pourcentage'] = pd.to_numeric(df_long['Pourcentage'], errors='coerce').fillna(0)
        df_long = df_long[df_long['Pourcentage'] > 0]

        # 9. Conversion des pourcentages en jours (100% = 5 jours, donc 20% = 1 jour)
        df_long['Jours'] = df_long['Pourcentage'] / 20.0
        
        # 10. Créer une colonne de tâche plus descriptive
        df_long['Type de Tâche'] = df_long['Projet'] + " - " + df_long['Tâche']
        
        # 11. Sélectionner et renommer les colonnes finales
        df_final = df_long[['Date', 'Employé', 'Type de Tâche', 'Jours']].copy()
        df_final.rename(columns={'Employé': 'Collaborateur'}, inplace=True)
        df_final['Date'] = pd.to_datetime(df_final['Date'])
        
        return df_final

    except Exception as e:
        st.error(f"Une erreur est survenue lors du traitement des données : {e}")
        return pd.DataFrame()

# ==============================================================================
# Interface Principale
# ==============================================================================
st.title("📊 Tableau de Bord de la Charge de Travail de l'Équipe")
st.markdown("Utilisez cette application pour visualiser la planification et équilibrer la charge de travail.")

# --- Chargement et traitement des données intégrées ---
df = get_and_process_data()

if df.empty:
    st.error("Impossible de charger les données. Le format interne pourrait être incorrect.")
else:
    # ==============================================================================
    # Barre latérale pour les filtres
    # ==============================================================================
    st.sidebar.header("Filtres")
    min_date = df['Date'].min().date()
    max_date = df['Date'].max().date()

    date_range = st.sidebar.date_input(
        "Sélectionnez une période",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    all_collaborateurs = sorted(df['Collaborateur'].unique())
    selected_collaborateurs = st.sidebar.multiselect(
        "Sélectionnez les collaborateurs",
        options=all_collaborateurs,
        default=all_collaborateurs
    )
    
    # Créer un filtre par projet/catégorie principale
    df['Projet'] = df['Type de Tâche'].apply(lambda x: x.split(' - ')[0])
    all_projets = sorted(df['Projet'].unique())
    selected_projets = st.sidebar.multiselect(
        "Sélectionnez les projets/catégories",
        options=all_projets,
        default=all_projets
    )


    # ==============================================================================
    # Filtrage des données
    # ==============================================================================
    start_date, end_date = (pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])) if len(date_range) == 2 else (pd.to_datetime(date_range[0]), pd.to_datetime(date_range[0]))

    filtered_df = df[
        (df['Date'] >= start_date) &
        (df['Date'] <= end_date) &
        (df['Collaborateur'].isin(selected_collaborateurs)) &
        (df['Projet'].isin(selected_projets))
    ]

    # ==============================================================================
    # Affichage du tableau de bord
    # ==============================================================================
    if filtered_df.empty:
        st.warning("Aucune donnée disponible pour les filtres sélectionnés.")
    else:
        st.markdown("---")
        # --- KPIs ---
        col1, col2, col3 = st.columns(3)
        total_jours = filtered_df['Jours'].sum()
        jours_absence = filtered_df[filtered_df['Projet'].str.contains('Congé|Absence|Férié|Temps Partiel', case=False)]['Jours'].sum()
        jours_selectionnes = (end_date - start_date).days + 1
        
        col1.metric("Total Jours Planifiés", f"{total_jours:.1f} j")
        col2.metric("Jours d'Absence (Congés, etc.)", f"{jours_absence:.1f} j")
        col3.metric("Période Analysée", f"{jours_selectionnes} j")
        
        st.markdown("---")

        # --- Graphique : Charge par collaborateur ---
        st.header("Charge de Travail par Collaborateur")
        workload_df = filtered_df.groupby('Collaborateur')['Jours'].sum().reset_index()
        
        # Calcul de la charge théorique (jours ouvrables dans la période)
        jours_ouvrables = np.busday_count(start_date.date(), (end_date + timedelta(days=1)).date())

        bar_chart = alt.Chart(workload_df).mark_bar().encode(
            x=alt.X('Collaborateur:N', sort='-y', title="Collaborateur"),
            y=alt.Y('Jours:Q', title="Jours planifiés cumulés"),
            color=alt.Color('Collaborateur:N', legend=None),
            tooltip=['Collaborateur', alt.Tooltip('Jours:Q', format='.1f')]
        ).properties(height=400)
        
        rule = alt.Chart(pd.DataFrame({'y': [jours_ouvrables]})).mark_rule(color='red', strokeDash=[5,5]).encode(y='y')
        
        st.altair_chart(bar_chart + rule, use_container_width=True)
        st.info(f"La ligne rouge représente la capacité théorique pour la période ({jours_ouvrables} jours ouvrables). Les barres dépassant cette ligne indiquent une surcharge potentielle.")

        # --- Graphiques de répartition ---
        col1_graph, col2_graph = st.columns(2)
        
        with col1_graph:
            st.header("Répartition par Projet/Catégorie")
            task_dist_df = filtered_df.groupby('Projet')['Jours'].sum().reset_index()
            pie_chart = alt.Chart(task_dist_df).mark_arc(innerRadius=50).encode(
                theta=alt.Theta(field="Jours", type="quantitative"),
                color=alt.Color(field="Projet", type="nominal", title="Catégorie"),
                tooltip=['Projet', alt.Tooltip('Jours:Q', format='.1f')]
            ).properties(height=350)
            st.altair_chart(pie_chart, use_container_width=True)
        
        with col2_graph:
            st.header("Détail par Collaborateur et Projet")
            stacked_bar = alt.Chart(filtered_df).mark_bar().encode(
                x=alt.X('Collaborateur:N', title=None),
                y=alt.Y('sum(Jours):Q', title="Jours"),
                color=alt.Color('Projet:N', title="Légende"),
                tooltip=['Collaborateur', 'Projet', alt.Tooltip('sum(Jours):Q', format='.1f')]
            ).properties(height=350)
            st.altair_chart(stacked_bar, use_container_width=True)

        # --- Données brutes ---
        with st.expander("Voir les données détaillées filtrées"):
            display_df = filtered_df[['Date', 'Collaborateur', 'Type de Tâche', 'Jours']].copy()
            st.dataframe(display_df.sort_values(by="Date", ascending=False).style.format({"Date": "{:%d-%m-%Y}", "Jours": "{:.2f}"}))

