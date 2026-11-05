"""SCRUM-37: prueba local de la herramienta (sin Docker, sin API key)."""
from herramienta_bayes import clasificar_intencion

print("Nombre:     ", clasificar_intencion.name)
print("Descripcion:", clasificar_intencion.description[:70], "...")
print("Parametros: ", clasificar_intencion.args)
print("-" * 60)

for m in ["¿Qué es la somnolencia al conducir?",
          "La unidad 5 tiene una alerta de parpadeo",
          "Dame una receta de pizza",
          "Hola"]:
    print(m, "->", clasificar_intencion.invoke({"mensaje": m}))
