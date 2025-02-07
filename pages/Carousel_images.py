import streamlit as st
import os
from PIL import Image


if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.error("⛔ Accès refusé. Veuillez vous authentifier sur la page Presentation.")
    st.stop()  # Arrête l'exécution du script ici
    
# Répertoire contenant les images
IMAGE_DIR = "image/"

# Filtrer les fichiers par extension (vous pouvez ajouter d'autres extensions si nécessaire)
valid_extensions = [".png", ".jpg", ".jpeg", ".gif"]
image_files = [f for f in os.listdir(IMAGE_DIR) if os.path.splitext(f)[1].lower() in valid_extensions]
image_files.sort()  # Tri alphabétique, si besoin

# Initialiser l'index de l'image courante dans la session
if "img_index" not in st.session_state:
    st.session_state.img_index = 0

st.title("Carrousel d'Images")
st.write("Devinez qui a réalisé l'image !")

if image_files:
    # Obtenir le chemin complet de l'image courante
    current_image_path = os.path.join(IMAGE_DIR, image_files[st.session_state.img_index])
    
    # Charger et afficher l'image (sans afficher le nom)
    image = Image.open(current_image_path)
    st.image(image, use_container_width =True)
    
    # Boutons de navigation
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("Précédent"):
            st.session_state.img_index = (st.session_state.img_index - 1) % len(image_files)
            st.rerun()
    with col3:
        if st.button("Suivant"):
            st.session_state.img_index = (st.session_state.img_index + 1) % len(image_files)
            st.rerun()
else:
    st.write("Aucune image trouvée dans le dossier spécifié.")
