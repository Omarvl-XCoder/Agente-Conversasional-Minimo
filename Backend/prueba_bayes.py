from bayes_router import clasificador

mensajes = [
    "¿Qué es la somnolencia al conducir?",
    "La unidad 5 tiene una alerta de parpadeo",
    "Dame una receta de pizza",
    "Hola",
    "El conductor lleva muchas horas manejando",
]

for m in mensajes:
    r = clasificador.clasificar(m)
    print("Mensaje:      ", r["mensaje"])
    print("Palabras:     ", r["palabras_usadas"])
    print("Probabilidad: ", r["probabilidades"])
    print("Decision:     ", r["intencion"], "(confianza", r["confianza"], ")")
    print("-" * 60)