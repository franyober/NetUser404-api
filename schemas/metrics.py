
def metricEntity(item) -> dict:
    return {
            "id": item["id"],
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
            "delay": item["delay"]
            }


