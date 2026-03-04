from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from .models import Workout


def _parse_segments(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return value
    if value in (None, ""):
        return []
    if isinstance(value, str):
        parsed = json.loads(value)
        if not isinstance(parsed, list):
            raise ValueError("segments JSON must decode to a list.")
        return parsed
    raise ValueError("Unsupported segments format.")


def _load_csv(path: Path) -> list[Workout]:
    workouts: list[Workout] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for line_number, row in enumerate(reader, start=2):
            row["segments"] = _parse_segments(row.get("segments", "[]"))
            try:
                workouts.append(Workout.from_raw(row))
            except ValueError as exc:
                raise ValueError(f"CSV error on line {line_number}: {exc}") from exc
    return workouts


def _load_json(path: Path) -> list[Workout]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("JSON input must be an array of workouts.")

    workouts: list[Workout] = []
    for index, row in enumerate(payload, start=1):
        if not isinstance(row, dict):
            raise ValueError(f"JSON item {index} is not an object.")
        normalized = dict(row)

        if "date" not in normalized and "start_time" in normalized:
            try:
                normalized["date"] = normalized["start_time"].split("T")[0]
            except Exception:
                normalized["date"] = None

        if "start_time" in normalized and "T" in normalized["start_time"]:
            try:
                t_part = normalized["start_time"].split("T")[1].split(":")
                normalized["start_time"] = f"{t_part[0]}:{t_part[1]}"
            except Exception:
                raise ValueError(
                    f"Invalid ISO start_time format in item {index}: {normalized['start_time']}"
                )

        normalized["segments"] = _parse_segments(normalized.get("segments", []))

        if "duration_minutes" not in normalized and "duration" in normalized:
            normalized["duration_minutes"] = normalized["duration"]

        try:
            workouts.append(Workout.from_raw(normalized))
        except ValueError as exc:
            raise ValueError(f"JSON error in item {index}: {exc}") from exc

    return workouts


def load_workouts(input_path: str) -> list[Workout]:
    path = Path(input_path)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    extension = path.suffix.lower()
    if extension == ".csv":
        return _load_csv(path)
    if extension == ".json":
        return _load_json(path)

    raise ValueError("Unsupported file type. Use .csv or .json")
