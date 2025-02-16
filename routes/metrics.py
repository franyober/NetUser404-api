from fastapi import APIRouter, Response, status, HTTPException, Header
from config.db import conn
from schemas.metrics import metricEntity, metricsEntity
from models.metrics import Metric
from bson import ObjectId
from starlette.status import HTTP_204_NO_CONTENT
from dotenv import load_dotenv
import os
import json

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

@metric.get('/metrics')
def get_all_metrics(authorization: str = Header(None)):
    #validate_device(authorization)
    return metricsEntity(conn.local.metrics.find())

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

