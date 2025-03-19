
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
