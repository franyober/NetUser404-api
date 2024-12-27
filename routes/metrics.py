from fastapi import APIRouter, Response, status
from config.db import conn
from schemas.metrics import metricEntity, metricsEntity 
from models.metrics import Metric
from bson import ObjectId
from starlette.status import HTTP_204_NO_CONTENT

metric = APIRouter()

@metric.get('/metrics')
def get_all_metrics():
    return metricsEntity(conn.local.metrics.find())

@metric.get('/metrics/{id}')
def find_metric(id: str):
    return metricEntity(conn.local.metrics.find_one({"_id": ObjectId(id)}))

@metric.post('/metrics')
def add_metric(metric: Metric):
    new_metric = dict(metric)
    del new_metric["id"]
    id = conn.local.metrics.insert_one(new_metric).inserted_id
    
    metric = conn.local.metrics.find_one({"_id": id})
    
    return metricEntity(metric)

@metric.put('/metrics/{id}')
def update_metric():
            return

@metric.delete('/metrics/{id}')
def remove_metric(id: str):
    metricEntity(conn.local.metrics.find_one_and_delete({"_id": ObjectId(id)}))
    
    return Response() 

