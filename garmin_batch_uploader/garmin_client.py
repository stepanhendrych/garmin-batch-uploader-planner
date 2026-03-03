from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from garminconnect import (
    Garmin,
    GarminConnectAuthenticationError,
)
from garminconnect.workout import (
    CyclingWorkout,
    HikingWorkout,
    RunningWorkout,
    SwimmingWorkout,
    WalkingWorkout,
    WorkoutSegment,
    create_warmup_step,
)

from .models import Workout


LOGGER = logging.getLogger(__name__)


class GarminUploaderClient:
    def __init__(
        self,
        user: str,
        password: str,
        dry_run: bool = False,
        tokenstore: str | None = None,
    ) -> None:
        self._user = user
        self._password = password
        self._dry_run = dry_run
        self._tokenstore = tokenstore or "~/.garminconnect"
        self._client: Garmin | None = None

    def login(self) -> None:
        if self._dry_run:
            LOGGER.info("Dry run enabled: skipping Garmin login.")
            return

        tokenstore_path = Path(self._tokenstore).expanduser()

        # Try to load existing session tokens first
        try:
            LOGGER.info("Attempting to use saved session tokens...")
            self._client = Garmin()
            self._client.login(str(tokenstore_path))
            LOGGER.info("Successfully authenticated using saved tokens.")
            return
        except (FileNotFoundError, GarminConnectAuthenticationError) as exc:
            LOGGER.debug(
                "No valid tokens found, will authenticate with credentials: %s", exc
            )

        # Authenticate with credentials (supports MFA)
        LOGGER.info("Logging in with username and password...")
        self._client = Garmin(
            email=self._user,
            password=self._password,
            return_on_mfa=True,
        )
        result1, result2 = self._client.login()

        # Handle MFA if needed
        if result1 == "needs_mfa":
            LOGGER.info("Multi-factor authentication required.")
            mfa_code = input("Enter your MFA code: ").strip()
            LOGGER.info("Submitting MFA code...")
            self._client.resume_login(result2, mfa_code)
            LOGGER.info("MFA authentication successful.")

        # Save tokens for future use
        self._client.garth.dump(str(tokenstore_path))
        LOGGER.info("Session tokens saved to %s", tokenstore_path)
        LOGGER.info("Successfully authenticated to Garmin Connect.")

    def upload_and_schedule(self, workout: Workout) -> dict[str, Any]:
        if self._dry_run:
            LOGGER.info(
                "[DRY-RUN] Would upload and schedule '%s' at %s",
                workout.title,
                workout.scheduled_datetime.isoformat(),
            )
            return {
                "status": "dry-run",
                "title": workout.title,
                "scheduled_for": workout.scheduled_datetime.isoformat(),
            }

        if self._client is None:
            raise RuntimeError("Not authenticated. Call login() first.")

        payload = self._build_workout_payload(workout)

        # Upload workout using the correct API method
        LOGGER.info("Uploading workout: %s", workout.title)
        LOGGER.debug("Workout payload: %s", payload)
        result = self._client.upload_workout(payload)

        workout_id = result.get("workoutId")
        if not workout_id:
            raise RuntimeError(
                f"Failed to create workout, no workoutId returned: {result}"
            )

        LOGGER.info(
            "Successfully created workout '%s' with ID: %s", workout.title, workout_id
        )

        # Note: Garmin Connect API does not support direct workout scheduling to calendar.
        # Users must manually assign workouts to calendar dates in the Garmin Connect UI.
        LOGGER.warning(
            "Workout scheduling not supported by API. "
            "Please assign workout (ID: %s) to %s manually in Garmin Connect.",
            workout_id,
            workout.date.isoformat(),
        )

        return {
            "status": "ok",
            "workout_id": workout_id,
            "title": workout.title,
            "note": "Manual calendar assignment required in Garmin Connect UI",
        }

    @staticmethod
    def _build_workout_payload(workout: Workout) -> dict[str, Any]:
        """Build Garmin-compatible workout payload."""
        duration_seconds = float(max(workout.duration_minutes * 60, 60))

        workout_type_map: dict[str, tuple[type[Any], dict[str, Any]]] = {
            "run": (RunningWorkout, {"sportTypeId": 1, "sportTypeKey": "running"}),
            "running": (RunningWorkout, {"sportTypeId": 1, "sportTypeKey": "running"}),
            "bike": (CyclingWorkout, {"sportTypeId": 2, "sportTypeKey": "cycling"}),
            "cycling": (CyclingWorkout, {"sportTypeId": 2, "sportTypeKey": "cycling"}),
            "walk": (WalkingWorkout, {"sportTypeId": 4, "sportTypeKey": "walking"}),
            "walking": (WalkingWorkout, {"sportTypeId": 4, "sportTypeKey": "walking"}),
            "hike": (HikingWorkout, {"sportTypeId": 17, "sportTypeKey": "hiking"}),
            "hiking": (HikingWorkout, {"sportTypeId": 17, "sportTypeKey": "hiking"}),
            "swim": (SwimmingWorkout, {"sportTypeId": 3, "sportTypeKey": "swimming"}),
            "swimming": (SwimmingWorkout, {"sportTypeId": 3, "sportTypeKey": "swimming"}),
        }

        workout_class, sport_type = workout_type_map.get(
            workout.sport_type,
            (RunningWorkout, {"sportTypeId": 1, "sportTypeKey": "running"}),
        )

        typed_workout = workout_class(
            workoutName=workout.title,
            estimatedDurationInSecs=int(duration_seconds),
            workoutSegments=[
                WorkoutSegment(
                    segmentOrder=1,
                    sportType=sport_type,
                    workoutSteps=[create_warmup_step(duration_seconds)],
                )
            ],
        )

        return typed_workout.to_dict()
