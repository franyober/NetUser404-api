from fastapi import FastAPI
from routes.metrics import metric   

app = FastAPI()

app.include_router(metric)




