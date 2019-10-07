#!/usr/bin/python
# -*- encoding: utf-8 -*-

# --------------------------------------------------------------------
# Notes :
#
# * Renomme le fichier à "Predictor.py"
# * Le script nécessite python 3 pour fonctionner correctement
# * Python 3 peut être downloadé à https://www.python.org/
# * Dans le terminal, vérifier l'installation de python avec :
#   which python3
# * Pour lancer le script à partir du terminal, écrire la commande :
#   python3 ~/documents/chemin/vers/Predictor.py
# * Les lignes 1 et 2 servent à encoder en utf-8, pour supporter
#   l'accent aigu dans "Montréal Canadiens" (grosse team)
# * Le modèle présenté ici est ultra simple, mais offre les bases
#   pour coder votre propre modèle ultra top
# * N'hésitez pas à m'écrire si vous avez des questions
#
# - Matthew
# --------------------------------------------------------------------

# Packages nécessaires au fonctionnement du script
# Doivent être installés en utilisant Pip dans le Terminal (Ex.: sudo pip install praw)
import json
import requests
import praw
import random
from datetime import datetime

# Création de l'instance reddit
# Modifier les variables pour vos propres informations
# client_id et client_secret proviennent d'un script app créé à https://www.reddit.com/prefs/apps/
reddit = praw.Reddit(client_id='xxxxxxxxxxxxxx',
                     client_secret='xxxxxxxxxxxxxxxxxxxxxxxxxxx',
                     user_agent='osx:NHLPredictor:1.0.0 (by /u/ilikehopbeverages)', # Pas nécessaire de changer
                     username='username',
                     password='password')

# Obtenir les matchs d'aujourd'hui à travers l'API de la NHL
# Exemple de réponse: coller https://statsapi.web.nhl.com/api/v1/schedule dans un navigateur pour avoir les matchs d'aujourd'hui
today = datetime.today().strftime('%Y-%m-%d')
response = requests.get(f"https://statsapi.web.nhl.com/api/v1/schedule?date={today}")
schedule = json.loads(response.text)

# Cette liste sert à stocker les gagnants de chaque prédiction
# Elle est vide pour l'instant, mais on va venir la remplir une équipe à la fois
winners = []

# Loop à travers chaque match pour déterminer la prédiction du gagnant
# Autrement dit, le script va voir une game à la fois pour aller chercher les données y étant associées
# Tout ce qui fait partie du for-loop doit être en "indent"
for game in schedule["dates"][0]["games"]:

    # Variables pouvant être utiles pour votre modèle :
    teams = game["teams"]
    away_team = teams["away"]["team"]
    home_team = teams["home"]["team"]
    a_id = away_team["id"] # ID de l'équipe away (ex.: 8)
    a_name = away_team["name"] # Nom complet de l'équipe away (ex.: Montréal Canadiens)
    h_id = home_team["id"] # ID de l'équipe home
    h_name = home_team["name"] # Nom complet de l'équipe home

    # Obtenir les statistiques de saison de base pour l'équipe away
    # Exemple de réponse: coller https://statsapi.web.nhl.com/api/v1/teams/8/stats dans un navigateur pour avoir les stats des Canadiens
    response = requests.get(f"https://statsapi.web.nhl.com/api/v1/teams/{a_id}/stats")
    a_stats = json.loads(response.text)
    a_stat = a_stats["stats"][0]["splits"][0]["stat"]

    # Ici, on peut aller chercher n'importe quelle statistique qui sera utile à votre modèle
    # Garder la formule a_stat["nom de la statistique"] pour l'obtenir
    # Si la metric est en "", il faut utiliser float() pour la convertir en nombre (c'est le cas de ptPctg, par exemple)
    a_ptpctg = float(a_stat["ptPctg"])

    # Obtenir les statistiques de saison de base pour l'équipe home
    response = requests.get(f"https://statsapi.web.nhl.com/api/v1/teams/{h_id}/stats")
    h_stats = json.loads(response.text)
    h_stat = h_stats["stats"][0]["splits"][0]["stat"]

    # Encore une fois, on peut aller chercher n'importe quelle statistique, cette fois pour l'équipe home
    # Garder la formule h_stat["nom de la statistique"] pour l'obtenir
    # Si la metric est en "", il faut utiliser float() pour la convertir en nombre (c'est le cas de ptPctg, par exemple)
    h_ptpctg = float(h_stat["ptPctg"])

    # Une fois qu'on a toutes les variables qu'on veut, on peut créer notre modèle
    # Une façon de faire est d'attribuer un score à l'équipe home qui représente sa probabilité de gagner
    home_team_score = h_ptpctg / (h_ptpctg + a_ptpctg) if (h_ptpctg + a_ptpctg) > 0 else 0.5

    # Si l'équipe home a une probabilité de gagner >= 50%, on fait la prédiction que home va gagner
    # Si l'équipe home a une probabilité de gagner < 50%, on fait la prédiction que away va gagner
    if home_team_score >= 0.5:
        winner = h_name
    else:
        winner = a_name

    # On ajoute le nom de l'équipe gagnante à la fin de la liste <winners> créée tout à l'heure
    winners.append(winner)

# Fin du for-loop ici.
# On arrête l'indentation.

# Pour poster au bon thread sur Reddit, on va chercher le stickied post du subreddit r/bihockey
submission = reddit.subreddit('bihockey').sticky()

# Écriture du texte qui sera le body du commentaire
# Chaque ligne de prédiction (la liste <winners> crée plus tôt) sera écrite sous forme de bullet points
text = "**Mes prédictions du gagnant pour chaque match :**\n\n - " + "\n - ".join(winners)

# Pour déboguer :
# Ceci imprimera la réponse à la console plutôt que de poster un commentaire sur Reddit
# Il suffit d'enlever le "#" en avant de la ligne ci-dessous
# print(text); quit()

# On utilise la méthode reply() pour répondre <text> au post <submission>
# À faire après 8h chaque jour
submission.reply(text)
