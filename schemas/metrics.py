from typing import Optional
from pydantic import BaseModel

class MetricIn(BaseModel):
    id: Optional[str] = None
    date: str
    hour: str
    system: str
    MAC: str
    bssid: str
    ip: str
    url: str
    status: int
    load: float
    transferred: float
    delay: float
    download: float
    comment: str

class MetricOut(MetricIn):
    id: str

def metricEntity(item) -> dict:
    return {
            "id": str(item["_id"]),
            "date": item["date"],
            "hour": item["hour"],
            "system": item["system"],
            "MAC": item["MAC"],
            "bssid": item["bssid"],
            "ip": item["ip"],
            "url": item["url"],
            "status": item["status"],
            "load": item["load"],
            "transferred": item["transferred"],
            "delay": item["delay"],
            "download": item["download"],
            "comment": item["comment"]
            }

def metricsEntity(entity) -> list:
    return [metricEntity(item) for item in entity]
