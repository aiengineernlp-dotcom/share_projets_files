# streamlit_app.py
import streamlit as st
import joblib
import pandas as pd

# Charger ton modèle (assure-toi qu'il existe)
model = joblib.load("modele_arbre_prune.joblib")

st.title("🌍 Prédiction du continent d’un pays selon son drapeau")

# Interface utilisateur simple
color = st.selectbox("Couleur principale du drapeau", ['red', 'blue', 'green', 'white'])
has_gold = st.checkbox("Présence de doré")

# Exemple de features simplifiés (à adapter selon ton dataset réel)
features = {
    'red': int(color == 'red'),
    'blue': int(color == 'blue'),
    'green': int(color == 'green'),
    'white': int(color == 'white'),
    'gold': int(has_gold),
}

X = pd.DataFrame([features])

if st.button("Prédire le continent"):
    prediction = model.predict(X)[0]
    continent = "Amérique du Nord" if prediction == 3 else "Océanie"
    st.success(f"🌍 Résultat : {continent}")
