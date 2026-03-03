from __future__ import annotations

import argparse
import logging
import sys

from garmin_batch_uploader.config import load_settings
from garmin_batch_uploader.garmin_client import GarminUploaderClient
from garmin_batch_uploader.parsers import load_workouts
from garmin_batch_uploader.planner import GarminBatchPlanner


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Bulk upload and schedule workouts to Garmin Connect."
    )
    parser.add_argument(
        "--file",
        required=True,
        help="Path to workouts input file (.csv or .json)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and simulate actions without logging into Garmin Connect.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable debug logging.",
    )
    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    try:
        workouts = load_workouts(args.file)
        if not workouts:
            logging.warning("No workouts found in input file.")
            return 0

        if args.dry_run:
            client = GarminUploaderClient(
                user="",
                password="",
                dry_run=True,
            )
        else:
            settings = load_settings()
            client = GarminUploaderClient(
                user=settings.garmin_user,
                password=settings.garmin_pass,
                tokenstore=settings.tokenstore,
                dry_run=False,
            )
        planner = GarminBatchPlanner(client)
        results = planner.run(workouts)

        logging.info("Finished processing %s workouts.", len(results))
        return 0
    except Exception as exc:
        logging.error("Execution failed: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
