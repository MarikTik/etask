"""The schema code generator: ``schema.yaml`` -> a C++ project and a Python client.

This is the *authoring* half of etask, and the CLI (``etask generate``, ``etask
scaffold``, ``etask rename``) is its front end. It is a subpackage of ``etask``
rather than a separate distribution because the two halves share one wire
contract - the status codes, the value types, and the uid width in
:mod:`etask.schema.uid_ledger` are the same facts the runtime decodes replies
with, and keeping them in one place is what stops them drifting apart.

Its dependencies are *not* the runtime's, though: reading YAML schemas and
validating them against a JSON meta-schema is a build-time concern, so they live
behind an extra::

    pip install etask              # the runtime: an async client, nothing else
    pip install etask[codegen]     # + this package's dependencies and the CLI

Importing anything here without that extra raises a message saying so, rather
than a bare ``ModuleNotFoundError`` for a package the user never asked for.
"""

from __future__ import annotations


def _require_codegen_extra() -> None:
    """Turns a missing build-time dependency into an actionable message."""
    missing = []
    for module, package in (("yaml", "pyyaml"), ("jsonschema", "jsonschema")):
        try:
            __import__(module)
        except ModuleNotFoundError:
            missing.append(package)
    if missing:
        raise ImportError(
            "etask's code generator needs "
            + " and ".join(missing)
            + ", which ship with the 'codegen' extra rather than the runtime: "
            "install them with `pip install etask[codegen]` (or "
            "`pip install -e .[codegen]` from a checkout)."
        )


_require_codegen_extra()

from .models.node import Node, Kind                                    # noqa: E402
from .models.param import Param                                        # noqa: E402
from .models.return_shape import ReturnShape                           # noqa: E402
from .models.status_code import StatusCode                             # noqa: E402
from .models.type_map import TypeMap                                   # noqa: E402
from .errors.duplicate_uid_error import DuplicateUidError              # noqa: E402
from .errors.invalid_identifier_error import InvalidIdentifierError    # noqa: E402
from .errors.unknown_type_error import UnknownTypeError                # noqa: E402
from .errors.unknown_status_error import UnknownStatusError            # noqa: E402
from .errors.schema_shape_error import SchemaShapeError                # noqa: E402
from .errors.abstract_instance_error import AbstractInstanceError      # noqa: E402
from .tree import Tree                                                 # noqa: E402
from .uid_ledger import UidLedger                                      # noqa: E402

__all__ = [
    "AbstractInstanceError",
    "DuplicateUidError",
    "InvalidIdentifierError",
    "Kind",
    "Node",
    "Param",
    "ReturnShape",
    "SchemaShapeError",
    "StatusCode",
    "Tree",
    "TypeMap",
    "UidLedger",
    "UnknownStatusError",
    "UnknownTypeError",
]
