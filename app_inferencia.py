import streamlit as st
import pandas as pd
import joblib
import numpy as np
import os
import requests

# Definir la URL de la API y función de llamada
API_URL = os.getenv('API_URL', 'http://localhost:8000')
API_KEY = os.getenv('API_KEY', 'tu-api-key-secreta-por-defecto')

def llamar_api(endpoint, datos):
    headers = {"X-API-Key": API_KEY}
    response = requests.post(
        f"{API_URL}/{endpoint}",
        json=datos,
        headers=headers
    )
    
    if response.status_code == 429:
        st.error("❌ Demasiadas solicitudes. Por favor, espera un momento antes de intentar nuevamente.")
        st.stop()
    elif response.status_code == 403:
        st.error("❌ Error de autenticación: API Key inválida")
        st.stop()
    
    return response

st.title("🔍 Predicción de Faltas de Stock")

# Cargar el modelo entrenado
@st.cache_resource
def cargar_modelo():
    return joblib.load("modelo_entrenado.pkl")

def generar_csv_stock(n=30, seed=-1):
    # Si seed es -1, no establecemos ninguna seed específica
    if seed != -1:
        np.random.seed(seed)
    
    producto_id = [f"P{i:04d}" for i in range(1, n + 1)]
    ventas_ultimos_7_dias = np.random.poisson(lam=10, size=n)
    stock_actual = np.random.randint(0, 40, size=n)
    
    df = pd.DataFrame({
        'producto_id': producto_id,
        'ventas_ultimos_7_dias': ventas_ultimos_7_dias,
        'stock_actual': stock_actual,
    })
    
    return df

# Añadimos una sección para generar datos de prueba
st.sidebar.header("🔧 Opciones")
modo_operacion = st.sidebar.radio(
    "Modo de operación",
    ["Datos de prueba", "API","Datos CSV"],
    index=0  # Por defecto selecciona "Datos CSV"
)

# Reemplazamos los if/else basados en los checkboxes anteriores
if modo_operacion == "Datos de prueba":
    n_registros = st.sidebar.slider("Número de registros", 10, 100, 30)
    usar_seed = st.sidebar.checkbox("Usar semilla específica")
    if usar_seed:
        seed_input = st.sidebar.number_input("Semilla aleatoria", value="", placeholder="Ingrese un número...")
        seed = -1 if seed_input == "" else int(seed_input)
    else:
        seed = -1
    
    if st.sidebar.button("Generar nuevos datos"):
        df = generar_csv_stock(n=n_registros, seed=seed)
        st.success(f"✅ Nuevos datos generados {'con semilla ' + str(seed) if seed != -1 else 'aleatoriamente'}")

elif modo_operacion == "API":
    st.header("🔌 Prueba de API")
    col1, col2 = st.columns(2)
    with col1:
        ventas_test = st.number_input("Ventas últimos 7 días", min_value=0, value=10)
    with col2:
        stock_test = st.number_input("Stock actual", min_value=0, value=5)
    
    if st.button("Realizar predicción via API"):
        try:
            response = llamar_api("predecir/individual", {
                "ventas_ultimos_7_dias": int(ventas_test),
                "stock_actual": int(stock_test)
            })
            
            if response.status_code == 200:
                resultado = response.json()
                st.write("Resultado de la API:")
                if resultado["falta_stock_predicha"]:
                    st.warning("⚠️ Producto en riesgo de falta de stock")
                else:
                    st.success("✅ Stock suficiente")
                st.json(resultado)
            else:
                st.error(f"Error en la API: {response.text}")
        except Exception as e:
            st.error(f"Error al conectar con la API: {str(e)}")

else:  # modo_operacion == "Datos CSV"
    archivo = st.file_uploader("📤 Sube tu archivo CSV con productos", type="csv")
    if archivo:
        df = pd.read_csv(archivo)

# Procesamiento de datos y predicción
if 'df' in locals():
    if 'ventas_ultimos_7_dias' in df.columns and 'stock_actual' in df.columns:
        if modo_operacion == "API":
            try:
                # Preparar datos para la API
                datos_api = {
                    "productos": [
                        {
                            "ventas_ultimos_7_dias": int(ventas),
                            "stock_actual": int(stock)
                        }
                        for ventas, stock in zip(df['ventas_ultimos_7_dias'], df['stock_actual'])
                    ]
                }
                
                # Llamar a la API
                response = llamar_api("predecir/batch", datos_api)
                
                if response.status_code == 200:
                    resultado = response.json()
                    pred = resultado["predicciones"]
                    
                    # Mostramos resultados
                    df_resultado = df.copy()
                    df_resultado['falta_stock_predicha'] = pred
                    
                    st.success("✅ Predicción realizada via API")
                else:
                    st.error(f"Error en la API: {response.text}")
                    st.stop()
                    
            except Exception as e:
                st.error(f"Error al conectar con la API: {str(e)}")
                st.stop()
        else:
            # Usar modelo local
            modelo = cargar_modelo()
            X = df[['ventas_ultimos_7_dias', 'stock_actual']]
            pred = modelo.predict(X)
            df_resultado = df.copy()
            df_resultado['falta_stock_predicha'] = pred
            
            st.success("✅ Predicción realizada localmente")
        
        # Resumen estadístico
        col1, col2 = st.columns(2)
        with col1:
            n_productos_riesgo = pred.sum()
            st.metric("Productos en riesgo de falta de stock", 
                     f"{int(n_productos_riesgo)} de {len(pred)}")
        with col2:
            porcentaje_riesgo = (n_productos_riesgo/len(pred)) * 100
            st.metric("Porcentaje en riesgo", f"{porcentaje_riesgo:.1f}%")

        # Tabla con formato condicional
        st.dataframe(
            df_resultado.style.apply(lambda x: ['background-color: rgba(255, 200, 200, 0.5)' if x['falta_stock_predicha'] == 1 
                                            else 'background-color: rgba(200, 255, 200, 0.5)' for i in x], axis=1)
        )

        # Gráfico de barras para productos en riesgo
        st.subheader("📊 Niveles de Stock por Producto")
        productos_riesgo = df_resultado[df_resultado['falta_stock_predicha'] == 1]
        if not productos_riesgo.empty:
            st.bar_chart(
                data=df_resultado.set_index('producto_id')['stock_actual']
            )
        else:
            st.info("¡No se detectaron productos en riesgo de falta de stock!")

        # Descargar CSV (usando df_resultado original)
        csv = df_resultado.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Descargar resultado", csv, "predicciones_stock.csv", "text/csv")
    else:
        st.error("❌ El CSV debe contener las columnas 'ventas_ultimos_7_dias' y 'stock_actual'")
