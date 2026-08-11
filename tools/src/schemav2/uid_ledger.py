"""The sticky record of which uid each task owns.

A task's uid is a **wire identifier**: it is what a peer (the Python receiver,
another board) puts in a request and matches in a reply. Derived uids used to be
a pure function of the schema — a blake2b hash of the task's dotted path, folded
into a width chosen from the current task *count*. That makes them stable only as
long as the schema never grows past a byte boundary and no path-hash collision
gets probed differently: adding the 257th task re-derives **every** implicit uid
at a wider digest, silently renumbering a live protocol.

The ledger removes the derivation from the equation for any task that already has
a uid. Generation is now: *look it up; only compute one if this path has never had
one.* The hash is just the seed for brand-new tasks.

## The file

JSON, next to the schema by default (``.<schema>.uids.json`` - a dotfile: it is
generator-maintained bookkeeping, not something to hand-edit), **meant to be
committed** — it is as much a part of the wire contract as the schema itself.

```json
{
  "version": 1,
  "uid_bytes": 2,
  "uids":    { "arm.shoulder.move": 4321 },
  "retired": { "arm.shoulder.wave": 9002 }
}
```

- ``uid_bytes`` only ever grows. A schema that shrinks back under a byte boundary
  keeps the wider width, because narrowing it would renumber every task that a
  peer already knows.
- ``uids`` are the tasks in the current schema.
- ``retired`` are paths that were in the schema once and no longer are. Their ids
  stay **reserved**, so a new task never inherits an id an old peer still
  associates with a task that no longer exists. Reclaiming one is deliberate:
  delete the entry (or the file) by hand.

A uid that moves anyway — because the schema now pins that number to a different
task with an explicit ``uid:`` — is reported as a warning rather than applied
silently; see :meth:`UidLedger.warnings`.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Union

_VERSION = 1


@dataclass
class UidLedger:
    """The uid assignments carried over from previous runs.

    Instances are cheap and side-effect free; :meth:`load` and :meth:`save` are
    the only file access, and a missing file simply yields an empty ledger (the
    first run of a project).
    """

    uid_bytes: Optional[int] = None
    uids: Dict[str, int] = field(default_factory=dict)
    retired: Dict[str, int] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)

    # ------------------------------------------------------------------- io

    @staticmethod
    def load(path: Union[str, Path]) -> "UidLedger":
        """Reads a ledger, or returns an empty one when the file does not exist."""
        path = Path(path)
        if not path.exists():
            return UidLedger()
        data = json.loads(path.read_text())
        if not isinstance(data, dict):
            raise ValueError(f"{path}: uid ledger must be a JSON object")
        version = data.get("version", _VERSION)
        if version != _VERSION:
            raise ValueError(
                f"{path}: uid ledger version {version} is not supported by this "
                f"generator (expected {_VERSION})"
            )
        return UidLedger(
            uid_bytes=data.get("uid_bytes"),
            uids=UidLedger.__parse_map(data.get("uids", {}), path, "uids"),
            retired=UidLedger.__parse_map(data.get("retired", {}), path, "retired"),
        )

    def save(self, path: Union[str, Path]) -> None:
        """Writes the ledger, sorted by path so diffs stay readable."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "version": _VERSION,
            "uid_bytes": self.uid_bytes,
            "uids": {key: self.uids[key] for key in sorted(self.uids)},
            "retired": {key: self.retired[key] for key in sorted(self.retired)},
        }
        path.write_text(json.dumps(payload, indent=2) + "\n")

    @staticmethod
    def __parse_map(raw: object, path: Path, field_name: str) -> Dict[str, int]:
        if not isinstance(raw, dict):
            raise ValueError(f"{path}: '{field_name}' must be a JSON object")
        parsed: Dict[str, int] = {}
        for key, value in raw.items():
            if not isinstance(value, int) or isinstance(value, bool):
                raise ValueError(f"{path}: '{field_name}.{key}' must be an integer uid")
            parsed[str(key)] = value
        return parsed

    # -------------------------------------------------------------- queries

    def known(self, path: str) -> Optional[int]:
        """The uid this path already owns (live or retired), if any."""
        if path in self.uids:
            return self.uids[path]
        return self.retired.get(path)

    def reserved(self) -> Dict[int, str]:
        """Every uid the ledger accounts for, mapped back to its path."""
        taken: Dict[int, str] = {uid: path for path, uid in self.retired.items()}
        taken.update({uid: path for path, uid in self.uids.items()})
        return taken

    def width(self, needed_bytes: int) -> int:
        """The uid width to use: never narrower than what was used before."""
        return max(needed_bytes, self.uid_bytes or 0)

    # -------------------------------------------------------------- updates

    def warn(self, message: str) -> None:
        """Records a uid movement for the caller to surface."""
        self.warnings.append(message)

    def rekey(self, old_path: str, new_path: str) -> bool:
        """Moves an entry to a new path, keeping its uid (used by ``rename``).

        A rename is the one edit that changes a task's path while meaning "the
        same task" — without this, the renamed task would look brand new and be
        handed a fresh uid, breaking the wire for a purely cosmetic change.

        Sub-paths are moved too, so renaming a scope carries its tasks along.

        @return ``True`` if anything moved.
        """
        moved = False
        for table in (self.uids, self.retired):
            for path in [key for key in table if key == old_path or key.startswith(old_path + ".")]:
                table[new_path + path[len(old_path):]] = table.pop(path)
                moved = True
        return moved

    def record(self, live: Dict[str, int], uid_bytes: int) -> None:
        """Replaces the live set, retiring any path that is no longer in it."""
        for path, uid in self.uids.items():
            if path not in live:
                self.retired[path] = uid
        for path in live:
            self.retired.pop(path, None)
        self.uids = dict(live)
        self.uid_bytes = uid_bytes
