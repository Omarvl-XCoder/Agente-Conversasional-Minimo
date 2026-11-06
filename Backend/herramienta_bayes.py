"""
SCRUM-37: el clasificador Bayesiano expuesto como herramienta (tool) de LangChain.

El decorador @tool convierte la funcion en una herramienta que el agente puede
invocar por si mismo. El LLM NO lee el codigo: lee el NOMBRE, la DESCRIPCION
(docstring) y los PARAMETROS (con su tipo). Por eso el docstring debe explicar
claramente CUANDO usar la herramienta.
"""
from langchain_core.tools import tool

from bayes_router import clasificador


@tool
def clasificar_intencion(mensaje: str) -> dict:
    """Clasifica la intencion de un mensaje del usuario con Naive Bayes.

    Usala SIEMPRE que necesites decidir como atender una consulta sobre
    fatiga al conducir en flotillas. Devuelve la intencion detectada:
    - info_fatiga: pregunta conceptual sobre fatiga o somnolencia.
    - alerta_flotilla: caso concreto de un conductor o unidad con alerta.
    - fuera_de_dominio: tema que no tiene relacion con fatiga al volante.
    - incierto: la confianza es baja y conviene pedir una aclaracion.

    Args:
        mensaje: texto exacto que escribio el usuario.
    """
    resultado = clasificador.clasificar(mensaje)
    return {
        "intencion": resultado["intencion"],
        "confianza": resultado["confianza"],
        "probabilidades": resultado["probabilidades"],
    }


# Lista de herramientas que se le entregan al agente (SCRUM-38 la usara).
HERRAMIENTAS = [clasificar_intencion]
