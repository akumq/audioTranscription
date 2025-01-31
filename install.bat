@echo off
echo Installation de l'application de transcription...

:: Création de l'environnement virtuel
python -m venv venv

:: Activation de l'environnement virtuel
call venv\Scripts\activate

:: Installation des dépendances
pip install -r requirements.txt

echo Installation terminée !
echo Pour lancer l'application, exécutez "run.bat"
pause 