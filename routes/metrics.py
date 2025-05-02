from fastapi import APIRouter
from fastapi import Query
from config.db import metrics, conn
from schemas.metrics import MetricIn, MetricOut, metricEntity, metricsEntity
from dotenv import load_dotenv
from typing import Optional, List
import codecs
import re
from collections import defaultdict
from datetime import datetime, timedelta

# Cargar las variables del archivo .env
load_dotenv()

metric = APIRouter()

def match_filter(date: str, bssid: str, url: Optional[str] = None, mac: Optional[str] = None):
    match = {"date": date, "bssid": bssid}
    if url:
        match["url"] = url
    if mac:
        match["MAC"] = mac
    return match

def clean_ssid(ssid_str):
    try:
        return codecs.decode(ssid_str.encode('utf-8').decode('unicode_escape').encode('latin1'), 'utf-8')
    except Exception:
        return ssid_str

# Nuevos endpoints con filtros
@metric.get('/macs_by_bssid')
def get_macs_by_bssid(bssid: str):
    pipeline = [
        {"$match": {"bssid": bssid, "MAC": {"$nin": ["N/A", "string"]}}},
        {"$group": {"_id": "$MAC"}}
    ]
    return {"MAC_list": [doc["_id"] for doc in metrics.aggregate(pipeline)]}

@metric.get('/bssids_by_mac')
def get_bssids_by_mac(mac: str):
    pipeline = [
        {"$match": {"MAC": mac, "bssid": {"$nin": ["N/A", "string"]}}},
        {"$group": {"_id": "$bssid"}}
    ]
    return {"network": [doc["_id"] for doc in metrics.aggregate(pipeline)]}

@metric.get('/networks')
def get_networks():
    
    pipeline = [
        {"$match": {"bssid": {"$nin": ["N/A","string"]}}}, 
        {"$group": {"_id": "$bssid"}},
        #{"$project": {"_id": 0, "bssid": "$_id"}}
    ]
    
    networks = [clean_ssid(item["_id"]) for item in metrics.aggregate(pipeline)]
    return {"network": networks}

@metric.get('/MAC_list')
def get_mac_list():
        
    pipeline = [
            {"$match": {"MAC": {"$nin": ["N/A", "string"]}}},
            {"$group": {"_id": "$MAC"}},

    ]
    
    MAC_list = [item["_id"] for item in metrics.aggregate(pipeline)]
    return {"MAC_list": MAC_list}


@metric.get('/pages')
def get_pages():
    
    pipeline = [
        {"$match": {"url": {"$nin": ["N/A","string"]}}}, 
        {"$group": {"_id": "$url"}},
        
    ]
    
    pages = [item["_id"] for item in metrics.aggregate(pipeline)]
    return {"pages": pages}

@metric.get("/metrics/status_code")
def get_errors_count(date: str, bssid: str, url: str, mac:Optional[str]=Query(None)):

    match = match_filter(date, bssid, url, mac)

    pipeline = [
        {"$match": match},  # Filtrar por fecha
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}  # Agrupar por código HTTP y contar
    ]

    resultados = list(metrics.aggregate(pipeline))

    # Convertir resultados en un diccionario {codigo: cantidad}
    conteo_por_codigo = [{"status": item["_id"], "count": item["count"]} for item in resultados]

    return conteo_por_codigo

@metric.get('/metrics/load')
def get_load_time(date: str, bssid: str, url: str, mac: Optional[str] = Query(None)):

    match = match_filter(date, bssid, url, mac)

    registros = metrics.find(
        match,  # Filtrar por fecha
        {"hour": 1, "load": 1, "_id": 0}  # Solo obtener hour y delay
    )
    registros_list = list(registros)

    return registros_list

#------------------------------------------------------------------------------
@metric.get('/metrics/latency')
def get_delay(date: str, bssid: str, mac: Optional[str] = Query(None)):

    match = match_filter(date, bssid, url=None, mac=mac)

    registros = metrics.find(
        match,  # Filtrar por fecha
        {"hour": 1, "delay": 1, "_id": 0}  # Solo obtener hour y delay
    )
    registros_list = list(registros)

    return registros_list

