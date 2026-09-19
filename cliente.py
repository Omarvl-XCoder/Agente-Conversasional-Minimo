import requests

API_URL = "http://127.0.0.1:8000/chat"
historial = []

print("=== Cliente del Agente Conversacional (Entrega 1) ===")
print("Escribe 'salir' para finalizar.\n")

while True:
    usuario = input("Tú: ").strip()
    if not usuario:
        continue
    if usuario.lower() in ("salir", "exit"):
        print("Sesión finalizada.")
        break

    payload = {
        "mensaje": usuario,
        "historial": historial
    }

    try:
        res = requests.post(API_URL, json=payload)
        if res.status_code == 200:
            datos = res.json()
            respuesta = datos["respuesta"]
            print(f"\nAsistente: {respuesta}\n")

            # Acumulación automática del contexto en memoria
            historial.append({"rol": "usuario", "contenido": usuario})
            historial.append({"rol": "asistente", "contenido": respuesta})
        else:
            print(f"Error {res.status_code}: {res.text}")
    except requests.exceptions.ConnectionError:
        print("Error: No se pudo conectar al servidor. Verifica que uvicorn esté corriendo.")