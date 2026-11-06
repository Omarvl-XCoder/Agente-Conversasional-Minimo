import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from logic import herramienta_analisis_pln

load_dotenv()

app = FastAPI(title="Agente Conversacional")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

llm = ChatGroq(
    groq_api_key=os.environ.get("API_KEY_GROQ"),
    model_name="openai/gpt-oss-20b", 
    max_tokens=500 
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "Eres un asistente conversacional útil y empático. Tienes una herramienta para analizar el texto (PLN). Úsala siempre que el usuario proporcione un correo, exprese una queja o pregunte por precios."),
    MessagesPlaceholder(variable_name="historial"),
    ("human", "{entrada}")
])

llm_con_herramientas = llm.bind_tools([herramienta_analisis_pln])
cadena = prompt | llm_con_herramientas

class MensajeHistorial(BaseModel):
    rol: str
    contenido: str

class PeticionChat(BaseModel):
    mensaje: str
    historial: Optional[List[MensajeHistorial]] = []

class RespuestaChat(BaseModel):
    respuesta: str

@app.get("/")
def ruta_raiz():
    return {"estado": "Servidor activo", "mensaje": "Bienvenido al Agente de IA"}

@app.post("/chat", response_model=RespuestaChat)
async def endpoint_chat(peticion: PeticionChat):
    memoria_langchain = []
    for msg in peticion.historial:
        if msg.rol == "usuario":
            memoria_langchain.append(HumanMessage(content=msg.contenido))
        elif msg.rol == "asistente":
            memoria_langchain.append(AIMessage(content=msg.contenido))

    resultado = await cadena.ainvoke({
        "historial": memoria_langchain,
        "entrada": peticion.mensaje
    })

    if resultado.tool_calls:
        for tool_call in resultado.tool_calls:
            if tool_call["name"] == "herramienta_analisis_pln":
                texto_a_analizar = tool_call["args"]["texto_usuario"]
                
                resultado_pln = herramienta_analisis_pln.invoke(texto_a_analizar)
                
                mensaje_herramienta = HumanMessage(
                    content=f"El análisis PLN del mensaje es: {resultado_pln}. Responde al usuario de forma natural basándote en esto."
                )
                
                respuesta_final = await llm.ainvoke(
                    memoria_langchain + [HumanMessage(content=peticion.mensaje), mensaje_herramienta]
                )
                return RespuestaChat(respuesta=respuesta_final.content)

    return RespuestaChat(respuesta=resultado.content)