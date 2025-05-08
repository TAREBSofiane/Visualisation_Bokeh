# Projet de Visualisation des Mobilités à Rennes

Ce petit projet propose une visualisation interactive des mobilités à Rennes en utilisant la bibliothèque Bokeh en Python. Le projet se concentre sur deux aspects principaux : le réseau de transport en commun STAR et la fréquentation des modes de déplacement doux (vélo/piéton) sur les grands boulevards.

## Fonctionnalités

### Réseau STAR
- Visualisation cartographique du réseau de lignes STAR (métro et bus)
- Affichage des arrêts de transport en commun
- Analyse du nombre de lignes par type de transport
- Statistiques sur le nombre d'arrêts par commune

### Fréquentation verte
- Carte interactive des points de comptage vélo/piéton avec leurs emplacements
- Histogrammes des moyennes de fréquentation par :
  - Heure de la journée
  - Mois de l'année
  - Année

## Technologies utilisées
- **Python** : langage de programmation principal
- **Pandas** : manipulation et traitement des données
- **NumPy** : calculs mathématiques
- **Bokeh** : création de visualisations interactives
- **Bokeh Server** (optionnel) : pour déployer l'application de façon interactive

## Structure des données
Le projet utilise trois jeux de données :
- `star_itineraires_actifs.csv` : Données sur les lignes du réseau STAR
- `star_arrets_physiques_actifs.csv` : Données sur les arrêts physiques du réseau
- `eco-counter-data.csv` : Données de comptage des déplacements doux (piétons/vélos)

## Installation et exécution

1. Cloner le dépôt :
```bash
git clone https://github.com/votre-compte/Visualisation_Bokeh.git
cd Visualisation_Bokeh
```

2. Installer les dépendances :
```bash
pip install -r requirements.txt
```

3. Exécuter le script :
```bash
python script.py
```

4. Le navigateur s'ouvrira automatiquement avec la visualisation interactive.

## Structure du projet
- `script.py` : Script principal contenant tout le code
- `data/` : Dossier contenant les jeux de données
   - `star_itineraires_actifs.csv`
   - `star_arrets_physiques_actifs.csv`
   - `eco-counter-data.csv`

## Fonctionnalités interactives
- Survol des éléments pour afficher des informations détaillées
- Navigation entre les onglets pour visualiser différents aspects
- Activation/désactivation des catégories via la légende
- Zoom et déplacement dans les cartes
