
# 🤖 Sistema de Predicción de Faltas de Stock

Aplicación interactiva basada en Machine Learning que permite predecir el riesgo de que un producto se quede sin stock, tanto en lote como en tiempo real vía API. Desarrollada como proyecto de portafolio personal.

---

## 🔎 Descripción General

Esta app permite cargar o generar datos de productos (ventas y stock actual), y con un modelo previamente entrenado, predice si un producto corre el riesgo de quedarse sin stock.

Se ofrecen dos modos:
- **Simulación local**: genera datos aleatorios o permite subir CSV.
- **API en tiempo real**: permite consultar predicciones individuales desde una interfaz o cliente externo.

---

## 🧠 Tecnologías utilizadas

| Tecnología       | Uso principal                       |
|-------------------|--------------------------------------|
| Python 3.11       | Lenguaje principal                   |
| Streamlit         | Interfaz web interactiva             |
| Scikit-learn      | Entrenamiento y predicción del modelo |
| Pandas / NumPy    | Manipulación de datos                |
| FastAPI (opcional)| API REST para consultas externas     |
| Docker            | Entorno portable para despliegue     |

---

## 🔢 Estructura del proyecto

```
.
├── app_inferencia.py         # Interfaz Streamlit
├── api_modelo.py             # API para predicción externa (opcional)
├── modelo_entrenado.pkl      # Modelo ML guardado
├── requirements.txt          # Dependencias
├── Dockerfile                # Contenedor principal
├── docker-compose.yml        # Orquestación simple
├── .env                      # Configuración privada (token API, etc.)
```

---

## 💪 Qué resuelve esta app

- Automatiza la detección de productos en riesgo de rotura de stock.
- Permite generar escenarios de prueba con datos aleatorios.
- Visualiza de forma clara el porcentaje de riesgo y los productos afectados.
- Ofrece una API para integrar el modelo en otros sistemas.

---

## 🚀 Cómo ejecutar el proyecto

### Opcion 1: Modo local

1. Crear entorno virtual (opcional pero recomendado):
```bash
python -m venv venv
venv\Scripts\activate
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

3. Ejecutar Streamlit:
```bash
streamlit run app_inferencia.py
```

### Opcion 2: Usar Docker

```bash
docker build -t pred-stock .
docker run -p 8501:8501 pred-stock
```

O con docker-compose:
```bash
docker-compose up --build
```

---

## 🔗 Uso de la app

- En la interfaz puedes:
  - Generar datos de prueba
  - Subir un CSV con datos propios
  - Visualizar resultados y porcentajes de riesgo
  - Descargar el CSV con resultados
  - Probar predicciones unitarias vía API

---

## 🤝 Prueba de la API (FastAPI)

Si ejecutas `api_modelo.py` (requiere FastAPI):

```bash
uvicorn api_modelo:app --reload --port 8000
```

Puedes hacer una petición POST:
```bash
curl -X POST http://localhost:8000/predecir \
     -H "Authorization: Bearer TU_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"ventas_ultimos_7_dias": 10, "stock_actual": 5}'
```

---

## 🚫 Seguridad

- La API está protegida con un token de autenticación
- El modo demo en Streamlit también permite ocultar funciones según una clave

---

## 📈 Capturas (opcional para GitHub)

Puedes incluir tus capturas como las que mostraste (panel lateral, tabla resaltada, prueba API).

---

## 🌟 Autor

Desarrollado por Pablo como parte de su portafolio personal.

---

## ✉️ Contacto

- Email: [tuemail@dominio.com]
- LinkedIn: [linkedin.com/in/tuusuario]

---

## ⚖️ Licencia

Este proyecto está bajo licencia MIT.
