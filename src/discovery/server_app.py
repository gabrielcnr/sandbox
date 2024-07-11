import fastapi

from discovery.core import ServiceId, ServiceInfoDict
from discovery.service_discovery import ServiceDiscovery

service_discovery = ServiceDiscovery()

app = fastapi.FastAPI()


@app.post('/update/{service_id}')
def update_service(service_id: ServiceId, service_params: dict):
    service_discovery.set(service_id, service_params)


@app.get('/get/{service_id}')
def get_service(service_id: ServiceId) -> ServiceInfoDict:
    return service_discovery.get(service_id)
