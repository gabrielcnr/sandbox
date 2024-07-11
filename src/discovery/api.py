import requests

from discovery.core import ServiceId, ServiceInfoDict, ServiceParams

class DiscoveryClient:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

    @property
    def base_url(self) -> str:
        return f'http://{self.host}:{self.port}'

    def get_service(self, service_id: ServiceId) -> ServiceInfoDict:
        resp = requests.get(f'{self.base_url}/get/{service_id}')
        resp.raise_for_status()
        return resp.json()

    def update_service(self, service_id: ServiceId, params: ServiceParams) -> None:
        resp = requests.post(f'{self.base_url}/update/{service_id}', json=params)
        resp.raise_for_status()


client = DiscoveryClient('localhost', 8000)
