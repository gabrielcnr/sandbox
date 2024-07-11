import datetime
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Self, TypedDict

type ServiceId = str

type ServiceParams = dict[str, Any]


def seconds_since(dt: datetime.datetime) -> int:
    delta = datetime.datetime.now(tz=datetime.UTC) - dt
    return int(delta.total_seconds())


class ServiceInfoDict(TypedDict):
    params: ServiceParams
    created_at: datetime.datetime
    updated_at: datetime.datetime
    age: int
    elapsed: int


@dataclass
class ServiceInfo:
    params: ServiceParams
    created_at: datetime.datetime
    updated_at: datetime.datetime

    @classmethod
    def create(cls) -> Self:
        now = datetime.datetime.now(tz=datetime.UTC)
        return cls(params={}, created_at=now, updated_at=now)

    def update(self, params: ServiceParams) -> None:
        self.updated_at = datetime.datetime.now(tz=datetime.UTC)
        self.params = params

    @property
    def age(self) -> int:
        return seconds_since(self.created_at)

    @property
    def elapsed(self) -> int:
        return seconds_since(self.updated_at)

    def to_dict(self) -> ServiceInfoDict:
        return ServiceInfoDict(
            params=self.params.copy(),
            created_at=self.created_at,
            updated_at=self.updated_at,
            age=self.age,
            elapsed=self.elapsed,
        )


class ServiceDiscovery:
    services: dict[ServiceId, ServiceInfo]

    def __init__(self):
        self.services = defaultdict(ServiceInfo.create)

    def set(self, service_id: ServiceId, params: ServiceParams) -> None:
        service_info = self.services[service_id]
        service_info.update(params)

    def get(self, service_id: ServiceId) -> ServiceInfoDict:
        service_info = self.services[service_id]
        return service_info.to_dict()
