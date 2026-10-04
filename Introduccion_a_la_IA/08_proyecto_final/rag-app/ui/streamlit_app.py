import streamlit as st

st.title(" ☄️ AstroBot")
st.subheader("Tu guía del cosmos de confianza 🪐")

st.write(
    "🌌 El universo es enorme y está lleno de preguntas. "
    "Por suerte, AstroBot tiene algunas respuestas."
)

# Inicializar el historial del chat
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "🧑🏻‍🚀 ¿Qué quieres descubrir sobre el universo?"
        }
    ]

# Mostrar historial del chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])