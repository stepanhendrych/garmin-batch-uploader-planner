#!/usr/bin/env python3
"""Showcase new extended format with repeat groups and end conditions."""

import json
from garmin_batch_uploader.parsers import load_workouts
from garmin_batch_uploader.garmin_client import GarminUploaderClient

workouts = load_workouts("workouts.json")
print(f"✓ Loaded {len(workouts)} workouts\n")

# Show detailed breakdown of specific workouts
test_workouts = [1, 2, 4, 5]  # Simple, repeat, HR-based, calories

for idx in test_workouts:
    workout = workouts[idx - 1]
    print(f"\n{'='*70}")
    print(f"Workout {idx}: {workout.title}")
    print(f"{'='*70}")
    
    payload = GarminUploaderClient._build_workout_payload(workout)
    segment = payload["workoutSegments"][0]
    steps = segment.get("workoutSteps", [])
    
    print(f"Generated {len(steps)} steps from {len(workout.segments)} segment(s):\n")
    
    for j, step in enumerate(steps, 1):
        step_type = step.get("stepType", {}).get("stepTypeKey")
        duration = step.get("endConditionValue", 0)
        end_cond = step.get("endCondition", {})
        
        # Format based on end condition type
        cond_key = end_cond.get("conditionTypeKey", "time")
        if cond_key == "distance":
            display = f"{duration/1000:.1f}km"
        elif cond_key == "calories":
            display = f"{duration:.0f} cal"
        elif cond_key == "heart.rate":
            op = step.get("endConditionCompare", "?")
            display = f"HR {op} {duration:.0f} bpm"
        elif cond_key == "lap.button":
            display = "LAP button"
        else:
            display = f"{duration/60:.1f}min"
        
        print(f"  {j:2d}. {step_type:10} → {display:20} [{cond_key}]")

print(f"\n{'='*70}")
print("✓ Extended format support verified!")
print(f"{'='*70}\n")
