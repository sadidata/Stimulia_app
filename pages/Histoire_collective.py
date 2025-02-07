
import streamlit as st
import openai
import requests
import time
from elevenlabs.client import ElevenLabs
import elevenlabs
from datetime import datetime


if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.error("⛔ Accès refusé. Veuillez vous authentifier sur la page Presentation.")
    st.stop()  # Arrête l'exécution du script ici
    
# Configuration des clés API
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
ELEVENLABS_API_KEY = st.secrets["ELEVENLABS_API_KEY"]

openai.api_key = OPENAI_API_KEY

client_evenlab = ElevenLabs(
    api_key=ELEVENLABS_API_KEY,
)

# --- Fonctions de génération d'histoire et text-to-speech (NE CHANGE PAS LES APPELS API) ---

def generate_story_part1(user_input):
    """
    Génère le début de l'histoire en intégrant les contributions (non vides) de l'utilisateur,
    puis propose trois options crédibles pour la suite.
    La réponse doit être formatée ainsi :
      - Le récit (texte complet)
      - Une ligne vide
      - La ligne 'OPTIONS:'
      - Trois lignes commençant par '1)', '2)', '3)' pour les options.
    Le récit est demandé de manière captivante et concise.
    """
    prompt = (
        f"L'histoire débute avec ces éléments : {user_input}. "
        "Raconte un début d'aventure de manière captivante et concise en intégrant ces éléments. "
        "À la fin, propose trois options crédibles pour la suite, chacune sous forme d'une courte phrase. "
        "Formate ta réponse de la manière suivante : d'abord le récit, puis une ligne vide, ensuite la ligne 'OPTIONS:', "
        "puis sur trois lignes, écris '1) [option]', '2) [option]', '3) [option]'."
    )
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Tu es un conteur d'histoires féeriques. Raconte l'introduction d'une aventure de manière captivante, précise et concise. Termine le récit en proposant trois options crédibles pour la suite, formatées comme indiqué."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

def generate_story_final(history, chosen_option):
    """
    Génère la conclusion de l'histoire en intégrant l'option choisie dans la première partie.
    L'histoire est conclue de manière cohérente, captivante et concise, sans proposer d'options supplémentaires.
    """
    prompt = (
        f"{history}\nUtilise cet élément choisi : {chosen_option} pour conclure l'aventure. "
        "Raconte le climax et la fin de l'histoire de manière cohérente, captivante et concise. "
        "Conclue l'histoire sans proposer d'options supplémentaires."
    )
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Tu es un conteur d'histoires féeriques. Conclus l'histoire de manière captivante, cohérente et concise, sans proposer d'options."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

def text_to_speech(text, client_even):
    """Convertit le texte en audio avec ElevenLabs."""
    return client_even.text_to_speech.convert(
        voice_id="L8JVqRsSjFF2XMHfiCgq",
        output_format="mp3_44100_128",
        text=text,
        model_id="eleven_flash_v2_5"
    )

# --- Interface Streamlit ---

st.title("🧚‍♀️ Générateur d'Histoires Féeriques")
st.write("Faites participer jusqu'à 7 personnes en remplissant les champs ci-dessous. Seuls les champs non vides seront utilisés pour générer le début de l'histoire. Ensuite, choisissez une option proposée pour conclure l'aventure.")


# Initialisation des variables de session
if "history" not in st.session_state:
    st.session_state.history = ""
if "part1_generated" not in st.session_state:
    st.session_state.part1_generated = False
if "part1_done" not in st.session_state:
    st.session_state.part1_done = False
if "options1" not in st.session_state:
    st.session_state.options1 = []
if "choice1" not in st.session_state:
    st.session_state.choice1 = ""
if "part3_generated" not in st.session_state:
    st.session_state.part3_generated = False
if "part3_done" not in st.session_state:
    st.session_state.part3_done = False

# Pour stocker les audios générés
if "audio1" not in st.session_state:
    st.session_state.audio1 = None
if "audio3" not in st.session_state:
    st.session_state.audio3 = None

