from fastapi import FastAPI, HTTPException, Security, Depends, Request
from fastapi.security.api_key import APIKeyHeader, APIKey
from starlette.status import HTTP_403_FORBIDDEN, HTTP_429_TOO_MANY_REQUESTS
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import BaseModel
import joblib
import uvicorn
from typing import List
import numpy as np
import os

# Configurar el limiter
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="API Predicción de Stock")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configurar API Key
API_KEY = os.getenv('API_KEY', 'tu-api-key-secreta-por-defecto')
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if not api_key_header or api_key_header != API_KEY:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, 
            detail="API Key inválida o no proporcionada"
        )
    return api_key_header

# Cargar el modelo
modelo = joblib.load("modelo_entrenado.pkl")

class ProductoInput(BaseModel):
    ventas_ultimos_7_dias: int
    stock_actual: int

class ProductosInput(BaseModel):
    productos: List[ProductoInput]

@app.post("/predecir/individual")
@limiter.limit("5/minute")  # 5 llamadas por minuto
async def predecir_individual(
    request: Request,
    producto: ProductoInput, 
    api_key: APIKey = Depends(get_api_key)
):
    try:
        prediccion = modelo.predict([[
            producto.ventas_ultimos_7_dias,
            producto.stock_actual
        ]])[0]
        
        return {
            "falta_stock_predicha": bool(prediccion),
            "datos_entrada": producto.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predecir/batch")
@limiter.limit("2/minute")  # 2 llamadas por minuto para batch
async def predecir_batch(
    request: Request,
    datos: ProductosInput, 
    api_key: APIKey = Depends(get_api_key)
):
    try:
        X = np.array([[p.ventas_ultimos_7_dias, p.stock_actual] for p in datos.productos])
        predicciones = modelo.predict(X)
        
        return {
            "predicciones": [bool(p) for p in predicciones],
            "total_registros": len(predicciones),
            "productos_en_riesgo": int(sum(predicciones))
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
@limiter.limit("10/minute")  # 10 llamadas por minuto para health check
async def health_check(request: Request):
    return {"status": "ok", "modelo_cargado": modelo is not None}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 