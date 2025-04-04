from fastapi import APIRouter
from config.db import conn
from schemas.metrics import metricEntity, metricsEntity
from models.metrics import Metric
from dotenv import load_dotenv


# Cargar las variables del archivo .env
load_dotenv()

metric = APIRouter()

@metric.get('/networks')
def get_networks():
    
    pipeline = [
        {"$match": {"bssid": {"$nin": ["N/A","string"]}}}, 
        {"$group": {"_id": "$bssid"}},
        #{"$project": {"_id": 0, "bssid": "$_id"}}
    ]
    
    networks = [item["_id"].replace("\\x20", " ") for item in conn.local.metrics.aggregate(pipeline)]
    return {"network": networks}

@metric.get('/pages')
def get_pages():
    
    pipeline = [
        {"$match": {"url": {"$nin": ["N/A","string"]}}}, 
        {"$group": {"_id": "$url"}},
        
    ]
    
    pages = [item["_id"] for item in conn.local.metrics.aggregate(pipeline)]
    return {"pages": pages}

@metric.get("/metrics/status_code")
def get_errors_count(date: str, bssid: str, url: str):

    pipeline = [
        {"$match": {"date": date, "bssid": bssid, "url": url}},  # Filtrar por fecha
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}  # Agrupar por código HTTP y contar
    ]

    resultados = list(conn.local.metrics.aggregate(pipeline))

    # Convertir resultados en un diccionario {codigo: cantidad}
    conteo_por_codigo = [{"status": item["_id"], "count": item["count"]} for item in resultados]

    return conteo_por_codigo

@metric.get('/metrics/load')
def get_load_time(date: str, bssid: str, url: str):
    registros = conn.local.metrics.find(
        {"date": date, "bssid": bssid, "url": url},  # Filtrar por fecha
        {"hour": 1, "load": 1, "_id": 0}  # Solo obtener hour y delay
    )
    registros_list = list(registros)

    return registros_list

#------------------------------------------------------------------------------
@metric.get('/metrics/latency')
def get_delay(date: str, bssid: str):
    registros = conn.local.metrics.find(
        {"date": date, "bssid": bssid},  # Filtrar por fecha
        {"hour": 1, "delay": 1, "_id": 0}  # Solo obtener hour y delay
    )
    registros_list = list(registros)

    return registros_list

@metric.get('/metrics/download')
def get_download(date: str, bssid: str):
    registros = conn.local.metrics.find(
        {"date": date, "bssid": bssid},  # Filtrar por fecha
        {"hour": 1, "download": 1, "_id": 0}  # Solo obtener hour y delay
    )
    registros_list = list(registros)

    return registros_list

#------------------------------------POST-------------------------------------
@metric.post('/metric')
def add_metric(metric: Metric):
    new_metric = dict(metric)
    del new_metric["id"]
    id = conn.local.metrics.insert_one(new_metric).inserted_id
    metric = conn.local.metrics.find_one({"_id": id})
    return metricEntity(metric)


@metric.post('/metrics')
def add_metrics(metrics: list[Metric]):
    new_metrics = [dict(metric) for metric in metrics]
    
    # Eliminar la clave "id" de cada métrica (si existe)
    for metric in new_metrics:
        metric.pop("id", None)
    
    # Insertar todas las métricas en la base de datos
    inserted = conn.local.metrics.insert_many(new_metrics)
    
    # Recuperar los documentos insertados
    metrics = list(conn.local.metrics.find({"_id": {"$in": inserted.inserted_ids}}))
    
    return [metricEntity(metric) for metric in metrics]

#----------------------
@metric.get("/check-mongodb")
def check_mongodb():
    try:
        # Intentar hacer ping al servidor de MongoDB
        conn.admin.command('ping')
        return 1 
    except:
        return 0
