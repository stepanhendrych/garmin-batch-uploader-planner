from __future__ import annotations

import logging
from collections import defaultdict

from .garmin_client import GarminUploaderClient
from .models import Workout


LOGGER = logging.getLogger(__name__)


class GarminBatchPlanner:
    def __init__(self, client: GarminUploaderClient) -> None:
        self._client = client

    def run(self, workouts: list[Workout]) -> list[dict]:
        self._client.login()

        results: list[dict] = []
        for index, workout in enumerate(workouts, start=1):
            LOGGER.info("Processing workout %s/%s: %s", index, len(workouts), workout.title)
            result = self._client.upload_and_schedule(workout)
            results.append(result)

        return results

    def delete_workouts_by_sport_type(self) -> int:
        """Interactive mode to delete all workouts of a specific sport type."""
        self._client.login()

        # Fetch all workouts from Garmin
        LOGGER.info("Fetching all workouts from Garmin Connect...")
        try:
            workouts = self._client.get_available_workouts()
        except Exception as exc:
            LOGGER.error("Failed to fetch workouts: %s", exc)
            return 1

        if not workouts:
            LOGGER.info("No workouts found in Garmin Connect.")
            return 0

        # Group workouts by sport type
        workouts_by_sport: dict[str, list[dict]] = defaultdict(list)
        for workout in workouts:
            sport_data = workout.get("sportType", {})
            if isinstance(sport_data, dict):
                sport_type = sport_data.get("sportTypeKey", "unknown").lower()
            else:
                sport_type = "unknown"
            workouts_by_sport[sport_type].append(workout)

        # Display available sports and count
        print("\n" + "=" * 60)
        print("Available sport types:")
        print("=" * 60)
        sport_list = sorted(workouts_by_sport.keys())
        for idx, sport in enumerate(sport_list, 1):
            count = len(workouts_by_sport[sport])
            print(f"{idx}. {sport.capitalize()} ({count} workouts)")

        print("\nEnter the number of the sport type to delete (or 'q' to quit):")
        choice = input("> ").strip().lower()

        if choice == "q":
            LOGGER.info("Operation cancelled by user.")
            return 0

        try:
            sport_idx = int(choice) - 1
            if sport_idx < 0 or sport_idx >= len(sport_list):
                LOGGER.warning("Invalid selection.")
                return 1
        except ValueError:
            LOGGER.warning("Invalid input.")
            return 1

        selected_sport = sport_list[sport_idx]
        selected_workouts = workouts_by_sport[selected_sport]

        print("\n" + "=" * 60)
        print(f"Workouts of type '{selected_sport.upper()}' ({len(selected_workouts)} total):")
        print("=" * 60)
        for idx, workout in enumerate(selected_workouts, 1):
            title = workout.get("workoutName", "Unknown")
            print(f"{idx}. {title}")

        print("\nDelete options:")
        print("1. Delete ALL workouts of this type")
        print("2. Delete workouts one by one (interactive)")
        print("3. Cancel")
        print("\nEnter your choice (1-3):")
        mode_choice = input("> ").strip()

        if mode_choice == "3":
            LOGGER.info("Operation cancelled by user.")
            return 0
        elif mode_choice == "1":
            return self._delete_all_workouts(selected_workouts, selected_sport)
        elif mode_choice == "2":
            return self._delete_workouts_interactive(selected_workouts, selected_sport)
        else:
            LOGGER.warning("Invalid selection.")
            return 1

    def _delete_all_workouts(self, workouts: list[dict], sport_type: str) -> int:
        """Delete all workouts in the list."""
        count = len(workouts)
        print(f"\n⚠️  You are about to delete {count} {sport_type} workout(s)!")
        print("Type 'yes' to confirm, or anything else to cancel:")
        confirm = input("> ").strip().lower()

        if confirm != "yes":
            LOGGER.info("Operation cancelled by user.")
            return 0

        deleted_count = 0
        failed_count = 0

        for idx, workout in enumerate(workouts, 1):
            workout_id = workout.get("workoutId")
            title = workout.get("workoutName", "Unknown")
            
            print(f"\n[{idx}/{count}] Deleting '{title}'...", end=" ")
            if self._client.delete_workout(workout_id):
                print("✓")
                deleted_count += 1
            else:
                print("✗")
                failed_count += 1

        print("\n" + "=" * 60)
        print(f"Deletion complete!")
        print(f"  ✓ Deleted: {deleted_count}")
        print(f"  ✗ Failed: {failed_count}")
        print("=" * 60)

        return 0 if failed_count == 0 else 1

    def _delete_workouts_interactive(self, workouts: list[dict], sport_type: str) -> int:
        """Delete workouts one by one with user confirmation."""
        deleted_count = 0
        skipped_count = 0
        count = len(workouts)

        for idx, workout in enumerate(workouts, 1):
            workout_id = workout.get("workoutId")
            title = workout.get("workoutName", "Unknown")

            print(f"\n[{idx}/{count}] {title}")
            print("Delete this workout? (yes/no/cancel):")
            choice = input("> ").strip().lower()

            if choice == "cancel":
                LOGGER.info("Operation cancelled by user at workout %d/%d.", idx, count)
                break
            elif choice == "yes":
                if self._client.delete_workout(workout_id):
                    print("✓ Deleted")
                    deleted_count += 1
                else:
                    print("✗ Failed to delete")
            else:
                print("⊘ Skipped")
                skipped_count += 1

        print("\n" + "=" * 60)
        print(f"Deletion complete!")
        print(f"  ✓ Deleted: {deleted_count}")
        print(f"  ⊘ Skipped: {skipped_count}")
        print("=" * 60)

        return 0
