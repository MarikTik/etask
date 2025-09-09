from .schema_error import *
from .schema import *
from .task_only_schema import *
from .device_based_schema import *
from .subsystem_based_schema import *
from .custom_schema import *

def get_schema(path: Path | str) -> Schema:
    if isinstance(path, str):
        path = Path(path)
    
    path_to_schema = {
        TASK_ONLY_SCHEMA_PATH : TaskOnlySchema(),
        DEVICE_BASED_SCHEMA_PATH : DeviceBasedSchema(),
        SUBSYSTEM_BASED_SCHEMA_PATH : SubsystemBasedSchema(),
        CUSTOM_SCHEMA_PATH : CustomSchema()
    }

    require(path in path_to_schema,
            SchemaError(f"Invalid schema path: {path}"))
    
    return path_to_schema[path]

