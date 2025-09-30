import streamlit as st
import pandas as pd
import altair as alt
from datetime import date, timedelta

# ==============================================================================
# Configuration de la page Streamlit
# ==============================================================================
st.set_page_config(
    page_title="Tableau de Bord - Charge de Travail",
    page_icon="📊",
    layout="wide"
)

# ==============================================================================
# Fonctions de génération de données
# ==============================================================================

# Nous allons générer des données fictives pour la démonstration.
# Dans un cas réel, vous vous connecteriez à une base de données, un fichier Excel, etc.
@st.cache_data
def generate_mock_data():
    """Génère un DataFrame de données fictives pour 5 collaborateurs sur 30 jours."""
    collaborateurs = ["Alice", "Benoît", "Claire", "David", "Émilie"]
    types_tache = ["Projet A", "Projet B", "Support Client", "Réunion", "Formation", "Absence"]
    
    # Probabilités pour chaque type de tâche
    probabilites = [0.4, 0.3, 0.15, 0.1, 0.03, 0.02]
    
    today = date.today()
    data = []
    
    for i in range(30): # Données pour les 30 derniers jours
        current_date = today - timedelta(days=i)
        for collaborateur in collaborateurs:
            # Chaque collaborateur a entre 1 et 3 tâches par jour
            num_taches = pd.np.random.randint(1, 4)
            jour_heures = 0
            for _ in range(num_taches):
                if jour_heures < 8:
                    tache = pd.np.random.choice(types_tache, p=probabilites)
                    if tache == "Absence":
                        heures = 8
                        jour_heures = 8
                    else:
                        heures = pd.np.random.randint(1, 5)
                        if jour_heures + heures > 8:
                            heures = 8 - jour_heures
                        jour_heures += heures
                    
                    if heures > 0:
                        data.append([current_date, collaborateur, tache, heures])
    
    df = pd.DataFrame(data, columns=["Date", "Collaborateur", "Type de Tâche", "Heures"])
    df['Date'] = pd.to_datetime(df['Date'])
    return df

# Chargement des données
df = generate_mock_data()

# ==============================================================================
# Interface Utilisateur (Barre latérale pour les filtres)
# ==============================================================================
st.sidebar.header("Filtres")

# --- Filtre par date ---
min_date = df['Date'].min().date()
max_date = df['Date'].max().date()

date_range = st.sidebar.date_input(
    "Sélectionnez une période",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
    help="Filtrez les données pour une période spécifique."
)

# --- Filtre par collaborateur ---
all_collaborateurs = df['Collaborateur'].unique()
selected_collaborateurs = st.sidebar.multiselect(
    "Sélectionnez les collaborateurs",
    options=all_collaborateurs,
    default=all_collaborateurs,
    help="Choisissez les membres de l'équipe à afficher."
)

# --- Filtre par type de tâche ---
all_types_tache = df['Type de Tâche'].unique()
selected_types_tache = st.sidebar.multiselect(
    "Sélectionnez les types de tâches",
    options=all_types_tache,
    default=all_types_tache,
    help="Filtrez par activité (projets, réunions, absences...)."
)

# ==============================================================================
# Filtrage des données basé sur les sélections
# ==============================================================================

# La logique de filtrage doit gérer le cas où date_range n'a qu'une seule date
start_date, end_date = (pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])) if len(date_range) == 2 else (pd.to_datetime(date_range[0]), pd.to_datetime(date_range[0]))

filtered_df = df[
    (df['Date'] >= start_date) &
    (df['Date'] <= end_date) &
    (df['Collaborateur'].isin(selected_collaborateurs)) &
    (df['Type de Tâche'].isin(selected_types_tache))
]

# ==============================================================================
# Affichage principal du tableau de bord
# ==============================================================================
st.title("📊 Tableau de Bord de la Charge de Travail de l'Équipe")
st.markdown("---")

if filtered_df.empty:
    st.warning("Aucune donnée disponible pour les filtres sélectionnés. Veuillez élargir votre sélection.")
else:
    # --- Indicateurs Clés (KPIs) ---
    col1, col2, col3 = st.columns(3)
    total_heures = int(filtered_df['Heures'].sum())
    jours_absence = int(filtered_df[filtered_df['Type de Tâche'] == 'Absence']['Heures'].sum() / 8)
    jours_selectionnes = (end_date - start_date).days + 1
    
    col1.metric("Total Heures Travaillées", f"{total_heures} h")
    col2.metric("Jours d'Absence Cumulés", f"{jours_absence} j")
    col3.metric("Période Analysée", f"{jours_selectionnes} j")
    
    st.markdown("---")

    # --- Graphique : Charge de travail par collaborateur ---
    st.header("Charge de Travail par Collaborateur")
    
    workload_df = filtered_df.groupby('Collaborateur')['Heures'].sum().reset_index()
    
    # Calcul de la charge de travail théorique (ex: 8h/jour)
    jours_ouvrables = jours_selectionnes # Simplification, on pourrait retirer les weekends
    charge_theorique = jours_ouvrables * 8 * len(selected_collaborateurs) / len(all_collaborateurs) if all_collaborateurs else 0

    bar_chart = alt.Chart(workload_df).mark_bar().encode(
        x=alt.X('Collaborateur:N', sort='-y', title="Collaborateur"),
        y=alt.Y('Heures:Q', title="Heures cumulées"),
        color=alt.Color('Collaborateur:N', legend=None),
        tooltip=['Collaborateur', 'Heures']
    ).properties(
        height=400
    )
    
    # Ligne de charge moyenne
    rule = alt.Chart(pd.DataFrame({'y': [charge_theorique]})).mark_rule(color='red', strokeDash=[5,5]).encode(y='y')
    
    st.altair_chart(bar_chart + rule, use_container_width=True)
    st.info(f"La ligne rouge représente la charge de travail moyenne attendue pour la période ({charge_theorique:.0f} heures). Les barres dépassant cette ligne indiquent une surcharge potentielle.")

    # --- Graphiques en colonnes : Répartition des tâches ---
    col1_graph, col2_graph = st.columns(2)
    
    with col1_graph:
        st.header("Répartition par Type de Tâche")
        task_dist_df = filtered_df.groupby('Type de Tâche')['Heures'].sum().reset_index()
        pie_chart = alt.Chart(task_dist_df).mark_arc().encode(
            theta=alt.Theta(field="Heures", type="quantitative"),
            color=alt.Color(field="Type de Tâche", type="nominal", title="Type de Tâche"),
            tooltip=['Type de Tâche', 'Heures']
        ).properties(
             height=350
        )
        st.altair_chart(pie_chart, use_container_width=True)
    
    with col2_graph:
        st.header("Détail par Collaborateur et Tâche")
        stacked_bar = alt.Chart(filtered_df).mark_bar().encode(
            x=alt.X('Collaborateur:N', title=None),
            y=alt.Y('sum(Heures):Q', title="Heures"),
            color=alt.Color('Type de Tâche:N', title="Légende"),
            tooltip=['Collaborateur', 'Type de Tâche', 'sum(Heures)']
        ).properties(
             height=350
        )
        st.altair_chart(stacked_bar, use_container_width=True)

    # --- Affichage des données brutes ---
    with st.expander("Voir les données détaillées filtrées"):
        st.dataframe(filtered_df.sort_values(by="Date", ascending=False).style.format({"Date": "{:%d-%m-%Y}"}))
