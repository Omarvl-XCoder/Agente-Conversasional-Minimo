"""
Módulo: Sistema Basado en Reglas (SBR) Determinístico
Entregable 2 - Actividad 3: Hechos, Base de Conocimientos y Motor de Inferencia.
"""

class SistemaBasadoEnReglas:
    def __init__(self):
        # 1. BASE DE CONOCIMIENTOS (Reglas de producción SI -> ENTONCES)
        self.reglas = [
            {
                "id": "R1_EMERGENCIA_FATIGA",
                "condiciones": lambda hechos: hechos.get("alerta_critica") is True,
                "accion": "PRIORIDAD_ALTA: Se detectan signos de fatiga o emergencia vial. Recomendar detener el vehículo inmediatamente en una zona segura.",
                "Directiva_Obligatoria": True
            },
            {
                "id": "R2_CONSULTA_REGLAMENTO",
                "condiciones": lambda hechos: hechos.get("solicita_normativa") is True,
                "accion": "POLÍTICA_OPERATIVA: Fundamentar la respuesta estrictamente en los manuales y políticas internas de seguridad vial del RAG.",
                "Directiva_Obligatoria": False
            },
            {
                "id": "R3_HORARIO_DESCANSO",
                "condiciones": lambda hechos: hechos.get("menciona_horas_conduccion") is True,
                "accion": "REGLA_NEGOCIO: Recordar que por normativa ningún conductor debe exceder las 5 horas continuas de manejo sin una pausa de 30 minutos.",
                "Directiva_Obligatoria": True
            },
            {
                "id": "R4_ESCALAMIENTO_SOPORTE",
                "condiciones": lambda hechos: hechos.get("falla_mecanica") is True,
                "accion": "PROTOCOLO_INCIDENTE: Indicar que debe reportar la falla a la central de monitoreo y no intentar reparaciones en autopista.",
                "Directiva_Obligatoria": True
            }
        ]

    # 2. EXTRACCIÓN DE HECHOS (Memoria de Trabajo a partir del mensaje)
    def extraer_hechos(self, mensaje: str) -> dict:
        texto = mensaje.lower()
        hechos = {
            "alerta_critica": any(p in texto for p in ["dormido", "sueño", "cansado", "fatiga", "cerrando los ojos", "bostezo", "accidente"]),
            "solicita_normativa": any(p in texto for p in ["regla", "norma", "política", "manual", "protocolo", "permitido"]),
            "menciona_horas_conduccion": any(p in texto for p in ["horas", "turno", "descanso", "pausa", "tiempo manejando"]),
            "falla_mecanica": any(p in texto for p in ["freno", "motor", "llanta", "humo", "avería", "falla"])
        }
        return hechos

    # 3. MOTOR DE INFERENCIA (Encadenamiento hacia adelante / Forward Chaining)
    def inferir(self, mensaje: str) -> dict:
        hechos_actuales = self.extraer_hechos(mensaje)
        reglas_activadas = []
        directivas = []

        for regla in self.reglas:
            if regla["condiciones"](hechos_actuales):
                reglas_activadas.append(regla["id"])
                directivas.append(regla["accion"])

        return {
            "hechos": hechos_actuales,
            "reglas_activadas": reglas_activadas,
            "directivas_negocio": directivas
        }

# Instancia lista para importar en app.py
motor_reglas = SistemaBasadoEnReglas()