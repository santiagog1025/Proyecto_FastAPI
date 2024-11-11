import streamlit as st
import requests

# Título de la aplicación
st.title("Asistente Virtual de Desarrollo Profesional")
st.write("¡Hola! Soy tu asistente profesional y estoy aquí para guiarte en tu carrera.")

# Pestaña deslizante (barra lateral) personalizada con fondo rojo oscuro
st.markdown("""
    <style>
        /* Estilo para la barra lateral */
        .css-1d391kg {
            background-color: #8B0000;  /* Rojo oscuro */
            padding: 20px;
            color: white;
        }
        .css-1d391kg input {
            width: 100%;
            padding: 10px;
            font-size: 16px;
            margin-bottom: 10px;
            border-radius: 5px;
            border: 1px solid #fff;
            color: #333;
        }
    </style>
""", unsafe_allow_html=True)

# Barra lateral para el nombre
with st.sidebar:
    st.markdown("<h2>Introduce tu nombre</h2>", unsafe_allow_html=True)
    nombre = st.text_input("Nombre:")

    if nombre:
        st.session_state["user_name"] = nombre
    elif "user_name" in st.session_state:
        st.session_state["user_name"] = None  # Limpiar el nombre si no está completo

# Inicializa el historial de chat en la sesión de Streamlit
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# Generar un `user_id` único para la sesión si no existe
if "user_id" not in st.session_state:
    # Generar un ID único basado en el hash del objeto `chat_history` o en algún valor fijo
    st.session_state["user_id"] = str(hash("unique_user" + str(id(st.session_state))))

# Definir una función para enviar la consulta y actualizar el historial de chat
def send_query():
    user_input = st.session_state["user_input"]
    
    if user_input:
        # Construir el historial de chat como un string que será enviado al backend
        chat_history = "\n".join([f"**🧑 Usuario:** {chat['Pregunta']}\n**🤖 Asistente:** {chat['Respuesta']}" for chat in st.session_state["chat_history"]])
        
        # Añadir la nueva pregunta del usuario al historial para que el modelo lo tenga en cuenta
        chat_history += f"\n**🧑 Usuario:** {user_input}"

        # Obtener el nombre del usuario desde la barra lateral
        user_name = st.session_state.get("user_name", "Usuario")

        # Backend Endpoint
        API_URL = "http://127.0.0.1:8000/generate_response/"
        with st.spinner("Pensando..."):
            # Solicitud a FastAPI con el historial completo, el `user_id` y el nombre del usuario
            response = requests.post(API_URL, json={
                "prompt": f"El nombre del usuario es {user_name}. {chat_history}",
                "user_id": st.session_state["user_id"]
            })
            if response.status_code == 200:
                answer = response.json().get("respuesta", "No se recibió respuesta.")
                # Añadir la pregunta del usuario y la respuesta al historial de chat
                st.session_state["chat_history"].append({"Pregunta": user_input, "Respuesta": answer})
            else:
                st.error("Error en la respuesta del servidor.")
        
        # Limpiar la caja de entrada después de enviar
        st.session_state["user_input"] = ""

# Muestra el historial de chat estilo GPT, encima del input del usuario
st.write("### Chat")
for chat in st.session_state["chat_history"]:
    # Diseño tipo burbuja de chat para las preguntas y respuestas
    st.markdown(f"**🧑 Usuario:** {chat['Pregunta']}", unsafe_allow_html=True)
    st.markdown(f"**🤖 Asistente:** {chat['Respuesta']}", unsafe_allow_html=True)
    st.write("---")

# Input del usuario con el botón para enviar, llamando a send_query cuando se hace clic
st.text_input("Escribe tu pregunta y presiona Enter:", key="user_input", on_change=send_query)
