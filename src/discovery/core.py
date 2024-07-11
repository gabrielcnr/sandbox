import datetime
from typing import TypedDict, Any

type ServiceId = str

type ServiceParams = dict[str, Any]


class ServiceInfoDict(TypedDict):
    params: ServiceParams
    created_at: datetime.datetime
    updated_at: datetime.datetime
    age: int
    elapsed: int
