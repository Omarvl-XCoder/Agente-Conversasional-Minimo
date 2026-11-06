# Flujo de decisión del agente (SCRUM-34)

**Técnica de IA elegida:** razonamiento probabilístico con el Teorema de Bayes
(clasificador Naive Bayes, `Backend/bayes_router.py`, SCRUM-29).

**Capacidad que requiere el agente:** decidir de forma autónoma *qué tipo de consulta*
recibió para responder con el enfoque adecuado.

## 1. Cuándo se invoca la técnica

El agente invoca la herramienta `clasificar_intencion` en **cada mensaje nuevo del
usuario**, antes de redactar la respuesta final. La herramienta se expone con `@tool`
(SCRUM-37, `Backend/herramienta_bayes.py`).

## 2. Diagrama de decisión

```mermaid
flowchart TD
    A([Usuario envía mensaje]) --> B[POST /chat en FastAPI]
    B --> C{¿El agente necesita clasificar la consulta?}
    C -- Sí --> D[Invoca tool clasificar_intencion]
    D --> E[Normaliza texto: minúsculas, sin acentos, sin stopwords]
    E --> F[Calcula P intención dado mensaje con Bayes]
    F --> G{¿Confianza >= 0.60?}
    G -- No --> H[intención = incierto]
    G -- Sí --> I{Intención ganadora}
    I -- info_fatiga --> J[Responde de forma educativa]
    I -- alerta_flotilla --> K[Responde con pasos de acción concretos]
    I -- fuera_de_dominio --> L[Indica que su especialidad es la fatiga al volante]
    H --> M[Pide una aclaración breve]
    J --> N[Registra log y guarda mensajes en Django]
    K --> N
    L --> N
    M --> N
    N --> O([Devuelve respuesta, intención y confianza al frontend])
```

## 3. Reglas de decisión

| Condición | Intención | Comportamiento del agente |
|---|---|---|
| Pregunta conceptual sobre fatiga o somnolencia | `info_fatiga` | Respuesta educativa y clara |
| Caso concreto de un conductor o unidad con alerta | `alerta_flotilla` | Pasos de acción concretos |
| Tema ajeno a la fatiga al volante | `fuera_de_dominio` | Aclara su especialidad y ofrece ayuda en el tema |
| Probabilidad máxima menor a 0.60 | `incierto` | Pide una aclaración breve |

## 4. Entradas y salidas de la herramienta

- **Entrada:** `mensaje` (texto del usuario).
- **Salida:** `intencion`, `confianza` y `probabilidades` por clase.
- **Umbral de confianza:** 0.60 (parámetro `umbral` de `ClasificadorBayes`).

## 5. Relación con las demás tareas del sprint

- SCRUM-35: lógica base del clasificador (`bayes_router.py`).
- SCRUM-37: la función se expone como `@tool` (`herramienta_bayes.py`).
- SCRUM-38: las instrucciones del sistema indican al agente cuándo usar la herramienta.
- SCRUM-39: registro de logs dentro de la herramienta.
- SCRUM-40: evidencias de ejecución para el documento final.