# ----- Saisie des contributions (7 inputs) -----
if not st.session_state.part1_generated:
    st.subheader("Contributions pour le début de l'histoire (max 7 personnes)")
    hero = st.text_input("Héros", key="input_hero")
    env = st.text_input("Environnement", key="input_env")
    adversaire = st.text_input("Adversaire", key="input_adversaire")
    objet = st.text_input("Objet magique", key="input_objet")
    pouvoir = st.text_input("Pouvoir spécial", key="input_pouvoir")
    compagnon = st.text_input("Compagnon", key="input_compagnon")
    quete = st.text_input("Quête", key="input_quete")
    if st.button("Générer le début de l'histoire", key="btn1"):
        contributions = []
        if hero: contributions.append(f"Héros: {hero}")
        if env: contributions.append(f"Environnement: {env}")
        if adversaire: contributions.append(f"Adversaire: {adversaire}")
        if objet: contributions.append(f"Objet magique: {objet}")
        if pouvoir: contributions.append(f"Pouvoir spécial: {pouvoir}")
        if compagnon: contributions.append(f"Compagnon: {compagnon}")
        if quete: contributions.append(f"Quête: {quete}")
        user_input_combined = ", ".join(contributions)
        with st.spinner("Génération du début de l'histoire..."):
            output = generate_story_part1(user_input_combined)
        # On s'attend à ce que la réponse contienne 'OPTIONS:'
        if "OPTIONS:" in output:
            narrative, options_str = output.split("OPTIONS:", 1)
            narrative = narrative.strip()
            st.session_state.history += narrative + "\n"
            # Conversion audio du récit généré
            audio_file1 = text_to_speech(narrative, client_evenlab)
            if audio_file1:
                elevenlabs.save(audio_file1, "audio/test1.mp3")
                with open("audio/test1.mp3", "rb") as f:
                    audio_bytes = f.read()
                st.audio(audio_bytes, format="audio/mp3")
                st.session_state.audio1 = audio_bytes
            # Extraction et nettoyage des options
            options_lines = options_str.strip().splitlines()
            options_list = []
            for line in options_lines:
                line = line.strip()
                if line.startswith("1)") or line.startswith("2)") or line.startswith("3)"):
                    option_text = line[2:].strip()
                    options_list.append(option_text)
                else:
                    options_list.append(line)
            st.session_state.options1 = options_list
        else:
            st.session_state.history += output.strip() + "\n"
        st.session_state.part1_generated = True

# ----- Choix de l'option dans la partie 1 -----
if st.session_state.part1_generated and not st.session_state.part1_done:
    st.markdown("### Histoire générée jusqu'à présent :")
    st.write(st.session_state.history)
    if st.session_state.options1:
        selected_option1 = st.radio("Choisissez une option pour continuer :", st.session_state.options1, key="radio1")
        if st.button("Valider votre choix", key="validate1"):
            st.session_state.choice1 = selected_option1
            st.session_state.history += "\n" + st.session_state.choice1 + "\n"
            st.session_state.part1_done = True

# ----- Étape finale : Conclure l'histoire (sans choix) -----
if st.session_state.part1_done and not st.session_state.part3_generated:
    st.subheader("Étape Finale : Conclure l'histoire")
    if st.button("Générer la conclusion de l'histoire", key="btn_final"):
        with st.spinner("Génération de la conclusion de l'histoire..."):
            output = generate_story_final(st.session_state.history, st.session_state.choice1)
        narrative = output.strip()
        st.session_state.history += narrative + "\n"
        st.session_state.part3_generated = True
        st.session_state.part3_done = True
        audio_file3 = text_to_speech(narrative, client_evenlab)
        if audio_file3:
            elevenlabs.save(audio_file3, "audio/test3.mp3")
            with open("audio/test3.mp3", "rb") as f:
                audio_bytes = f.read()
            st.audio(audio_bytes, format="audio/mp3")
            st.session_state.audio3 = audio_bytes

# Affichage final de l'histoire complétée
if st.session_state.part3_done:
    st.markdown("### Histoire Finale :")
    st.write(st.session_state.history)

# Section pour rejouer les audios générés, même après
st.markdown("### Rejouer les audios générés")
if st.session_state.audio1 is not None:
    st.subheader("Audio du début")
    st.audio(st.session_state.audio1, format="audio/mp3")
if st.session_state.audio3 is not None:
    st.subheader("Audio de la conclusion")
    st.audio(st.session_state.audio3, format="audio/mp3")


# Boutons de réinitialisation et sauvegarde
col1, col2 = st.columns(2)
with col1:
    if st.button("Réinitialiser l'histoire"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
with col2:
    if st.session_state.get("history", ""):
        st.download_button(
            "Sauvegarder l'histoire",
            data=st.session_state.history,
            file_name=f"story_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )
