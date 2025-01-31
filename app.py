import streamlit as st
import whisper
import tempfile
import os
from datetime import datetime, timedelta
import time

# Création du dossier de sauvegarde s'il n'existe pas
SAVE_DIR = "sauvegardes"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

# Fonction pour lister les fichiers sauvegardés
def list_saved_files():
    saved_files = {}
    if os.path.exists(SAVE_DIR):
        # Parcourir tous les sous-dossiers
        for date_folder in sorted(os.listdir(SAVE_DIR), reverse=True):
            folder_path = os.path.join(SAVE_DIR, date_folder)
            if os.path.isdir(folder_path):
                files = []
                # Regrouper les fichiers .txt et .srt
                txt_files = {f.replace('.txt', ''): f for f in os.listdir(folder_path) if f.endswith('.txt')}
                for base_name, txt_file in txt_files.items():
                    srt_file = base_name + '.srt'
                    if srt_file in os.listdir(folder_path):
                        files.append({
                            'base_name': base_name,
                            'txt_path': os.path.join(folder_path, txt_file),
                            'srt_path': os.path.join(folder_path, srt_file)
                        })
                if files:
                    saved_files[date_folder] = files
    return saved_files

# Fonction pour convertir les timestamps en format SRT
def format_timestamp(seconds):
    tdelta = timedelta(seconds=seconds)
    hours = int(tdelta.total_seconds() // 3600)
    minutes = int((tdelta.total_seconds() % 3600) // 60)
    seconds = tdelta.total_seconds() % 60
    milliseconds = int((seconds % 1) * 1000)
    seconds = int(seconds)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

def create_srt(segments):
    srt_content = ""
    for i, segment in enumerate(segments, start=1):
        start_time = format_timestamp(segment['start'])
        end_time = format_timestamp(segment['end'])
        text = segment['text'].strip()
        srt_content += f"{i}\n{start_time} --> {end_time}\n{text}\n\n"
    return srt_content

st.set_page_config(
    page_title="Transcription Audio",
    page_icon="🎙️",
    layout="centered"
)

# Configuration de la session state
if 'transcription_history' not in st.session_state:
    st.session_state.transcription_history = []
if 'file_queue' not in st.session_state:
    st.session_state.file_queue = []

# Styles CSS personnalisés
st.markdown("""
    <style>
    .stProgress > div > div > div > div {
        background-color: #00cc00;
    }
    .success-message {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #dcf7dc;
        border: 1px solid #00cc00;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎙️ Transcription Audio en Texte")
st.write("Transformez facilement vos fichiers audio en texte!")

# Section des sauvegardes existantes
st.markdown("### 💾 Sauvegardes existantes")
saved_files = list_saved_files()

if not saved_files:
    st.info("Aucune sauvegarde trouvée.")
else:
    for date, files in saved_files.items():
        with st.expander(f"📅 {date} ({len(files)} fichiers)"):
            for file in files:
                st.markdown(f"**{file['base_name']}**")
                
                # Lecture des contenus
                try:
                    with open(file['txt_path'], 'r', encoding='utf-8') as f:
                        txt_content = f.read()
                    with open(file['srt_path'], 'r', encoding='utf-8') as f:
                        srt_content = f.read()
                    
                    # Affichage avec tabs
                    tab1, tab2 = st.tabs(["Format Texte", "Format SRT"])
                    with tab1:
                        st.text_area("Texte:", value=txt_content, height=150, key=f"saved_txt_{file['base_name']}")
                    with tab2:
                        st.text_area("SRT:", value=srt_content, height=150, key=f"saved_srt_{file['base_name']}")
                    
                    # Boutons de téléchargement
                    col1, col2 = st.columns(2)
                    with col1:
                        st.download_button(
                            label="📥 TXT",
                            data=txt_content,
                            file_name=os.path.basename(file['txt_path']),
                            mime="text/plain",
                            key=f"dl_txt_{file['base_name']}"
                        )
                    with col2:
                        st.download_button(
                            label="📺 SRT",
                            data=srt_content,
                            file_name=os.path.basename(file['srt_path']),
                            mime="text/plain",
                            key=f"dl_srt_{file['base_name']}"
                        )
                except Exception as e:
                    st.error(f"Erreur lors de la lecture du fichier: {str(e)}")
                st.markdown("---")

st.markdown("---")

# Sélection de la langue
langue = st.selectbox(
    "Langue principale de l'audio",
    ["Français", "Anglais", "Espagnol", "Allemand", "Italien", "Portugais", "Auto-détection"],
    index=0
)

# Sélection du modèle
model_size = st.select_slider(
    "Qualité de la transcription (plus la qualité est élevée, plus le processus est long)",
    options=["base", "small", "medium", "large"],
    value="base",
    help="'base' est rapide mais moins précis, 'large' est plus précis mais plus lent"
)

# Chargement du modèle Whisper
@st.cache_resource
def load_model(model_size):
    try:
        return whisper.load_model(model_size)
    except Exception as e:
        st.error(f"Erreur lors du chargement du modèle: {str(e)}")
        return None

# Interface de téléchargement
st.markdown("### 📂 Sélection des fichiers")
uploaded_files = st.file_uploader("Choisissez vos fichiers audio", type=['mp3', 'wav', 'm4a', 'ogg'], accept_multiple_files=True)

if uploaded_files:
    # Affichage de la file d'attente
    st.markdown("### 📋 File d'attente")
    for idx, file in enumerate(uploaded_files):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.audio(file)
        with col2:
            st.markdown(f"**{file.name}**")
    
    col1, col2 = st.columns(2)
    with col1:
        transcribe_button = st.button("🎯 Démarrer les transcriptions")
    with col2:
        save_auto = st.checkbox("Sauvegarder automatiquement", value=True)
    
    if transcribe_button:
        for audio_file in uploaded_files:
            try:
                # Affichage de la progression
                st.markdown(f"**Traitement de : {audio_file.name}**")
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Étape 1: Chargement du modèle
                status_text.text("Chargement du modèle...")
                progress_bar.progress(20)
                model = load_model(model_size)
                
                if model is None:
                    st.error("Impossible de charger le modèle. Veuillez réessayer.")
                    continue
                
                # Étape 2: Préparation du fichier
                status_text.text("Préparation du fichier audio...")
                progress_bar.progress(40)
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(audio_file.name)[1]) as tmp_file:
                    tmp_file.write(audio_file.getvalue())
                    tmp_file_path = tmp_file.name
                
                # Étape 3: Transcription
                status_text.text("Transcription en cours...")
                progress_bar.progress(60)
                
                # Configuration de la langue
                language_code = None
                if langue != "Auto-détection":
                    language_map = {
                        "Français": "fr",
                        "Anglais": "en",
                        "Espagnol": "es",
                        "Allemand": "de",
                        "Italien": "it",
                        "Portugais": "pt"
                    }
                    language_code = language_map.get(langue)
                
                # Transcription avec la langue sélectionnée
                result = model.transcribe(
                    tmp_file_path,
                    language=language_code,
                    fp16=False
                )
                
                progress_bar.progress(80)
                status_text.text("Finalisation...")
                
                transcribed_text = result["text"]
                srt_content = create_srt(result["segments"])
                
                # Génération du timestamp pour les noms de fichiers
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                # Sauvegarde automatique
                if save_auto:
                    # Création d'un sous-dossier avec la date
                    date_folder = os.path.join(SAVE_DIR, datetime.now().strftime("%Y-%m-%d"))
                    if not os.path.exists(date_folder):
                        os.makedirs(date_folder)
                    
                    # Sauvegarde TXT
                    txt_filename = f"transcription_{timestamp}_{audio_file.name}.txt"
                    txt_path = os.path.join(date_folder, txt_filename)
                    with open(txt_path, "w", encoding="utf-8") as f:
                        f.write(transcribed_text)
                    
                    # Sauvegarde SRT
                    srt_filename = f"transcription_{timestamp}_{audio_file.name}.srt"
                    srt_path = os.path.join(date_folder, srt_filename)
                    with open(srt_path, "w", encoding="utf-8") as f:
                        f.write(srt_content)
                    
                    st.info(f"""✅ Fichiers sauvegardés pour {audio_file.name} dans {date_folder} :
                    - {txt_filename}
                    - {srt_filename}""")
                
                # Ajout à l'historique
                st.session_state.transcription_history.append({
                    "filename": audio_file.name,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "text": transcribed_text,
                    "srt": srt_content
                })
                
                progress_bar.progress(100)
                status_text.empty()
                
            except Exception as e:
                st.error(f"Une erreur est survenue avec {audio_file.name}: {str(e)}")
                continue
            
            finally:
                # Nettoyage du fichier temporaire
                if 'tmp_file_path' in locals():
                    os.unlink(tmp_file_path)

# Affichage de l'historique
if st.session_state.transcription_history:
    st.markdown("### 📋 Historique des transcriptions")
    
    # Bouton pour effacer l'historique
    if st.button("🗑️ Effacer l'historique"):
        st.session_state.transcription_history = []
        st.experimental_rerun()
    
    # Affichage de chaque transcription
    for idx, item in enumerate(st.session_state.transcription_history):
        with st.expander(f"📄 {item['filename']} - {item['timestamp']}"):
            tab1, tab2 = st.tabs(["Format Texte", "Format SRT"])
            
            with tab1:
                st.text_area("Texte transcrit:", value=item['text'], height=200, key=f"text_{idx}")
            
            with tab2:
                st.text_area("Format SRT:", value=item['srt'], height=200, key=f"srt_{idx}")
            
            # Boutons de téléchargement
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="📥 Télécharger en TXT",
                    data=item['text'],
                    file_name=f"transcription_{item['filename']}_{idx}.txt",
                    mime="text/plain",
                    key=f"txt_download_{idx}"
                )
            with col2:
                st.download_button(
                    label="📺 Télécharger en SRT",
                    data=item['srt'],
                    file_name=f"transcription_{item['filename']}_{idx}.srt",
                    mime="text/plain",
                    key=f"srt_download_{idx}"
                )
            
            # Informations supplémentaires
            st.markdown(f"""
            **Informations** :
            - Fichier : {item['filename']}
            - Date : {item['timestamp']}
            ---
            """)

# Instructions et aide
with st.expander("ℹ️ Instructions et aide"):
    st.markdown(f"""
    ### Comment utiliser l'application :
    1. Sélectionnez la langue principale de votre audio
    2. Choisissez la qualité de transcription souhaitée
    3. Cliquez sur 'Parcourir' pour sélectionner votre fichier audio
    4. Activez ou désactivez la sauvegarde automatique
    5. Cliquez sur 'Démarrer la transcription'
    
    ### Formats supportés :
    - MP3
    - WAV
    - M4A
    - OGG
    
    ### Organisation des sauvegardes :
    Les fichiers sont sauvegardés dans le dossier '{SAVE_DIR}', organisés par date.
    Chaque transcription génère deux fichiers :
    - Un fichier .txt contenant le texte brut
    - Un fichier .srt contenant les sous-titres avec le timing
    
    ### Résolution des problèmes courants :
    - Si la transcription échoue, essayez avec un fichier plus court
    - Vérifiez que le format du fichier est bien supporté
    - Pour une meilleure précision, utilisez un modèle de plus grande taille
    """) 