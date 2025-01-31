# Transcription Audio 🎙️

Une application simple pour transcrire vos fichiers audio en texte.

## Prérequis

1. **Python** : 
   - Téléchargez et installez Python depuis [python.org](https://python.org)
   - Version recommandée : Python 3.8 ou supérieure

2. **FFmpeg** :
   
   **Pour Windows** :
   - Téléchargez FFmpeg depuis [ffmpeg.org](https://ffmpeg.org/download.html)
   - Ajoutez FFmpeg aux variables d'environnement Windows

   **Pour Mac** :
   - Installez avec Homebrew : `brew install ffmpeg`

   **Pour Linux** :
   - Ubuntu/Debian : `sudo apt-get install ffmpeg`
   - Fedora : `sudo dnf install ffmpeg`

## Installation

1. **Téléchargez ce dossier** sur votre ordinateur

2. **Ouvrez un terminal** (Invite de commandes sur Windows)

3. **Naviguez vers le dossier** de l'application :
   ```bash
   cd chemin/vers/le/dossier
   ```

4. **Créez un environnement virtuel** :
   
   Sur Windows :
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

   Sur Mac/Linux :
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

5. **Installez les dépendances** :
   ```bash
   pip install -r requirements.txt
   ```

## Lancement de l'application

1. **Activez l'environnement virtuel** (si ce n'est pas déjà fait) :
   
   Sur Windows :
   ```bash
   venv\Scripts\activate
   ```

   Sur Mac/Linux :
   ```bash
   source venv/bin/activate
   ```

2. **Lancez l'application** :
   ```bash
   streamlit run app.py
   ```

3. Votre navigateur web s'ouvrira automatiquement avec l'application

## Utilisation

1. Cliquez sur "Parcourir" pour sélectionner votre fichier audio
2. Cliquez sur "Démarrer la transcription"
3. Attendez que la transcription soit terminée
4. Récupérez votre texte transcrit

## Formats audio supportés

- MP3
- WAV
- M4A
- OGG

## Problèmes courants

1. **FFmpeg non trouvé** :
   - Vérifiez que FFmpeg est bien installé
   - Sur Windows, vérifiez les variables d'environnement

2. **Erreur Python** :
   - Vérifiez que Python est bien installé
   - Vérifiez que vous utilisez l'environnement virtuel

Pour toute aide supplémentaire, n'hésitez pas à créer une issue sur ce projet. 