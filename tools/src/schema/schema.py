# SPDX-License-Identifier: BSL-1.1
# -*- coding: utf-8 -*-

import json
from pathlib import Path
from typing import Any, Dict, Type, Mapping
from abc import ABC, abstractmethod
from ctypes import c_uint8, c_uint16, c_uint32, c_uint64
from functools import cached_property
from .schema_error import SchemaError, SchemaKeyError, SchemaValueError
from utils import require

TASK_SCHEMA_TYPE = Dict[str, Any]

class Schema(ABC):
    """
    Base schema loader/validator.

    Exposes:
      - tasks: Mapping[str, TASK_SCHEMA_TYPE]  (must be provided by subclasses)
      - task_uid_type: a ctypes unsigned integer type chosen by max uid
    """
    def __init__(self, path: Path) -> None:
        try:
            with path.open("r", encoding="utf-8") as schema_file:
                self._schema: Mapping[str, Any] = json.load(schema_file)
        except FileNotFoundError as e:
            raise SchemaError(f"Schema file not found: {path}") from e
        except json.JSONDecodeError as e:
            raise SchemaError(f"Invalid JSON in: {path}") from e
        self._validate()

    @cached_property
    @abstractmethod
    def tasks(self) -> Mapping[str, TASK_SCHEMA_TYPE]:
        """Subclasses must expose a mapping of task_name -> task_def dicts."""
        raise NotImplementedError
    
    @cached_property
    def task_uid_type(self) -> Type[c_uint8] | Type[c_uint16] | Type[c_uint32] | Type[c_uint64]:
        max_uid_task: TASK_SCHEMA_TYPE = max(self.tasks.values(), key=lambda task: int(task["uid"]))
        max_uid = int(max_uid_task["uid"]) 
        
        if max_uid <= 0xff:
            return c_uint8
    
        if max_uid < 0xffff:
            return c_uint16

        if max_uid < 0xffff_ffff:
            return c_uint32

        if max_uid < 0xffff_ffff_ffff_ffff:
            return c_uint64    

        raise SchemaValueError(
            "Task uids must be unsigned integers in range [0, 2 ^ 64)",
            "uid",
            max_uid
        )
    
    def __getitem__(self, key) -> Any:
        return self._schema[key]
    
    def _validate(self) -> None:
        #### Validate schema

        require(bool(self._schema),
                SchemaError("Empty schema"))

        require(isinstance(self.tasks, Mapping),
                SchemaError("`tasks` must be a mapping"))
        for task_name, task in self.tasks.items():

            #### Validate uid
            require("uid" in task,
                    SchemaKeyError(message="uid absent", key="uid", field=task_name))
            
            require("params" in task,
                    SchemaKeyError(message="params absent", key="params", field=task_name))
            require("return" in task,
                    SchemaKeyError(message="return absent", key="return", field=task_name))

            uid, params, returns = task["uid"], task["params"], task["return"]

            if isinstance(uid, str):
                try:
                    _ = int(uid)
                except ValueError:
                    raise SchemaValueError("Unable to convert string uid to integer", task_name, uid)
            
            elif not isinstance(uid, int):
                raise SchemaValueError("UID values must be integers or strings representing integers", task_name, uid)
            

            #### Validate params
            require(isinstance(params, dict),
                    SchemaValueError(
                        "Parameters signature of a task must be a dictioanry with keys being the parameters name, and values as their type",
                        task_name,
                        params
                    ))

            #### Validate return
            require(isinstance(returns, dict),
                    SchemaValueError(
                        "Return signature of a task should be a dictionary with keys being the return value name, and values as their type",
                        task_name,
                        returns
                    ))


            

            
            
            



        