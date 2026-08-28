from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class Freshness:
    """Whether a project's generated code still matches its schema.

    A build must never quietly rewrite files a user has open, and it must never
    quietly compile against generated code that no longer matches the schema.
    Those pull in opposite directions, so the build does neither: it *checks*,
    and stops with instructions if the answer is no.

    The check is deliberately a timestamp comparison rather than a re-render.
    Re-rendering to compare would be exact, but it means running the whole
    generator on every build of every target - and the answer it gives is the
    same one in every case that matters, because the generated files are only
    ever written by the generator.
    """

    #: Generated files that do not exist at all.
    missing: List[Path] = field(default_factory=list)
    #: Generated files older than the schema that produced them.
    stale: List[Path] = field(default_factory=list)
    #: The schema everything was compared against.
    schema: Optional[Path] = None

    @property
    def is_fresh(self) -> bool:
        """Whether the build may proceed without regenerating."""
        return not self.missing and not self.stale

    def report(self, regenerate_hint: str) -> str:
        """A message telling the user exactly what is wrong and what to run.

        @param regenerate_hint The command that fixes it, phrased for whichever
               build system is asking (they differ, and a user pasting the wrong
               one is a bad first experience).
        """
        lines: List[str] = []
        if self.missing:
            lines.append("etask: generated code is missing:")
            lines.extend(f"         {path}" for path in self.missing)
        if self.stale:
            lines.append(f"etask: {self.schema} is newer than the code generated from it:")
            lines.extend(f"         {path}" for path in self.stale)
        lines.append("")
        lines.append("       The build will not regenerate on its own - that would rewrite")
        lines.append("       files while you are working in them. Run:")
        lines.append("")
        lines.append(f"         {regenerate_hint}")
        lines.append("")
        lines.append("       ...then build again. Only generated sections are rewritten;")
        lines.append("       your task bodies and contexts are never touched.")
        return "\n".join(lines)

    @staticmethod
    def check(schema: Path, generated: List[Path]) -> "Freshness":
        """Compares a schema against the files generated from it.

        @param schema    The project's schema.
        @param generated Every always-regenerated output (task ids, task lists,
               scope accessors, client bindings). Scaffolds are deliberately not
               included: they are generate-once and user-owned, so being older
               than the schema is their normal state.

        @return What is missing or stale, if anything.
        """
        result = Freshness(schema=schema)
        if not schema.exists():
            return result

        schema_mtime = schema.stat().st_mtime
        for path in generated:
            if not path.exists():
                result.missing.append(path)
            elif path.stat().st_mtime < schema_mtime:
                result.stale.append(path)
        return result
