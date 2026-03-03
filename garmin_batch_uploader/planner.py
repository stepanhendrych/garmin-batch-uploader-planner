from __future__ import annotations

import logging

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
