from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time
from typing import Any


@dataclass(frozen=True)
class Workout:
    date: date
    start_time: time
    title: str
    sport_type: str
    duration_minutes: int
    segments: list[dict[str, Any]]

    @property
    def scheduled_datetime(self) -> datetime:
        return datetime.combine(self.date, self.start_time)

    @classmethod
    def from_raw(cls, raw: dict[str, Any]) -> "Workout":
        try:
            parsed_date = date.fromisoformat(str(raw["date"]))
            parsed_time = time.fromisoformat(str(raw["start_time"]))
            title = str(raw["title"]).strip()
            sport_type = str(raw["sport_type"]).strip().lower()
            duration_minutes = int(raw["duration_minutes"])
            segments = raw.get("segments", [])
        except KeyError as exc:
            raise ValueError(f"Missing required field: {exc.args[0]}") from exc
        except Exception as exc:
            raise ValueError(f"Invalid workout row: {raw}") from exc

        if not title:
            raise ValueError("Workout title cannot be empty.")
        if duration_minutes <= 0:
            raise ValueError("duration_minutes must be greater than 0.")
        if not isinstance(segments, list):
            raise ValueError("segments must be an array/list.")

        return cls(
            date=parsed_date,
            start_time=parsed_time,
            title=title,
            sport_type=sport_type,
            duration_minutes=duration_minutes,
            segments=segments,
        )

    @property
    def formatted_title(self) -> str:
        """Return a filename-friendly title in the format: "title - date (DD. MM. YYYY)".

        Example: "Morning Run - 03. 03. 2026"
        """
        return f"{self.title} - {self.date.strftime('%d. %m. %Y')}"
