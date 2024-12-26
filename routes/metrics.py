from fastapi import APIRouter

metric = APIRouter()

@metric.get('/metrics')
def get_all_metrics():
    return "hello world"

@metric.get('/metrics/{id}')
def find_metric():
    return

@metric.post('/metrics')
def post_metric():
    return 

@metric.put('/metrics/{id}')
def update_metric():
            return

@metric.delete('/metrics/{id}')
def remove_metric():
    return
