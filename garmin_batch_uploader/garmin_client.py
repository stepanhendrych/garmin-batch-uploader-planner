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
        
        try:
            result = self._client.upload_workout(payload)
        except Exception as e:
            LOGGER.error("Upload failed. Payload: %s", payload)
            raise

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
        """Build Garmin-compatible workout payload from workout segments."""
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

        # Build steps from all workout segments
        workout_steps = []
        step_order = 1

        def _build_step(segment: dict, step_order: int, is_nested: bool = False) -> tuple[dict, int]:
            """Build a single step from a segment. Returns (step_dict, new_step_order)."""
            seg_type = str(segment.get("type", "steady")).lower()
            
            # Map segment types to Garmin step types
            # Valid step types: 1=warmup, 2=cooldown, 3=interval, 4=recovery, 5=rest, 6=repeat, 7=other
            step_type_map = {
                "warmup": (1, "warmup"),
                "cooldown": (2, "cooldown"),
                "interval": (3, "interval"),
                "recovery": (4, "recovery"),
                "rest": (5, "rest"),
                "steady": (3, "interval"),  # Steady efforts are intervals in Garmin
                "other": (7, "other"),
            }
            
            step_type_id, step_type_key = step_type_map.get(seg_type, (6, "exercise"))
            
            # Determine duration/end condition
            end_condition_value = None
            end_condition = None
            
            if "end_condition" in segment:
                ec = segment["end_condition"]
                ec_type = ec.get("type", "time").lower()
                
                if ec_type == "distance":
                    value_km = float(ec.get("value", 0))
                    end_condition_value = value_km * 1000  # Convert to meters
                    end_condition = {
                        "conditionTypeId": 3,
                        "conditionTypeKey": "distance",
                        "displayOrder": 3,
                        "displayable": True
                    }
                elif ec_type == "calories":
                    end_condition_value = float(ec.get("value", 0))
                    end_condition = {
                        "conditionTypeId": 4,
                        "conditionTypeKey": "calories",
                        "displayOrder": 4,
                        "displayable": True
                    }
                elif ec_type == "heart.rate":
                    end_condition_value = float(ec.get("value", 0))
                    operator = ec.get("operator", "lt")
                    end_condition = {
                        "conditionTypeId": 6,
                        "conditionTypeKey": "heart.rate",
                        "displayOrder": 6,
                        "displayable": True,
                        "conditionCompare": operator
                    }
                elif ec_type == "lap.button":
                    end_condition_value = 1
                    end_condition = {
                        "conditionTypeId": 1,
                        "conditionTypeKey": "lap.button",
                        "displayOrder": 1,
                        "displayable": True
                    }
                else:  # Default to time
                    end_condition_value = float(segment.get("duration", 0)) * 60
                    end_condition = None
            else:
                # Use duration-based time
                if seg_type == "interval":
                    end_condition_value = float(segment.get("work", 0)) * 60
                elif seg_type == "recovery":
                    end_condition_value = float(segment.get("rest", 0)) * 60
                else:
                    end_condition_value = float(segment.get("duration", 0)) * 60
            
            # Create base step
            step_obj = create_warmup_step(end_condition_value, step_order=step_order)
            
            # For nested steps in repeat groups, don't include None target fields
            if is_nested:
                step_dict = step_obj.model_dump(exclude_none=True)
            else:
                step_dict = step_obj.model_dump(exclude_none=True)
            
            # Override step type if not warmup
            if step_type_id != 1:
                step_dict["stepType"] = {
                    "stepTypeId": step_type_id,
                    "stepTypeKey": step_type_key,
                    "displayOrder": step_type_id,
                }
            
            # Override end condition if specified
            if end_condition:
                step_dict["endCondition"] = end_condition
                step_dict["endConditionValue"] = end_condition_value
            
            # Handle target if specified
            if "target" in segment and segment["target"]:
                target = segment["target"]
                target_type_str = target.get("type", "no.target").lower()
                
                # Map target types to Garmin IDs
                target_type_map = {
                    "no.target": (1, "no.target"),
                    "speed.zone": (2, "speed.zone"),
                    "cadence": (3, "cadence"),
                    "heart.rate.zone": (4, "heart.rate.zone"),
                    "power.zone": (5, "power.zone"),
                    "pace.zone": (6, "pace.zone"),
                    "heart.rate": (8, "heart.rate"),
                    "power": (9, "power"),
                    "pace": (10, "pace"),
                    "speed": (11, "speed"),
                }
                
                target_id, target_key = target_type_map.get(target_type_str, (1, "no.target"))
                
                step_dict["targetType"] = {
                    "workoutTargetTypeId": target_id,
                    "workoutTargetTypeKey": target_key,
                    "displayOrder": target_id,
                }
                
                # Set zone number or value range
                if "zoneNumber" in target:
                    step_dict["zoneNumber"] = int(target["zoneNumber"])
                    step_dict["targetValueOne"] = None
                    step_dict["targetValueTwo"] = None
                elif "valueOne" in target and "valueTwo" in target:
                    step_dict["targetValueOne"] = float(target["valueOne"])
                    step_dict["targetValueTwo"] = float(target["valueTwo"])
                    step_dict["zoneNumber"] = None
                else:
                    step_dict["zoneNumber"] = None
                    step_dict["targetValueOne"] = None
                    step_dict["targetValueTwo"] = None
            
            return step_dict, step_order + 1

        def _process_segment(segment: dict, step_order: int, is_nested: bool = False) -> tuple[list, int]:
            """Process a segment and return list of steps and next step_order."""
            steps = []
            seg_type = str(segment.get("type", "steady")).lower()
            
            if seg_type == "repeat":
                # Handle repeat/cycle group as RepeatGroupDTO (Garmin native structure)
                reps = int(segment.get("reps", 1))
                nested_segments = segment.get("segments", [])

                repeat_step_order = step_order
                step_order += 1

                child_step_id = 1
                nested_steps = []
                for nested_seg in nested_segments:
                    nested_step, step_order = _build_step(nested_seg, step_order, is_nested=True)
                    nested_step["childStepId"] = child_step_id
                    nested_steps.append(nested_step)

                repeat_step = {
                    "type": "RepeatGroupDTO",
                    "stepOrder": repeat_step_order,
                    "stepType": {
                        "stepTypeId": 6,
                        "stepTypeKey": "repeat",
                        "displayOrder": 6,
                    },
                    "childStepId": child_step_id,
                    "numberOfIterations": reps,
                    "workoutSteps": nested_steps,
                    "endConditionValue": int(reps),
                    "endCondition": {
                        "conditionTypeId": 7,
                        "conditionTypeKey": "iterations",
                        "displayOrder": 7,
                        "displayable": False,
                    },
                    "skipLastRestStep": False,
                    "smartRepeat": False,
                }
                steps.append(repeat_step)
            else:
                # Regular segment
                step_dict, step_order = _build_step(segment, step_order, is_nested)
                steps.append(step_dict)
            
            return steps, step_order

        # Process all segments
        for segment in workout.segments:
            segment_steps, step_order = _process_segment(segment, step_order)
            workout_steps.extend(segment_steps)

        typed_workout = workout_class(
            workoutName=workout.formatted_title,
            estimatedDurationInSecs=int(duration_seconds),
            workoutSegments=[
                WorkoutSegment(
                    segmentOrder=1,
                    sportType=sport_type,
                    workoutSteps=workout_steps,
                )
            ],
        )

        payload = typed_workout.model_dump(exclude_none=True)
        
        # Post-process to ensure required target fields are present (including nested repeat steps)
        def _normalize_step(step: dict[str, Any]) -> None:
            if "targetType" in step:
                if "targetValueOne" not in step:
                    step["targetValueOne"] = None
                if "targetValueTwo" not in step:
                    step["targetValueTwo"] = None
                if "targetValueUnit" not in step:
                    step["targetValueUnit"] = None
                if "zoneNumber" not in step:
                    step["zoneNumber"] = None

            for nested in step.get("workoutSteps", []):
                _normalize_step(nested)

        for segment in payload.get("workoutSegments", []):
            for step in segment.get("workoutSteps", []):
                _normalize_step(step)
        
        return payload

    def get_available_workouts(self) -> list[dict[str, Any]]:
        """Fetch list of available workouts from Garmin Connect."""
        if self._dry_run:
            LOGGER.info("[DRY-RUN] Would fetch available workouts from Garmin Connect.")
            return []

        if self._client is None:
            raise RuntimeError("Not authenticated. Call login() first.")

        LOGGER.info("Fetching workouts from Garmin Connect...")
        try:
            workouts = self._client.get_workouts()
            LOGGER.info("Successfully fetched %s workouts.", len(workouts))
            return workouts
        except Exception as exc:
            LOGGER.error("Failed to fetch workouts: %s", exc)
            raise

    def delete_workout(self, workout_id: int) -> bool:
        """Delete a single workout by ID.
        
        Returns True if successful, False otherwise.
        """
        if self._dry_run:
            LOGGER.info("[DRY-RUN] Would delete workout with ID: %s", workout_id)
            return True

        if self._client is None:
            raise RuntimeError("Not authenticated. Call login() first.")

        try:
            LOGGER.info("Deleting workout with ID: %s", workout_id)
            path = f"/workout-service/workout/{workout_id}"
            response = self._client.garth.request("DELETE", "connectapi", path)
            
            if response.status_code in (200, 204):
                LOGGER.info("Successfully deleted workout with ID: %s", workout_id)
                return True
            else:
                LOGGER.error("Failed to delete workout with ID %s: HTTP %s", workout_id, response.status_code)
                return False
        except Exception as exc:
            LOGGER.error("Failed to delete workout with ID %s: %s", workout_id, exc)
            return False
