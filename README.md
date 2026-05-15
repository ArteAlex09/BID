# BID 🛡️📊

Proyecto universitario para la clase de **Probabilidad y Estadística**.

## 🎯 Objetivo
Desarrollar una herramienta que calcule la probabilidad $P(M|E)$ de que una dirección IP sea maliciosa utilizando el **Teorema de Bayes**, alimentado por tres datasets distintos y validado contra motores de reputación externos.

## 🛠️ Tecnologías
* **Lenguaje:** Python
* **Modelo:** Inferencia Bayesiana
* **Integraciones:** AbuseIPDB API / VirusTotal API
* **Interfaz:** [Aquí puedes poner Streamlit o FastAPI, según decidas]

## 📈 Lógica Estadística
El sistema evalúa la presencia de una IP en múltiples fuentes de datos y actualiza la probabilidad de amenaza conforme se encuentra evidencia en los datasets locales y externos.

---

## 💻 Requisitos Previos (Para macOS)

Para ejecutar este proyecto en tu Mac, tienes dos opciones: ejecutarlo de manera nativa con Python o usar Docker. 

Si eliges la opción nativa (recomendada), asegúrate de tener instalado:
- **Python 3.9 o superior**: Puedes verificarlo abriendo la `Terminal` y escribiendo `python3 --version`.
- **pip**: El gestor de paquetes de Python (generalmente viene incluido con Python 3).

---

## 🚀 Opción 1: Ejecución Nativa en macOS (Recomendada)

Sigue estos pasos en tu aplicación `Terminal` (`Comando + Espacio` y escribe "Terminal"):

### 1. Navegar a la carpeta del proyecto
Abre la terminal y navega hasta donde descomprimiste este proyecto. Por ejemplo, si está en tus Descargas:

```

```text
Files created and zipped successfully.

```bash
cd ~/Downloads/Proyecto-BID

```

### 2. Crear un Entorno Virtual

Es una buena práctica para no interferir con las librerías de tu Mac:

```bash
python3 -m venv venv

```

### 3. Activar el Entorno Virtual

```bash
source venv/bin/activate

```

*(Notarás que tu terminal ahora dice `(venv)` al inicio de la línea).*

### 4. Instalar las Dependencias

Se ha incluido un archivo `requirements.txt` con todas las librerías necesarias (Streamlit, Pandas, Plotly, Scikit-learn, etc.):

```bash
pip3 install -r requirements.txt

```

### 5. (Opcional) Entrenar el Modelo de Inteligencia Artificial

Si es la primera vez que lo ejecutas o deseas regenerar el modelo de Random Forest con el dataset más reciente:

```bash
python3 entrenar_rf.py

```

### 6. Iniciar la Aplicación

Arranca el servidor web interactivo:

```bash
streamlit run Inicio.py

```

¡Listo! Se abrirá automáticamente una pestaña en tu navegador (Safari o Chrome) en la dirección `http://localhost:8501`.

---

## 🐳 Opción 2: Ejecución mediante Docker

Si prefieres usar contenedores y tienes **Docker Desktop** instalado en tu Mac:

1. Abre la Terminal en la carpeta del proyecto.
2. Construye la imagen (esto descargará las dependencias necesarias):
```bash
docker build -t proyecto-bid .

```


3. Ejecuta el contenedor:
```bash
docker run -p 8501:8501 proyecto-bid

```


4. Abre tu navegador web y entra a: `http://localhost:8501`

---

## 📂 Estructura del Proyecto

* `Inicio.py`: Archivo principal que lanza la interfaz gráfica de la plataforma.
* `pages/`: Contiene los módulos del sistema.
* `1_📡_Analizador.py`: Buscador que ejecuta el modelo bayesiano.
* `2_📊_Dashboard.py`: Análisis descriptivo e interactivo usando One-Hot Encoding.
* `3_🛠️_Herramientas.py`: Herramientas de reporte a bases de datos externas.


* `motor_bayesiano.py`: Núcleo estadístico (Teorema de Bayes, Suavizado de Laplace).
* `requirements.txt`: Lista estricta de dependencias Python.
* `Dockerfile`: Archivo de configuración para despliegue en contenedores.

---

*Proyecto Universitario - Universidad de Guadalajara*

