import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
from dotenv import load_dotenv
import os

# Chargement des variables d'environnement
load_dotenv()

# Configuration de la page
st.set_page_config(
    page_title="Dashboard TheKnowHow.ae",
    page_icon="🏥",
    layout="wide"
)

# Fonction pour se connecter à la base de données
def get_db_connection():
    return sqlite3.connect(os.getenv("DB_PATH"))

# Fonction pour charger les données
def load_data():
    conn = get_db_connection()
    conversations_df = pd.read_sql_query("""
        SELECT 
            id,
            user_id,
            timestamp,
            message,
            response,
            language,
            medical_category,
            urgency_level
        FROM conversations
    """, conn)
    conn.close()
    return conversations_df

# Titre principal
st.title("Dashboard TheKnowHow.ae")

# Chargement des données
df = load_data()

# Métriques principales
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Conversations", len(df))
with col2:
    st.metric("Conversations Aujourd'hui", len(df[df['timestamp'].dt.date == datetime.now().date()]))
with col3:
    st.metric("Langues Supportées", len(df['language'].unique()))

# Graphiques
st.subheader("Statistiques des Conversations")
col1, col2 = st.columns(2)

with col1:
    # Conversations par langue
    lang_counts = df['language'].value_counts()
    fig_lang = px.pie(values=lang_counts.values, names=lang_counts.index, title="Conversations par Langue")
    st.plotly_chart(fig_lang)

with col2:
    # Conversations par jour
    daily_counts = df.groupby(df['timestamp'].dt.date).size()
    fig_daily = px.line(x=daily_counts.index, y=daily_counts.values, title="Conversations par Jour")
    st.plotly_chart(fig_daily)

# Table des conversations récentes
st.subheader("Conversations Récentes")
recent_conversations = df.sort_values('timestamp', ascending=False).head(10)
st.dataframe(recent_conversations)

# Filtres
st.sidebar.title("Filtres")
selected_language = st.sidebar.multiselect(
    "Langue",
    options=df['language'].unique(),
    default=df['language'].unique()
)

selected_date = st.sidebar.date_input(
    "Date",
    value=(datetime.now() - timedelta(days=7), datetime.now()),
    max_value=datetime.now()
)

# Export des données
if st.sidebar.button("Exporter les données"):
    csv = df.to_csv(index=False)
    st.sidebar.download_button(
        label="Télécharger CSV",
        data=csv,
        file_name="conversations_data.csv",
        mime="text/csv"
    ) 