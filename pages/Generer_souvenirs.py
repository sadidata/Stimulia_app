import streamlit as st
import openai
import requests
import os
from datetime import datetime
from openai import OpenAI
import io
from pydub import AudioSegment
import imageio_ffmpeg as ffmpeg

# Définir le chemin du binaire ffmpeg fourni par imageio-ffmpeg
AudioSegment.converter = ffmpeg.get_ffmpeg_exe()


if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.error("⛔ Accès refusé. Veuillez vous authentifier sur la page Presentation.")
    st.stop()  # Arrête l'exécution du script ici

    
# Configuration de la clé API OpenAI
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
openai.api_key = OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)



# --- Fonctions d'appel API ---

def transcribe_audio(audio_file_path):
    """
    Transcrit l'audio en texte via l'API Whisper d'OpenAI.
    L'audio_file doit être un objet de type file-like.
    """
    audio_file = open(audio_file_path, "rb")
    transcript = client.audio.transcriptions.create(
        model="whisper-1", 
        file=audio_file, 
        response_format="text"
    )
    return transcript

def generate_image(prompt):
    """
    Génère une image via l'API DALL-E d'OpenAI en utilisant le prompt fourni.
    Renvoie l'URL de l'image générée.
    """
    response = openai.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="hd",
        n=1
    )
    return response.data[0].url

def transform_transcript_to_prompt(transcript_text):
    """
    Utilise GPT-4o pour transformer le texte transcrit en un prompt optimisé pour la génération d'image.
    Supprime les expressions subjectives ou pouvant dégrader le rendu (ex: "je me rappelle...") et précise
    que l'image doit être en forme d'animation reflétant un souvenir.
    """
    prompt = (
        "Transforme le texte suivant en un prompt optimisé pour la génération d'image avec DALL-E. "
        "Supprime toutes les expressions subjectives (par exemple, 'je me rappelle') et reformule-le pour obtenir "
        "Garde les descriptions des personnes (nationalité, couleur de peau, des yeux etc)"
        "une description en style animation qui reflète un souvenir. "
        f"Texte original : {transcript_text}"
    )
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Tu es un assistant expert en création de prompts pour la génération d'images."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

# --- Interface Streamlit ---

st.title("Générateur d'Image à partir d'un Audio")
st.write("Enregistrez un audio. Une fois l'audio terminé, il sera transcrit automatiquement, puis transformé en un prompt optimisé pour générer une image en style animation reflétant un souvenir. L'image sera enregistrée dans le dossier `image`.")

# Composant pour téléverser un fichier audio (formats WAV ou MP3)
audio_file = st.audio_input("Enregistrez ou téléversez votre audio")
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
name_ = st.text_input("Entrer le nom de l'utilisateur")
if audio_file is not None:
    # Lecture du contenu binaire
    audio_bytes = audio_file.getvalue()
    
    # Conversion : ici, on suppose que l'audio est au format WAV
    audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes), format="wav")
    
    # Exporter en MP3
    output_filename = f"audio/souvenir_{name_}.mp3"
    audio_segment.export(output_filename, format="mp3")
    st.success(f"Audio converti et sauvegardé en MP3 sous {output_filename}")

    if st.button("Générer l'image à partir de l'audio"):
        with st.spinner("Transcription de l'audio..."):
            transcript_text = transcribe_audio(output_filename)
        st.write("Transcription :", transcript_text)
        
        with st.spinner("Transformation du texte pour la génération d'image..."):
            transformed_prompt = transform_transcript_to_prompt(transcript_text)
        st.write("Prompt transformé :", transformed_prompt)
        
        with st.spinner("Génération de l'image..."):
            image_url = generate_image(transformed_prompt)
        
        # Téléchargement de l'image générée
        image_response = requests.get(image_url)
        if image_response.status_code == 200:
            # Création du dossier "image" s'il n'existe pas
            os.makedirs("image", exist_ok=True)
            # Création d'un nom de fichier unique (en fonction de la date et de l'heure)
            file_name = f"image/image_{name_}.png"
            with open(file_name, "wb") as f:
                f.write(image_response.content)
            st.success(f"Image enregistrée sous : {file_name}")
            st.image(image_url, caption="Image générée avec DALL-E")
        else:
            st.error("Erreur lors du téléchargement de l'image.")
