import streamlit as st
import hmac
import streamlit as st

# Simuler des secrets (normalement, ils sont stockés dans `st.secrets`)
USER_CREDENTIALS = {
    st.secrets["database"]["username"]: {"password": st.secrets["database"]["password"]},
}

# Configurer la page avec un titre, un emoji, et des éléments de menu
st.set_page_config(
    page_title="Stimulia",
    page_icon="🌍",
    layout="wide",  # Options: 'centered' ou 'wide'
)

# Fonction pour vérifier l'authentification
def check_credentials():
    """Vérifie le nom d'utilisateur, le mot de passe et la clé API."""
    
    def credentials_entered():
        """Valide les identifiants entrés par l'utilisateur."""
        username = st.session_state.get("username", "")
        password = st.session_state.get("password", "")
        
        if username in USER_CREDENTIALS:
            user_data = USER_CREDENTIALS[username]
            if hmac.compare_digest(password, user_data["password"]):
                # Authentification réussie
                st.session_state["authenticated"] = True
                # Supprimer les informations sensibles des entrées
                del st.session_state["username"]
                del st.session_state["password"]
                return
        # Si les identifiants sont incorrects
        st.session_state["authenticated"] = False

    # Si l'utilisateur est déjà authentifié, retourner True
    if st.session_state.get("authenticated", False):
        return True

    # Interface d'entrée pour les identifiants
    st.title("🔐 Authentification requise")
    st.text_input("Nom d'utilisateur", key="username")
    st.text_input("Mot de passe", type="password", key="password")
    st.button("Se connecter", on_click=credentials_entered)

    # Message d'erreur si les identifiants sont incorrects
    if "authenticated" in st.session_state and not st.session_state["authenticated"]:
        st.error("😕 Nom d'utilisateur, mot de passe")
    return False

# Appel de la fonction pour gérer l'authentification
if not check_credentials():
    st.stop()  # Bloque l'exécution si l'utilisateur n'est pas authentifié

st.markdown("""
**Bienvenue !** 😊

Cette application vous propose une expérience immersive en deux grandes sections accessibles via des onglets :
""")

st.markdown("## Générer / Raconter un Souvenir 🎤")
st.markdown("""
Dans cette section, vous pouvez :

- **Générer un souvenir** :  
  Enregistrez un audio 🎙️ qui sera ensuite transformé en une image unique 🖼️, créant ainsi un souvenir visuel à partir de votre voix.

- **Raconter son souvenir ou son histoire** :  
  Racontez votre histoire en audio. Celle-ci sera également convertie en image, permettant d'illustrer votre récit de manière originale.
""")

st.markdown("## Histoire Collective 📖")
st.markdown("""
Cette section vous invite à participer à une aventure collective en deux temps :

1. **Contribuer à l'histoire collective** :  
    Vous renseignez différentes informations concernant :
    - Votre héros 🦸‍♂️🦸‍♀️
    - L'environnement 🌳🏙️
    - Et d'autres éléments de votre histoire personnelle ✨

    Ces contributions servent à construire une histoire commune 🤝.

2. **Décider de la suite de l'histoire** :  
    Après avoir écouté l'histoire collective qui résulte des contributions de chacun, vous intervenez une deuxième fois pour influencer son évolution.  
    Vous choisissez, parmi trois options proposées, la direction que prendra l'histoire 🔀.
""")

st.markdown("## Navigation 🧭")
st.markdown("""
Pour accéder aux fonctionnalités décrites, utilisez les onglets situés en haut de l'application :

- **Onglet 'Générer / Raconter un Souvenir'** : pour créer ou partager un souvenir via un enregistrement audio.
- **Onglet 'Histoire Collective'** : pour contribuer à l'élaboration et à l'évolution de l'histoire collective.
""")
