"""
Module de construction de la base de connaissances médicales.
Intègre les données analysées, structure les connaissances et met à jour la base.
"""

import logging
from typing import Dict, List, Optional, Set, Tuple
import json
from datetime import datetime
import networkx as nx
from collections import defaultdict
import numpy as np
import pandas as pd
from pathlib import Path

from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

class KnowledgeBaseBuilder:
    """Classe pour la construction de la base de connaissances médicales."""
    
    def __init__(self, output_path: str):
        """
        Initialise le constructeur de base de connaissances.
        
        Args:
            output_path: Chemin de sortie pour la base de connaissances
        """
        self.logger = logging.getLogger(__name__)
        self.output_path = output_path
        self.knowledge_graph = nx.DiGraph()
        self.symptom_index = defaultdict(set)
        self.diagnosis_index = defaultdict(set)
        self.temporal_patterns = defaultdict(list)
        
    def build_knowledge_base(self, cases: List[Dict], analysis_results: Dict) -> None:
        """
        Construit la base de connaissances à partir des cas et des résultats d'analyse.
        
        Args:
            cases: Liste des cas médicaux
            analysis_results: Résultats des analyses (symptômes, relations, statistiques)
        """
        self.logger.info("Début de la construction de la base de connaissances")
        
        try:
            # Intégration des cas
            self._integrate_cases(cases)
            
            # Intégration des analyses
            self._integrate_analysis_results(analysis_results)
            
            # Structuration des connaissances
            self._structure_knowledge()
            
            # Sauvegarde de la base
            self._save_knowledge_base()
            
            self.logger.info("Construction de la base de connaissances terminée")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la construction de la base: {str(e)}")
            
    def _integrate_cases(self, cases: List[Dict]) -> None:
        """
        Intègre les cas médicaux dans la base de connaissances.
        
        Args:
            cases: Liste des cas médicaux
        """
        for case in cases:
            case_id = case.get('id', str(len(self.knowledge_graph.nodes)))
            
            # Conversion des dates en chaînes de caractères
            case_data = {}
            for k, v in case.items():
                if isinstance(v, (pd.Period, pd.Timestamp)):
                    case_data[k] = str(v)
                else:
                    case_data[k] = v
            
            # Ajout du cas comme nœud
            self.knowledge_graph.add_node(case_id, type='case', **case_data)
            
            # Indexation des symptômes
            for symptom in case.get('symptoms', []):
                self.symptom_index[symptom].add(case_id)
                self.knowledge_graph.add_edge(symptom, case_id, type='has_symptom')
                
            # Indexation des diagnostics
            diagnosis = case.get('diagnosis')
            if diagnosis:
                self.diagnosis_index[diagnosis].add(case_id)
                self.knowledge_graph.add_edge(case_id, diagnosis, type='has_diagnosis')
                
            # Enregistrement des patterns temporels
            if 'date' in case:
                date = case['date']
                if isinstance(date, (pd.Period, pd.Timestamp)):
                    date = str(date)
                self.temporal_patterns[date].append(case_id)
                
    def _integrate_analysis_results(self, analysis_results: Dict) -> None:
        """
        Intègre les résultats d'analyse dans la base de connaissances.
        
        Args:
            analysis_results: Résultats des analyses
        """
        # Intégration des relations
        if 'relationship' in analysis_results:
            self._integrate_relationships(analysis_results['relationship'])
            
        # Intégration des patterns
        if 'pattern' in analysis_results:
            self._integrate_patterns(analysis_results['pattern'])
            
        # Intégration des statistiques
        if 'statistics' in analysis_results:
            self._integrate_statistics(analysis_results['statistics'])
            
    def _integrate_relationships(self, relationships: Dict) -> None:
        """
        Intègre les relations entre cas dans le graphe.
        
        Args:
            relationships: Relations entre cas
        """
        if 'graph' in relationships:
            for edge in relationships['graph'].edges(data=True):
                self.knowledge_graph.add_edge(edge[0], edge[1], **edge[2])
                
    def _integrate_patterns(self, patterns: Dict) -> None:
        """
        Intègre les patterns détectés dans la base.
        
        Args:
            patterns: Patterns détectés
        """
        for pattern_type, pattern_data in patterns.items():
            pattern_id = f"pattern_{len(self.knowledge_graph.nodes)}"
            self.knowledge_graph.add_node(pattern_id, type='pattern', pattern_type=pattern_type, **pattern_data)
            
            # Liaison des cas au pattern
            for case_id in pattern_data.get('cases', []):
                self.knowledge_graph.add_edge(pattern_id, case_id, type='exhibits_pattern')
                
    def _integrate_statistics(self, statistics: Dict) -> None:
        """
        Intègre les statistiques dans la base.
        
        Args:
            statistics: Statistiques générées
        """
        for stat_type, stat_data in statistics.items():
            stat_id = f"stat_{len(self.knowledge_graph.nodes)}"
            self.knowledge_graph.add_node(stat_id, type='statistic', stat_type=stat_type, **stat_data)
            
    def _structure_knowledge(self) -> None:
        """Structure les connaissances dans le graphe."""
        # Ajout des relations symptôme-diagnostic
        for symptom, cases in self.symptom_index.items():
            for case_id in cases:
                diagnosis = self.knowledge_graph.nodes[case_id].get('diagnosis')
                if diagnosis:
                    self.knowledge_graph.add_edge(symptom, diagnosis, type='associated_with')
                    
        # Ajout des relations temporelles
        for date, cases in self.temporal_patterns.items():
            if len(cases) > 1:
                for i in range(len(cases)-1):
                    self.knowledge_graph.add_edge(cases[i], cases[i+1], type='temporal_sequence')
                    
    def _save_knowledge_base(self) -> None:
        """Sauvegarde la base de connaissances."""
        try:
            # Conversion du graphe en format JSON
            knowledge_data = {
                'nodes': [
                    {'id': str(node), **{str(k): str(v) if isinstance(v, (pd.Period, pd.Timestamp)) else v 
                                       for k, v in data.items()}}
                    for node, data in self.knowledge_graph.nodes(data=True)
                ],
                'edges': [
                    {'source': str(u), 'target': str(v), **{str(k): str(v) if isinstance(v, (pd.Period, pd.Timestamp)) else v 
                                                          for k, v in data.items()}}
                    for u, v, data in self.knowledge_graph.edges(data=True)
                ],
                'indices': {
                    'symptoms': {str(k): [str(v) for v in list(v)] for k, v in self.symptom_index.items()},
                    'diagnoses': {str(k): [str(v) for v in list(v)] for k, v in self.diagnosis_index.items()}
                },
                'temporal_patterns': {str(k): [str(v) for v in v] for k, v in self.temporal_patterns.items()}
            }
            
            # Sauvegarde dans un fichier JSON
            with open(f"{self.output_path}/knowledge_base.json", 'w', encoding='utf-8') as f:
                json.dump(knowledge_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la sauvegarde de la base: {str(e)}")
            
    def query_knowledge_base(self, query: Dict) -> List[Dict]:
        """
        Interroge la base de connaissances.
        
        Args:
            query: Dictionnaire de critères de recherche
            
        Returns:
            Liste des résultats correspondants
        """
        results = []
        
        try:
            # Recherche par symptôme
            if 'symptom' in query:
                case_ids = self.symptom_index.get(query['symptom'], set())
                results.extend([
                    self.knowledge_graph.nodes[case_id]
                    for case_id in case_ids
                ])
                
            # Recherche par diagnostic
            if 'diagnosis' in query:
                case_ids = self.diagnosis_index.get(query['diagnosis'], set())
                results.extend([
                    self.knowledge_graph.nodes[case_id]
                    for case_id in case_ids
                ])
                
            # Recherche par période
            if 'start_date' in query and 'end_date' in query:
                start = datetime.fromisoformat(query['start_date'])
                end = datetime.fromisoformat(query['end_date'])
                for date, cases in self.temporal_patterns.items():
                    if start <= datetime.fromisoformat(date) <= end:
                        results.extend([
                            self.knowledge_graph.nodes[case_id]
                            for case_id in cases
                        ])
                        
            return list(set(results))  # Élimination des doublons
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la requête: {str(e)}")
            return []
            
    def update_knowledge_base(self, new_cases: List[Dict], new_analysis: Dict) -> None:
        """
        Met à jour la base de connaissances avec de nouveaux cas et analyses.
        
        Args:
            new_cases: Nouveaux cas médicaux
            new_analysis: Nouvelles analyses
        """
        self.logger.info("Début de la mise à jour de la base de connaissances")
        
        try:
            # Intégration des nouveaux cas
            self._integrate_cases(new_cases)
            
            # Intégration des nouvelles analyses
            self._integrate_analysis_results(new_analysis)
            
            # Restructuration des connaissances
            self._structure_knowledge()
            
            # Sauvegarde de la base mise à jour
            self._save_knowledge_base()
            
            self.logger.info("Mise à jour de la base de connaissances terminée")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la mise à jour: {str(e)}")

class ModelBuilder:
    """Classe pour la construction et la configuration des modèles NLP."""
    
    def __init__(self):
        """Initialise le builder."""
        self.logger = logging.getLogger(__name__)
        
    def build_model(self, model_name: str, device: Optional[str] = None) -> Dict:
        """
        Construit un modèle NLP.
        
        Args:
            model_name (str): Nom du modèle à construire
            device (Optional[str]): Device sur lequel charger le modèle
            
        Returns:
            Dict: Modèle et tokenizer
        """
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            
        try:
            # Chargement du tokenizer
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            
            # Chargement du modèle
            model = AutoModelForCausalLM.from_pretrained(model_name)
            model.to(device)
            
            self.logger.info(f"Modèle {model_name} chargé avec succès sur {device}")
            
            return {
                "model": model,
                "tokenizer": tokenizer,
                "device": device
            }
            
        except Exception as e:
            self.logger.error(f"Erreur lors du chargement du modèle {model_name}: {str(e)}")
            raise
            
    def save_model(self, model: Dict, output_dir: str):
        """
        Sauvegarde un modèle.
        
        Args:
            model (Dict): Modèle à sauvegarder
            output_dir (str): Répertoire de sortie
        """
        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Sauvegarde du modèle
            model["model"].save_pretrained(output_dir)
            
            # Sauvegarde du tokenizer
            model["tokenizer"].save_pretrained(output_dir)
            
            self.logger.info(f"Modèle sauvegardé avec succès dans {output_dir}")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la sauvegarde du modèle: {str(e)}")
            raise
            
    def load_model(self, model_dir: str, device: Optional[str] = None) -> Dict:
        """
        Charge un modèle sauvegardé.
        
        Args:
            model_dir (str): Répertoire du modèle
            device (Optional[str]): Device sur lequel charger le modèle
            
        Returns:
            Dict: Modèle et tokenizer
        """
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            
        try:
            model_path = Path(model_dir)
            if not model_path.exists():
                raise FileNotFoundError(f"Répertoire du modèle non trouvé: {model_dir}")
                
            # Chargement du tokenizer
            tokenizer = AutoTokenizer.from_pretrained(model_dir)
            
            # Chargement du modèle
            model = AutoModelForCausalLM.from_pretrained(model_dir)
            model.to(device)
            
            self.logger.info(f"Modèle chargé avec succès depuis {model_dir}")
            
            return {
                "model": model,
                "tokenizer": tokenizer,
                "device": device
            }
            
        except Exception as e:
            self.logger.error(f"Erreur lors du chargement du modèle depuis {model_dir}: {str(e)}")
            raise 