#!/bin/bash

echo "Installation de l'application de transcription..."

# Création de l'environnement virtuel
python3 -m venv venv

# Activation de l'environnement virtuel
source venv/bin/activate

# Installation des dépendances
pip install -r requirements.txt

echo "Installation terminée !"
echo "Pour lancer l'application, exécutez : sh run.sh" 