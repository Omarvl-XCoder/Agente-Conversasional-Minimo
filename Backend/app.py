import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import requests


from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

import logging
from bayes_router import clasificador

logger = logging.getLogger("uvicorn.error")

# Cargar variables de entorno (tu API_KEY_GROQ)
load_dotenv()



# ==========================================
# 1. CREACIÓN DEL MICROSERVICIO (FastAPI)
# ==========================================
app = FastAPI(title="Agente Conversacional ")

# Agregar el middleware de CORS aquí (después de crear app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# 2. CREACIÓN DEL AGENTE (LangChain)
# ==========================================
llm = ChatGroq(
    groq_api_key=os.environ.get("API_KEY_GROQ"),
    model_name="openai/gpt-oss-20b", 
    max_tokens=500 # para que no de errores a la hora de preguntar 
)

prompt = ChatPromptTemplate.from_messages([
    ("system", """Eres un asistente conversacional mínimo desarrollado con LangChain y FastAPI, ejecutándose sobre el modelo openai/gpt-oss-20b a través de la infraestructura de Groq.

INFORMACIÓN SOBRE TU IDENTIDAD (RESPETA ESTO ESTRICTAMENTE):
- NO eres ChatGPT, ni GPT-4, ni un producto de OpenAI.
- NO eres Claude, Gemini, ni ningún asistente de otras empresas.
- Cuando te pregunten quién eres, responde: "Soy un agente conversacional mínimo construido con LangChain y FastAPI, corriendo sobre el modelo openai/gpt-oss-20b alojado en Groq."
- Si te preguntan tu versión, di que es un prototipo educativo, no un producto comercial.

SOBRE TU MEMORIA:
- Recuerdas el contexto de la conversación actual (el historial se te pasa en cada mensaje).
- NO tienes memoria persistente entre sesiones distintas.
- Si te preguntan si tienes memoria, explica esta distinción con claridad.

REGLAS DE COMPORTAMIENTO:
- Responde de forma clara, útil y concisa.
- Si no sabes algo, dilo honestamente. NO inventes información.
- Si el usuario pregunta sobre algo fuera de tu conocimiento, admítelo.
- Evita respuestas excesivamente largas salvo que el usuario lo pida.
- Sé amable pero directo."""),
    ("system", "{nota_ruta}"),
    MessagesPlaceholder(variable_name="historial"),
    ("human", "{entrada}")
])

# El agente conversacional mínimo
cadena = prompt | llm

# Nota que el modulo bayesiano le pasa al LLM segun la intencion detectada
NOTAS_RUTA = {
    "info_fatiga": "La consulta es conceptual sobre fatiga al conducir. Responde de forma educativa y clara.",
    "alerta_flotilla": "La consulta trata de un caso concreto de un conductor o unidad. Responde con pasos de accion concretos.",
    "fuera_de_dominio": "La consulta esta fuera del dominio de fatiga en flotillas. Indica brevemente que tu especialidad es la fatiga al volante y ofrece ayuda en ese tema.",
    "incierto": "La intencion del usuario no es clara. Si hace falta, pide una aclaracion breve antes de responder.",
}

# ==========================================
# 3. MODELOS DE DATOS PARA LA API (Pydantic)
# ==========================================
class MensajeHistorial(BaseModel):
    rol: str  # "usuario" o "asistente"
    contenido: str

class PeticionChat(BaseModel):
    mensaje: str
    historial: Optional[List[MensajeHistorial]] = []
    conversacion_id: Optional[int] = None  # Nuevo campo para agrupar chats

class RespuestaChat(BaseModel):
    respuesta: str
    conversacion_id: Optional[int] = None  # Para que el frontend sepa el ID
    intencion: Optional[str] = None
    confianza: Optional[float] = None

@app.get("/")
def ruta_raiz():
    return {"estado": "Servidor activo", "mensaje": "Bienvenido al Agente de IA"}

# ==========================================
# 4. ENDPOINT /chat (Requerido por el PDF)
# ==========================================
@app.post("/chat", response_model=RespuestaChat)
async def endpoint_chat(peticion: PeticionChat):
    # a) Convertir el historial que llega por internet al formato de LangChain
    memoria_langchain = []
    for msg in peticion.historial:
        if msg.rol == "usuario":
            memoria_langchain.append(HumanMessage(content=msg.contenido))
        elif msg.rol == "asistente":
            memoria_langchain.append(AIMessage(content=msg.contenido))

        # a2) Razonamiento probabilistico (Bayes): clasificar la intencion
    clasif = clasificador.clasificar(peticion.mensaje)
    logger.info(
        "[BAYES] mensaje=%r | palabras=%s | probs=%s | decision=%s (confianza=%s)",
        peticion.mensaje, clasif["palabras_usadas"], clasif["probabilidades"],
        clasif["intencion"], clasif["confianza"],
    )

    # b) Pasar los datos al agente de LangChain
    resultado = await cadena.ainvoke({
        "historial": memoria_langchain,
        "entrada": peticion.mensaje,
        "nota_ruta": NOTAS_RUTA[clasif["intencion"]],
    })

    URL_DJANGO = "http://django-service:8001/api"
    conv_id = peticion.conversacion_id

    try:
        # 1. Si es el primer mensaje, crear la "carpeta" de la conversación
        if not conv_id:
            res_conv = requests.post(f"{URL_DJANGO}/conversaciones/", json={})
            if res_conv.status_code == 201:
                conv_id = res_conv.json().get("id")

        # 2. Guardar el globo de texto del usuario
        if conv_id:
            requests.post(f"{URL_DJANGO}/mensajes/", json={
                "conversacion": conv_id,
                "rol": "usuario",
                "contenido": peticion.mensaje
            })

            # 3. Guardar el globo de texto de la IA
            requests.post(f"{URL_DJANGO}/mensajes/", json={
                "conversacion": conv_id,
                "rol": "agente",
                "contenido": resultado.content
            })
    except Exception as e:
        print(f"Error conectando con el microservicio de gestión: {e}")

    # d) Devolver la respuesta al frontend junto con el ID del chat
    return RespuestaChat(
        respuesta=resultado.content,
        conversacion_id=conv_id,
        intencion=clasif["intencion"],
        confianza=clasif["confianza"],
    )