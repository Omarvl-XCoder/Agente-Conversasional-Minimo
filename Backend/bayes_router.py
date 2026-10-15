"""
Modulo de razonamiento probabilistico (SCRUM-29)
Clasificador de intencion con el Teorema de Bayes (Naive Bayes).

    P(intencion | mensaje) = P(mensaje | intencion) * P(intencion) / P(mensaje)

Sirve para decidir a que capacidad del agente enrutar una consulta.
"""
import math
import re
import unicodedata
from collections import Counter

STOPWORDS = {
    "que", "los", "las", "una", "uno", "por", "para", "con", "del", "como",
    "cual", "cuales", "esta", "este", "son", "mis", "muy", "hay", "puedes",
    "pueden", "mas", "sus", "tiene", "hace", "dame", "hola",
}

DATOS_ENTRENAMIENTO = {
    "info_fatiga": [
        "que es la fatiga al volante",
        "cuales son los sintomas de la fatiga en conductores",
        "como prevenir el cansancio al manejar",
        "cuantas horas puede manejar un conductor sin descanso",
        "que causa la somnolencia al conducir",
        "como afecta el sueno la conduccion",
        "recomendaciones para evitar microsuenos en carretera",
        "diferencia entre fatiga y somnolencia",
    ],
    "alerta_flotilla": [
        "el conductor del camion tiene una alerta de fatiga",
        "explica la alerta del sensor del vehiculo",
        "mi conductor lleva ocho horas manejando y bostezando",
        "se activo la alerta de parpadeo prolongado",
        "que hago con la alerta del turno nocturno",
        "el sistema detecto desviacion de carril en la unidad",
        "unidad con alerta de cabeceo del conductor",
        "reporte de alerta en la flotilla de hoy",
    ],
    "fuera_de_dominio": [
        "cual es la capital de francia",
        "dame una receta de pasta",
        "quien gano el partido de futbol",
        "ayudame con mi tarea de matematicas",
        "recomiendame una pelicula",
        "como esta el clima hoy",
        "cuanto cuesta un telefono nuevo",
        "cuentame un chiste",
    ],
}


def normalizar(texto):
    """Minusculas, sin acentos, solo palabras utiles."""
    texto = unicodedata.normalize("NFD", texto.lower())
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return [p for p in re.findall(r"[a-z]+", texto) if len(p) > 2 and p not in STOPWORDS]


class ClasificadorBayes:
    def __init__(self, datos, umbral=0.60):
        self.umbral = umbral
        self.intenciones = list(datos.keys())
        total_frases = sum(len(frases) for frases in datos.values())

        # P(intencion): probabilidad a priori
        self.prior = {i: len(f) / total_frases for i, f in datos.items()}

        # Conteo de palabras por intencion (para P(palabra | intencion))
        self.conteo = {}
        self.total_palabras = {}
        self.vocabulario = set()
        for intencion, frases in datos.items():
            c = Counter()
            for frase in frases:
                c.update(normalizar(frase))
            self.conteo[intencion] = c
            self.total_palabras[intencion] = sum(c.values())
            self.vocabulario.update(c)

    def clasificar(self, mensaje):
        palabras = [p for p in normalizar(mensaje) if p in self.vocabulario]
        v = len(self.vocabulario)

        # log P(intencion) + suma de log P(palabra | intencion), con suavizado de Laplace
        log_post = {}
        for i in self.intenciones:
            lp = math.log(self.prior[i])
            for p in palabras:
                lp += math.log((self.conteo[i][p] + 1) / (self.total_palabras[i] + v))
            log_post[i] = lp

        # Normalizar (divide entre P(mensaje)) para obtener probabilidades que suman 1
        m = max(log_post.values())
        exp = {i: math.exp(x - m) for i, x in log_post.items()}
        total = sum(exp.values())
        probs = {i: exp[i] / total for i in exp}

        mejor = max(probs, key=probs.get)
        confianza = probs[mejor]
        return {
            "mensaje": mensaje,
            "palabras_usadas": palabras,
            "probabilidades": {i: round(p, 3) for i, p in probs.items()},
            "intencion": mejor if confianza >= self.umbral else "incierto",
            "confianza": round(confianza, 3),
        }


clasificador = ClasificadorBayes(DATOS_ENTRENAMIENTO)