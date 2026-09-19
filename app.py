import os
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

# Cargar variables de entorno (tu API_KEY_GROQ)
load_dotenv()

# ==========================================
# 1. CREACIÓN DEL MICROSERVICIO (FastAPI)
# ==========================================
app = FastAPI(title="Agente Conversacional ")

# ==========================================
# 2. CREACIÓN DEL AGENTE (LangChain)
# ==========================================
llm = ChatGroq(
    groq_api_key=os.environ.get("API_KEY_GROQ"),
    model_name="qwen/qwen3.8-27b", # aqui se puede poner el que sea 
    max_tokens=500 # para que no de errores a la hora de preguntar 
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "Eres un asistente conversacional útil, amable y conciso."),
    MessagesPlaceholder(variable_name="historial"),
    ("human", "{entrada}")
])

# El agente conversacional mínimo
cadena = prompt | llm

# ==========================================
# 3. MODELOS DE DATOS PARA LA API (Pydantic)
# ==========================================
class MensajeHistorial(BaseModel):
    rol: str  # "usuario" o "asistente"
    contenido: str

class PeticionChat(BaseModel):
    mensaje: str
    historial: Optional[List[MensajeHistorial]] = []

class RespuestaChat(BaseModel):
    respuesta: str

# ==========================================
# 4. ENDPOINT /chat (Requerido por el PDF)
# ==========================================
@app.post("/chat", response_model=RespuestaChat)
def endpoint_chat(peticion: PeticionChat):
    # a) Convertir el historial que llega por internet al formato de LangChain
    memoria_langchain = []
    for msg in peticion.historial:
        if msg.rol == "usuario":
            memoria_langchain.append(HumanMessage(content=msg.contenido))
        elif msg.rol == "asistente":
            memoria_langchain.append(AIMessage(content=msg.contenido))

    # b) Pasar los datos al agente de LangChain
    resultado = cadena.invoke({
        "historial": memoria_langchain,
        "entrada": peticion.mensaje
    })

    # c) Devolver la respuesta en formato JSON
    return RespuestaChat(respuesta=resultado.content)