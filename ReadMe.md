# 🤖 Agente Conversacional Mínimo — Entrega 1

Microservicio con **FastAPI** y agente conversacional básico implementado con **LangChain** y **Groq API**.

---

## 📋 Requisitos Previos

Antes de comenzar, asegúrate de tener instalado:
* **Python 3.10 o superior** (marcar "Add Python to PATH" durante la instalación).
* **Git** instalado en tu sistema.
* Una cuenta gratuita en [Groq Cloud Console](https://console.groq.com/keys) para obtener tu API Key.

---

## 🚀 Guía de Instalación y Ejecución Paso a Paso

Sigue estos pasos en orden estricto en tu terminal:

### 1. Clonar el repositorio y entrar a la carpeta
```bash
git clone [https://github.com/Omarvl-XCoder/Agente-Conversasional-Minimo.git](https://github.com/Omarvl-XCoder/Agente-Conversasional-Minimo.git)
cd Agente-Conversasional-Minimo
```

---

### 2. Configurar el Entorno Virtual

Crea un entorno aislado para no mezclar librerías con tu sistema operativo:

```bash
# Crear el entorno virtual
python -m venv venv
```

Activa el entorno virtual:
* **En Windows (CMD / PowerShell):**
  ```bash
  venv\Scripts\activate
  ```
* **En macOS / Linux:**
  ```bash
  source venv/bin/activate
  ```

*(Sabrás que está activado porque verás `(venv)` al inicio de tu línea de comandos).*

---

### 3. Crear el archivo `.env` (Variables de entorno)

Copia la plantilla `.env.example` para generar tu archivo `.env` local:

* **En Windows:**
  ```bash
  copy .env.example .env
  ```
* **En macOS / Linux:**
  ```bash
  cp .env.example .env
  ```

> ⚠️ **IMPORTANTE:** Abre el archivo `.env` recién creado en tu editor (VS Code, Bloc de notas, etc.) y pega tu clave real de Groq:
> ```env
> API_KEY_GROQ=gsk_tu_clave_real_aqui
> ```

---

### 4. Instalar las Dependencias

Con el entorno virtual `(venv)` activado, instala todas las librerías necesarias del proyecto:

```bash
pip install fastapi uvicorn[standard] python-dotenv pydantic langchain-groq langchain-core
```

---

### 5. Ejecutar el Servidor Backend

Inicia el microservicio de FastAPI con recarga en caliente:

```bash
uvicorn app:app --reload
```

* El servidor quedará activo en: `http://127.0.0.1:8000`
* Documentación interactiva de la API (Swagger UI): `http://127.0.0.1:8000/docs`

---

### 6. Probar la Interfaz de Usuario

1. Deja la terminal de `uvicorn` corriendo.
2. Abre el archivo `index.html` en tu navegador favorito (doble clic o usando la extensión *Live Server* en VS Code).
3. ¡Listo! Ya puedes chatear con el agente.

---

## 🌿 Flujo de Trabajo con Git (Para contribuir)

Para trabajar de forma ordenada y no sobreescribir código:

```bash
# 1. Traer los cambios más recientes antes de empezar
git pull origin main

# 2. Crear una rama para tu tarea (ejemplo: feature/historial)
git checkout -b feature/nombre-de-tu-tarea

# 3. Guardar tus avances locales
git add .
git commit -m "feat: descripcion breve de lo que hiciste"

# 4. Subir tu rama a GitHub para revisión
git push -u origin feature/nombre-de-tu-tarea
```

---

## 🐳 Nueva Ejecución con Docker (Entrega 2)

A partir de esta versión, el proyecto está contenerizado. **Ya no es necesario levantar manualmente los servicios con Uvicorn ni lidiar con dependencias locales.**

### 1. Actualizar el repositorio local
Antes de ejecutar cualquier cosa, asegúrate de traer los últimos cambios del equipo:

```bash
git checkout main
git pull origin main

2. Configurar variables de entorno
Verifica que tengas tu archivo .env en la raíz (o en Backend/) con tus credenciales configuradas a partir del archivo .env.example:

GROQ_API_KEY=tu_api_key_aqui

3. Levantar el proyecto con Docker Desktop
Asegúrate de que la aplicación Docker Desktop esté abierta y ejecutándose en segundo plano. Luego, corre el siguiente comando en la terminal:

```bash

docker compose up --build
Nota: La bandera --build compila las imágenes e instala los paquetes necesarios en el contenedor. En las siguientes ejecuciones puedes simplemente usar docker compose up.
# Presiona CTRL + C en la terminal activa, o ejecuta en otra ventana:
docker compose down  (para detener el servicio)