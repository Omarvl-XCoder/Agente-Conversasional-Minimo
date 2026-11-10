import os
import sys
import logging
import requests
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

# Módulos del Entregable 2: Reglas (SBR), Probabilidad (Bayes) y Memoria Semántica (RAG)
from motor_sbr import motor_reglas
from bayes_router import clasificador
from rag.retriever import SupabaseRetriever, formatear_contexto

# Configuración de logs en consola y archivo físico (force=True para no ser ignorado por Uvicorn)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("ejecucion_agente.log", encoding="utf-8")
    ],
    force=True
)
logger = logging.getLogger("AgenteFlotilla")

# Conectar con el retriever real de Supabase (SCRUM-27)
try:
    retriever_rag = SupabaseRetriever(k=3)
    RAG_DISPONIBLE = True
except Exception as e:
    logger.error(f"Error inicializando SupabaseRetriever: {e}")
    retriever_rag = None
    RAG_DISPONIBLE = False

# Cargar variables de entorno (tu API_KEY_GROQ)
load_dotenv()

# ==========================================
# 1. CREACIÓN DEL MICROSERVICIO (FastAPI)
# ==========================================
app = FastAPI(title="Agente Conversacional")

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
    max_tokens=500
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
- Cuentas con memoria semántica (RAG), un Sistema Basado en Reglas (SBR) y un enrutador probabilístico (Bayes).

REGLAS DE COMPORTAMIENTO:
- Responde de forma clara, útil y concisa.
- Si se te proporciona CONTEXTO RAG o DIRECTIVAS DE REGLAS DE NEGOCIO, úsalos obligatoriamente para fundamentar tu respuesta.
- Si no sabes algo, dilo honestamente. NO inventes información."""),
    ("system", "ENRUTAMIENTO BAYESIANO: {nota_ruta}"),
    ("system", "DIRECTIVAS DEL SISTEMA BASADO EN REGLAS (SBR):\n{reglas_sbr}"),
    ("system", "CONTEXTO RECUPERADO DE LA BASE VECTORIAL (RAG):\n{contexto_rag}"),
    MessagesPlaceholder(variable_name="historial"),
    ("human", "{entrada}")
])

# Cadena principal del agente
cadena = prompt | llm

# Nota que el módulo bayesiano le pasa al LLM según la intención detectada
NOTAS_RUTA = {
    "info_fatiga": "La consulta es conceptual sobre fatiga al conducir. Responde de forma educativa y clara.",
    "alerta_flotilla": "La consulta trata de un caso concreto de un conductor o unidad. Responde con pasos de acción concretos.",
    "fuera_de_dominio": "La consulta está fuera del dominio de fatiga en flotillas. Indica brevemente que tu especialidad es la fatiga al volante y ofrece ayuda en ese tema.",
    "incierto": "La intención del usuario no es clara. Si hace falta, pide una aclaración breve antes de responder.",
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
    conversacion_id: Optional[int] = None

class RespuestaChat(BaseModel):
    respuesta: str
    conversacion_id: Optional[int] = None
    intencion: Optional[str] = None
    confianza: Optional[float] = None
    reglas_activadas: Optional[List[str]] = []

@app.get("/")
def ruta_raiz():
    return {"estado": "Servidor activo", "mensaje": "Bienvenido al Agente de IA"}

# ==========================================
# 4. ENDPOINT /chat (Requerido por el PDF)
# ==========================================
@app.post("/chat", response_model=RespuestaChat)
async def endpoint_chat(peticion: PeticionChat):
    # a) Convertir el historial al formato de LangChain
    memoria_langchain = []
    for msg in peticion.historial:
        if msg.rol == "usuario":
            memoria_langchain.append(HumanMessage(content=msg.contenido))
        elif msg.rol == "asistente":
            memoria_langchain.append(AIMessage(content=msg.contenido))

    # b) Razonamiento probabilístico (Bayes): clasificar la intención
    clasif = clasificador.clasificar(peticion.mensaje)
    logger.info(
        "[BAYES] mensaje=%r | palabras=%s | probs=%s | decision=%s (confianza=%s)",
        peticion.mensaje, clasif["palabras_usadas"], clasif["probabilidades"],
        clasif["intencion"], clasif["confianza"],
    )

    # c) Sistema Basado en Reglas (SBR): evaluar hechos y disparar reglas determinísticas
    resultado_sbr = motor_reglas.inferir(peticion.mensaje)
    texto_reglas = (
        "\n".join(resultado_sbr["directivas_negocio"])
        if resultado_sbr["directivas_negocio"]
        else "Ninguna regla crítica activada para este mensaje."
    )
    logger.info(
        "[SBR] hechos=%s | reglas_activadas=%s",
        resultado_sbr["hechos"], resultado_sbr["reglas_activadas"]
    )

    # d) Memoria Semántica (RAG): recuperar fragmentos relevantes desde Supabase
    # d) Memoria Semántica (RAG): recuperar fragmentos relevantes desde Supabase
    texto_rag = "Sin contexto documental adicional."
    if clasif["intencion"] != "fuera_de_dominio" and retriever_rag is not None:
        try:
            logger.info("[RAG] Consultando base de datos vectorial en Supabase...")
            docs = retriever_rag.invoke(peticion.mensaje)
            if docs:
                texto_rag = formatear_contexto(docs)
                logger.info(
                    "[RAG] %d fragmentos recuperados de Supabase (fuentes=%s)",
                    len(docs), [d.metadata.get("fuente") for d in docs]
                )
            else:
                logger.info("[RAG] La consulta no arrojó fragmentos coincidentes.")
        except Exception as e:
            logger.error(f"[RAG] Error consultando el retriever: {e}")
    else:
        logger.info("[RAG] Omitido por clasificador o retriever no inicializado.")

    # e) Pasar todos los componentes integrados al agente de LangChain
    resultado = await cadena.ainvoke({
        "historial": memoria_langchain,
        "entrada": peticion.mensaje,
        "nota_ruta": NOTAS_RUTA.get(clasif["intencion"], NOTAS_RUTA["incierto"]),
        "reglas_sbr": texto_reglas,
        "contexto_rag": texto_rag,
    })

    # f) Persistir conversación y mensajes en el microservicio de gestión (Django DRF)
    URL_DJANGO = "http://django-service:8001/api"
    conv_id = peticion.conversacion_id

    try:
        if not conv_id:
            res_conv = requests.post(f"{URL_DJANGO}/conversaciones/", json={})
            if res_conv.status_code == 201:
                conv_id = res_conv.json().get("id")

        if conv_id:
            requests.post(f"{URL_DJANGO}/mensajes/", json={
                "conversacion": conv_id,
                "rol": "usuario",
                "contenido": peticion.mensaje
            })

            requests.post(f"{URL_DJANGO}/mensajes/", json={
                "conversacion": conv_id,
                "rol": "agente",
                "contenido": resultado.content
            })
    except Exception as e:
        logger.error(f"Error conectando con el microservicio de gestión: {e}")

    # g) Devolver la respuesta al frontend junto con metadatos de razonamiento
    return RespuestaChat(
        respuesta=resultado.content,
        conversacion_id=conv_id,
        intencion=clasif["intencion"],
        confianza=clasif["confianza"],
        reglas_activadas=resultado_sbr["reglas_activadas"],
    )