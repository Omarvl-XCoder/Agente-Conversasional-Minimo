import logging
import re
from langchain_core.tools import tool

logger = logging.getLogger("AgenteFlotilla.ToolPLN")

def analizar_texto_pln(texto: str) -> str:
    """
    Lógica base (SCRUM-35): Analiza el texto usando PLN básico.
    Extrae correos, evalúa sentimiento y busca palabras clave.
    """
    texto_lower = texto.lower()
    hallazgos = []
    
    # 1. Extracción de entidades (Correos)
    correos = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', texto)
    if correos:
        hallazgos.append(f"Correos detectados: {', '.join(correos)}")
        
    # 2. Análisis de sentimiento
    palabras_pos = ["gracias", "excelente", "bueno", "genial", "feliz", "ayuda"]
    palabras_neg = ["malo", "enojado", "pésimo", "error", "falla", "molesto", "problema"]
    
    if any(p in texto_lower for p in palabras_pos):
        hallazgos.append("Sentimiento: Positivo")
    elif any(p in texto_lower for p in palabras_neg):
        hallazgos.append("Sentimiento: Negativo / Queja")
    else:
        hallazgos.append("Sentimiento: Neutro")

    # 3. Palabras clave (Ejemplo: Precios)
    if "precio" in texto_lower or "costo" in texto_lower:
         hallazgos.append("Entidad: Consulta de precio")

    if not hallazgos:
        return "No se encontraron entidades relevantes."
        
    return " | ".join(hallazgos)

@tool
def herramienta_analisis_pln(texto_usuario: str) -> str:
    """
    Útil para analizar el texto del usuario. 
    Úsala cuando el usuario escriba correos, exprese quejas o pregunte por precios.
    """
    logger.info(f"[TOOL-PLN] Invocando 'herramienta_analisis_pln' | entrada='{texto_usuario}'")
    resultado = analizar_texto_pln(texto_usuario)
    logger.info(f"[TOOL-PLN] Hallazgos PLN: {resultado}")
    return resultado