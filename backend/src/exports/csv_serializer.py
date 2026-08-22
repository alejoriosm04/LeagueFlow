"""Serialización CSV compatible con hojas de cálculo."""

import csv
import io
import re
import unicodedata
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass(frozen=True)
class CsvDocument:
    content: bytes
    filename: str
    generated_at: datetime
    media_type: str = "text/csv; charset=utf-8"


def _neutralizar_formula(value: object) -> object:
    if not isinstance(value, str):
        return value
    stripped = value.lstrip()
    if stripped.startswith(("=", "+", "-", "@")):
        prefix = value[: len(value) - len(stripped)]
        return f"{prefix}'{stripped}"
    return value


def _slug(value: str) -> str:
    ascii_value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", ascii_value.lower()).strip("-") or "liga"


def crear_csv(
    *,
    league_name: str,
    resource: str,
    headers: Sequence[str],
    rows: Iterable[Sequence[object]],
    now: Callable[[], datetime] | None = None,
) -> CsvDocument:
    generated_at = (now or (lambda: datetime.now(UTC)))().astimezone(UTC)
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\r\n")
    writer.writerow(["Liga", _neutralizar_formula(league_name)])
    writer.writerow(["Generado en", generated_at.isoformat().replace("+00:00", "Z")])
    writer.writerow([])
    writer.writerow(headers)
    writer.writerows([_neutralizar_formula(value) for value in row] for row in rows)
    filename = f"{_slug(league_name)}-{resource}-{generated_at.date().isoformat()}.csv"
    return CsvDocument(output.getvalue().encode("utf-8-sig"), filename, generated_at)
