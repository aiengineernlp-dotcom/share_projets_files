"""
Module de tableau de bord pour TheKnowHow.
"""
import streamlit as st
import requests
import json
import logging
from typing import Dict, Any
from datetime import datetime
import pandas as pd
import plotly.express as px
from streamlit_chat import message
import jwt

class Dashboard:
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
        self.logger = logging.getLogger(__name__)
        
    def initialize_session_state(self):
        """Initialise l'état de la session."""
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        if 'user_token' not in st.session_state:
            st.session_state.user_token = None
        if 'username' not in st.session_state:
            st.session_state.username = None

    def login_page(self):
        """Page de connexion."""
        st.title("Connexion - Assistant Médical IA")
        
        with st.form("login_form"):
            username = st.text_input("Nom d'utilisateur")
            password = st.text_input("Mot de passe", type="password")
            submitted = st.form_submit_button("Se connecter")
            
            if submitted:
                try:
                    response = requests.post(
                        f"{self.api_url}/token",
                        data={"username": username, "password": password}
                    )
                    if response.status_code == 200:
                        token_data = response.json()
                        st.session_state.user_token = token_data["access_token"]
                        st.session_state.username = username
                        st.success("Connexion réussie!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Erreur de connexion : {str(e)}")

    def display_chat_interface(self):
        """Affiche l'interface de chat."""
        st.title("Assistant Médical IA - TheKnowHow")
        
        # Sidebar avec les statistiques et options
        with st.sidebar:
            st.header("Options")
            if st.button("Effacer l'historique"):
                self._clear_history()
            
            st.header("Statistiques")
            self._display_statistics()
        
        # Zone principale de chat
        st.header("Conversation")
        
        # Affichage des messages
        for msg in st.session_state.messages:
            is_user = msg["role"] == "user"
            message(msg["content"], is_user=is_user, key=msg["timestamp"])
        
        # Zone de saisie
        with st.container():
            user_message = st.text_input("Votre message :", key="user_input")
            col1, col2 = st.columns([4, 1])
            with col2:
                if st.button("Envoyer"):
                    self._process_message(user_message)

    def _process_message(self, message: str):
        """Traite et envoie un message."""
        if not message:
            return
            
        try:
            # Ajout du message utilisateur
            timestamp = datetime.now().isoformat()
            st.session_state.messages.append({
                "role": "user",
                "content": message,
                "timestamp": f"user_{timestamp}"
            })
            
            # Appel à l'API
            response = self._send_message(message)
            
            # Ajout de la réponse
            st.session_state.messages.append({
                "role": "assistant",
                "content": response["response"],
                "timestamp": f"assistant_{timestamp}"
            })
            
            # Réinitialisation de l'entrée
            st.rerun()
            
        except Exception as e:
            st.error(f"Erreur : {str(e)}")

    def _send_message(self, message: str) -> Dict[str, Any]:
        """Envoie un message à l'API."""
        try:
            headers = {}
            if st.session_state.user_token:
                headers["Authorization"] = f"Bearer {st.session_state.user_token}"
                
            response = requests.post(
                f"{self.api_url}/chat",
                json={"text": message},
                headers=headers
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi du message : {str(e)}")
            raise

    def _clear_history(self):
        """Efface l'historique des conversations."""
        try:
            headers = {"Authorization": f"Bearer {st.session_state.user_token}"}
            response = requests.delete(
                f"{self.api_url}/history",
                headers=headers
            )
            response.raise_for_status()
            st.session_state.messages = []
            st.success("Historique effacé avec succès!")
            
        except Exception as e:
            st.error(f"Erreur lors de l'effacement de l'historique : {str(e)}")

    def _display_statistics(self):
        """Affiche les statistiques d'utilisation."""
        try:
            headers = {"Authorization": f"Bearer {st.session_state.user_token}"}
            response = requests.get(
                f"{self.api_url}/history",
                headers=headers
            )
            history = response.json()
            
            if history:
                # Création d'un DataFrame
                df = pd.DataFrame(history)
                df['date'] = pd.to_datetime(df['timestamp']).dt.date
                
                # Graphique des conversations par jour
                fig = px.line(
                    df.groupby('date').size().reset_index(name='count'),
                    x='date',
                    y='count',
                    title="Conversations par jour"
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Statistiques générales
                st.metric("Total des conversations", len(history))
                st.metric("Aujourd'hui", len(df[df['date'] == pd.Timestamp.now().date()]))
                
        except Exception as e:
            st.error(f"Erreur lors du chargement des statistiques : {str(e)}")

    def run(self):
        """Lance l'interface utilisateur."""
        self.initialize_session_state()
        
        if not st.session_state.user_token:
            self.login_page()
        else:
            self.display_chat_interface()

if __name__ == "__main__":
    dashboard = Dashboard()
    dashboard.run() 