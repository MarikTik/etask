from typing import Mapping
from pathlib import Path
from functools import cached_property
from .schema import Schema, TASK_SCHEMA_TYPE

CUSTOM_SCHEMA_PATH = Path("schema/custom_schema.json")

class CustomSchema(Schema):
    def __init__(self, path: Path = CUSTOM_SCHEMA_PATH) -> None:
        super().__init__(path)
    
    @cached_property
    def tasks(self) -> Mapping[str, TASK_SCHEMA_TYPE]:
        return self._schema
    

