import json
import traceback
import sys
from pathlib import Path

# Ensure project root is on sys.path when running the script directly
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from garmin_batch_uploader.parsers import load_workouts
from garmin_batch_uploader.garmin_client import GarminUploaderClient

try:
    workouts = load_workouts('workouts.json')
except Exception as exc:
    print('Failed to load workouts.json:', exc)
    sys.exit(1)

for idx, w in enumerate(workouts, start=1):
    print(f"--- Workout {idx}: {w.title} ({w.date}) ---")
    try:
        payload = GarminUploaderClient._build_workout_payload(w)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    except Exception as exc:
        print('Error building payload:', exc)
        traceback.print_exc()
    print()