@metric.get('/metrics/download')
def get_download(date: str, bssid: str, mac: Optional[str] = Query(None)):

    match = match_filter(date, bssid, url=None, mac=mac)

    registros = metrics.find(
        match,
        {"hour": 1, "download": 1, "_id": 0}
    )

    bloques = defaultdict(list)

    for r in registros:
        hora = r["hour"]
        velocidad = r.get("download", 0)

        try:
            t = datetime.strptime(hora, "%H:%M:%S")
            bloque_clave = (t.hour * 60 + t.minute) // 5  # Agrupar cada 5 min
            bloques[bloque_clave].append(velocidad)
        except:
            continue  # Ignorar formatos incorrectos

    resultado = []
    for bloque, valores in sorted(bloques.items()):
        promedio = sum(valores) / len(valores)
        minutos = bloque * 5
        hora_formateada = (datetime(1900, 1, 1) + timedelta(minutes=minutos)).strftime("%H:%M:%S")
        resultado.append({
            "hour": hora_formateada,
            "download": round(promedio, 2)
        })

    return resultado

@metric.get('/metrics/comments')
def get_comments_ranges(date: str, bssid: str, mac: Optional[str] = Query(None)):
    match = {"date": date, "bssid": bssid}
    if mac:
        match["MAC"] = mac

    # Obtener registros ordenados por hora
    registros = list(metrics.find(
        match,
        {"hour": 1, "comment": 1, "_id": 0}
    ).sort("hour", 1))

    # Función para extraer comentarios individuales
    def extraer_comentarios(texto):
        return re.findall(r'\[(.*?)\]', texto)

    comentarios_activos = {}
    resultados = []

    for reg in registros:
        hora = reg["hour"]
        comentarios_actuales = extraer_comentarios(reg.get("comment", ""))

        # Marcar comentarios que continúan activos
        comentarios_en_este_registro = set()

        for comentario in comentarios_actuales:
            comentarios_en_este_registro.add(comentario)
            if comentario not in comentarios_activos:
                # Nuevo comentario detectado: abrir rango
                comentarios_activos[comentario] = {"Inicio": hora}

        # Detectar comentarios que desaparecieron
        comentarios_a_cerrar = []
        for comentario in comentarios_activos:
            if comentario not in comentarios_en_este_registro:
                # Este comentario ya no aparece: cerrar el rango
                resultado = {
                    "Comentario": comentario,
                    "Inicio": comentarios_activos[comentario]["Inicio"],
                    "Final": hora
                }
                resultados.append(resultado)
                comentarios_a_cerrar.append(comentario)

        for comentario in comentarios_a_cerrar:
            comentarios_activos.pop(comentario)

    # Cerrar comentarios activos restantes al final
    for comentario, rango in comentarios_activos.items():
        resultados.append({
            "Comentario": comentario,
            "Inicio": rango["Inicio"],
            "Final": registros[-1]["hour"]  # Finalizamos en la última hora conocida
        })

    return resultados


#------------------------------------POST-------------------------------------
@metric.post("/metric", response_model=MetricOut)
def add_metric(metric: MetricIn):
    new_metric = dict(metric)
    del new_metric["id"]
    id = metrics.insert_one(new_metric).inserted_id
    metric = metrics.find_one({"_id": id})
    return metricEntity(metric)



@metric.post('/metrics', response_model=List[MetricOut])
def add_metrics(metrics_list: list[MetricIn]):
    new_metrics = [dict(metric) for metric in metrics_list]

    # Eliminar la clave "id" de cada métrica (si existe)
    for metric in new_metrics:
        metric.pop("id", None)

    # Insertar en MongoDB
    inserted = metrics.insert_many(new_metrics)

    inserted_docs = list(metrics.find({"_id": {"$in": inserted.inserted_ids}}))

    return [metricEntity(metric) for metric in inserted_docs]  # ← Esta es la línea clave

#----------------------
@metric.get("/check-mongodb")
def check_mongodb():
    try:
        # Intentar hacer ping al servidor de MongoDB
        conn.admin.command('ping')
        return 1 
    except:
        return 0
