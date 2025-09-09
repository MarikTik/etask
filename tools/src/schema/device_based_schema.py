from typing import Mapping
from pathlib import Path
from functools import cached_property
from .schema import Schema, TASK_SCHEMA_TYPE

DEVICE_BASED_SCHEMA_PATH = Path("schema/device_based_schema.json")

class DeviceBasedSchema(Schema):
    def __init__(self, path: Path = DEVICE_BASED_SCHEMA_PATH) -> None:
        super().__init__(path)
    
    @cached_property
    def tasks(self) -> Mapping[str, TASK_SCHEMA_TYPE]:
        return self._schema
    

