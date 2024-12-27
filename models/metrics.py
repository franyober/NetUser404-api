from typing import Optional
from pydantic import BaseModel


class Metric(BaseModel):
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
