# Asistente Virtual de Desarrollo Profesional

Este proyecto consiste en una aplicación web que permite interactuar con un asistente virtual especializado en recomendar carreras laborales personalizadas, cursos en línea y libros que ayuden en el desarrollo profesional del usuario. El asistente obtiene información del usuario para sugerir la mejor carrera basada en sus intereses, habilidades, nivel educativo, experiencia y objetivos profesionales.

La aplicación está construida usando **FastAPI** para el backend y **Streamlit** para el frontend.

## Estructura del Proyecto

Este proyecto se divide en dos partes principales:

1. **Backend (FastAPI)**: 
   - Implementa un servidor web que maneja las solicitudes del frontend y consulta el modelo Groq para generar las respuestas personalizadas.
   
2. **Frontend (Streamlit)**:
   - Interfaz de usuario para que los usuarios introduzcan sus datos, como el nombre, y reciban recomendaciones personalizadas del asistente virtual.

## Requisitos

- Python 3.8 o superior.
- Dependencias del proyecto:
  - FastAPI
  - Pydantic
  - Groq
  - Requests
  - Streamlit
  - python-dotenv
  - Uvicorn
