from fastapi import APIRouter, Response, status, HTTPException, Header
from config.db import conn
from schemas.metrics import metricEntity, metricsEntity
from models.metrics import Metric
from bson import ObjectId
from starlette.status import HTTP_204_NO_CONTENT
from dotenv import load_dotenv
import os
import json
from collections import defaultdict
import statistics

# Cargar las variables del archivo .env
load_dotenv()

SERVER_KEY = os.getenv("SERVER_KEY")
if not SERVER_KEY:
    raise ValueError("SECRET_KEY no está configurada")

AUTHORIZED_DEVICES = os.getenv("AUTHORIZED_DEVICES")
if not AUTHORIZED_DEVICES:
    raise ValueError("AUTHORIZED_DEVICES no está configurada")

AUTHORIZED_DEVICES = json.loads(AUTHORIZED_DEVICES)

metric = APIRouter()

# Middleware para validar dispositivos autorizados
def validate_device(authorization: str = Header(None)):
    if authorization not in AUTHORIZED_DEVICES.values():
        raise HTTPException(status_code=403, detail="Dispositivo no autorizado")


@metric.get("/metrics/errors-count")
def get_errors_count(date: str, authorization: str = Header(None)):
    # validate_device(authorization)  # Descomentar si es necesario

    pipeline = [
        {"$match": {"date": date}},  # Filtrar por fecha
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}  # Agrupar por código HTTP y contar
    ]

    resultados = list(conn.local.metrics.aggregate(pipeline))

    # Convertir resultados en un diccionario {codigo: cantidad}
    conteo_por_codigo = [{"status": item["_id"], "count": item["count"]} for item in resultados]

    return conteo_por_codigo

@metric.get('/metrics/delay')
def get_delay_5min(date: str):
    registros = conn.local.metrics.find(
        {"date": date},  # Filtrar por fecha
        {"hour": 1, "delay": 1, "_id": 0}  # Solo obtener hour y delay
    )
    print(registros)

    delay_por_5min = defaultdict(list)

    for registro in registros:
        hora = registro["hour"][:2]  # Obtener solo las horas (HH)
        minuto = int(registro["hour"][3:5])  # Obtener los minutos (MM)

        # Redondear el minuto al múltiplo de 5 más cercano hacia abajo 
        minuto_redondeado = minuto // 5 * 5  
        clave = f"{hora}:{minuto_redondeado:02d}"  # Formato HH:MM

        delay_por_5min[clave].append(registro["delay"])

    # Calcular el promedio de delay por cada bloque de 5 minutos
    delay_avg = [{"minute": minuto, "avg_delay": round(statistics.mean(delays), 2)}
                 for minuto, delays in sorted(delay_por_5min.items())]

    return delay_avg

@metric.get('/metrics/{id}')
def find_metric(id: str, authorization: str = Header(None)):
    #validate_device(authorization)
    return metricEntity(conn.local.metrics.find_one({"_id": ObjectId(id)}))

@metric.post('/metrics')
def add_metric(metric: Metric, authorization: str = Header(None)):
    #validate_device(authorization)
    new_metric = dict(metric)
    del new_metric["id"]
    id = conn.local.metrics.insert_one(new_metric).inserted_id
    metric = conn.local.metrics.find_one({"_id": id})
    return metricEntity(metric)

@metric.put('/metrics/{id}')
def update_metric(id: str, metric: Metric, authorization: str = Header(None)):
    #validate_device(authorization)
    updated_metric = dict(metric)
    del updated_metric["id"]
    conn.local.metrics.find_one_and_update(
        {"_id": ObjectId(id)}, {"$set": updated_metric}
    )
    return metricEntity(conn.local.metrics.find_one({"_id": ObjectId(id)}))

@metric.delete('/metrics/{id}')
def remove_metric(id: str, authorization: str = Header(None)):
    #validate_device(authorization)
    conn.local.metrics.find_one_and_delete({"_id": ObjectId(id)})
    return Response(status_code=HTTP_204_NO_CONTENT)

