from typing import Mapping
from pathlib import Path
from functools import cached_property
from .schema import Schema, TASK_SCHEMA_TYPE

SUBSYSTEM_BASED_SCHEMA_PATH = Path("schema/subsystem_based_schema.json")

class SubsystemBasedSchema(Schema):
    def __init__(self, path: Path = SUBSYSTEM_BASED_SCHEMA_PATH) -> None:
        super().__init__(path)
    
    @cached_property
    def tasks(self) -> Mapping[str, TASK_SCHEMA_TYPE]:
        return self._schema
    

