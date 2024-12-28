from pymongo import MongoClient
import json

with open("config.json") as f:
    config = json.load(f)
server_url = config["server_url"]
print(server_url)
conn = MongoClient(f"mongodb://{server_url}:27017")


