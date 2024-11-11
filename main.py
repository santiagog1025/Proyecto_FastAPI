from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from groq import Groq
from typing import List, Dict
import logging

# Configurar el logging
logging.basicConfig(level=logging.INFO)

# Cargar variables de entorno y establecer la clave API de Groq
load_dotenv()
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

# Inicializar la aplicación FastAPI
app = FastAPI()

# Crear el modelo de solicitud de datos
class Query(BaseModel):
    prompt: str
    user_id: str  # Agregar el campo user_id

# Definir el mensaje del sistema
SYSTEM_PROMPT = """
Eres un asistente de recomendaciones de carreras laborales personalizadas. Tu tarea es recomendar una carrera adecuada para el usuario, además de sugerir cursos en línea y libros que complementen su desarrollo en esa carrera. Para hacer recomendaciones precisas, comienza preguntando lo siguiente al usuario:

Intereses y Pasiones: Pregunta cuáles son sus áreas de interés principales y si existe algún campo o tema que le apasione (por ejemplo, tecnología, arte, negocios, salud, etc.).

Habilidades Actuales: Pide que mencione las habilidades o conocimientos que posee, tanto habilidades técnicas (como manejo de software, programación, o idiomas) como habilidades blandas (como comunicación, liderazgo, trabajo en equipo, etc.).

Nivel de Educación y Experiencia: Solicita información sobre su nivel educativo actual y experiencia laboral previa, incluyendo cualquier especialización o certificación relevante.

Objetivos Profesionales: Pregunta al usuario sobre sus metas a largo plazo en su carrera (por ejemplo, ocupar un puesto gerencial, trabajar en una empresa internacional, iniciar un negocio propio, etc.).

Preferencias de Estilo de Trabajo: Indaga si prefiere un entorno de trabajo estructurado y tradicional o uno flexible y creativo, y si prefiere trabajar en equipo o de manera independiente.

Disponibilidad para Aprender Nuevas Habilidades: Pregunta si está interesado en realizar cursos o leer libros para mejorar sus habilidades, y cuánto tiempo semanal podría dedicar a este aprendizaje.

Luego de obtener esta información, analiza el perfil del usuario y sugiere una carrera que se ajuste a sus intereses y habilidades. Incluye recomendaciones de cursos en línea y libros que lo ayuden a desarrollar las habilidades necesarias para tener éxito en esa carrera.
"""

# Estructura de memoria para almacenar el historial de conversaciones de cada usuario
user_memory: Dict[str, List[Dict[str, str]]] = {}

# Limitar la cantidad de mensajes en la memoria (para mantener contexto sin sobrecargar la API)
MAX_MEMORY_LENGTH = 5

def get_user_memory(user_id: str) -> List[Dict[str, str]]:
    """Obtiene la memoria del usuario o la crea si no existe."""
    if user_id not in user_memory:
        user_memory[user_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
    return user_memory[user_id]

def update_user_memory(user_id: str, message: Dict[str, str]):
    """Agrega un mensaje a la memoria del usuario, y mantiene solo los más recientes."""
    user_memory[user_id].append(message)
    # Limitar la memoria a los últimos N mensajes
    if len(user_memory[user_id]) > MAX_MEMORY_LENGTH:
        user_memory[user_id] = user_memory[user_id][-MAX_MEMORY_LENGTH:]

# Definir la ruta para generar la respuesta de Groq
@app.post("/generate_response/")
async def generate_response(query: Query):
    try:
        # Verificar los datos que llegan en la solicitud
        logging.info(f"Recibido prompt: {query.prompt}")
        logging.info(f"Recibido user_id: {query.user_id}")
        
        # Obtén la memoria del usuario y agrega el mensaje del usuario actual
        user_id = query.user_id  # Usar el user_id recibido en la solicitud
        messages = get_user_memory(user_id)
        user_message = {"role": "user", "content": query.prompt}
        update_user_memory(user_id, user_message)

        # Llamada a la API de Groq con el historial de mensajes
        response = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=messages,
            temperature=1,
            max_tokens=400
        )

        # Obtener respuesta y actualizar la memoria con la respuesta del asistente
        assistant_message = {"role": "assistant", "content": response.choices[0].message.content.strip()}
        update_user_memory(user_id, assistant_message)

        # Devolver la respuesta en formato JSON
        return {"respuesta": assistant_message["content"]}
    except Exception as e:
        # Manejo de errores con excepción HTTP
        logging.error(f"Error en la solicitud: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error en la solicitud: {str(e)}")
