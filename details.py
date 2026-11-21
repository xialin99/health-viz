"""Daily drill-down data, kept separate from the existing summary."""
from collections import defaultdict
from datetime import datetime, timedelta
from math import isfinite


METRICS = {
    "HeartRate": ("心率", False),
    "RestingHeartRate": ("静息心率", False),
    "StepCount": ("步数", True),
    "DistanceWalkingRunning": ("步行与跑步距离", True),
    "ActiveEnergyBurned": ("活动能量", True),
    "AppleExerciseTime": ("锻炼时间", True),
    "BodyMass": ("体重", False),
    "RespiratoryRate": ("呼吸频率", False),
    "OxygenSaturation": ("血氧饱和度", False),
    "HeartRateVariabilitySDNN": ("心率变异性（SDNN）", False),
}


def day_segments(start, end):
    while start < end:
        midnight = start.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        stop = min(midnight, end)
        yield start.date().isoformat(), start.strftime("%H:%M:%S"), (
            "24:00:00" if stop == midnight else stop.strftime("%H:%M:%S")
        ), (stop - start).total_seconds()
        start = stop


def daily_details(data, sessions, wear):
    days = defaultdict(lambda: {"audio": [], "watch": [], "body": {}, "workouts": []})
    for session in sessions:
        first, last = session["intervals"][0][0], session["intervals"][-1][1]
        recorded = defaultdict(float)
        for start, end in session["intervals"]:
            for day, _, _, seconds in day_segments(start, end):
                recorded[day] += seconds
        for day, start, end, _ in day_segments(first, last):
            if recorded[day]:
                days[day]["audio"].append([start, end, round(recorded[day] / 60, 1)])

    for day, hours in wear.items():
        ranges = days[day]["watch"]
        for hour in sorted(hours):
            if ranges and ranges[-1][1] == hour:
                ranges[-1][1] += 1
            else:
                ranges.append([hour, hour + 1])

    readings = defaultdict(list)
    for key in METRICS:
        for start, _, value, unit, source in data.get(key, []):
            try:
                value = float(value)
            except (ValueError, TypeError):
                continue
            if isfinite(value):
                readings[start[:10], key, unit or "", source or "未知来源"].append(value)
    for (day, key, unit, source), values in readings.items():
        label, cumulative = METRICS[key]
        number = sum(values) if cumulative else sum(values) / len(values)
        if isfinite(number):
            days[day]["body"].setdefault(label, []).append([
                "合计" if cumulative else "平均", round(number, 2), unit, source, len(values)
            ])

    sleep = defaultdict(list)
    for start, end, value, _, _ in data.get("sleep", []):
        if value and value.startswith("HKCategoryValueSleepAnalysisAsleep"):
            sleep[end[:10]].append((datetime.fromisoformat(start), datetime.fromisoformat(end)))
    for day, intervals in sleep.items():
        merged = []
        for start, end in sorted(intervals):
            if start >= end:
                continue
            if merged and start <= merged[-1][1]:
                merged[-1][1] = max(end, merged[-1][1])
            else:
                merged.append([start, end])
        minutes = sum((end - start).total_seconds() / 60 for start, end in merged)
        if merged:
            days[day]["body"]["睡眠"] = [["按记录结束日汇总", round(minutes, 1), "分钟", "", len(merged)]]

    for start, end, kind, _, source in sorted(data.get("workout", []), key=lambda row: row[:2]):
        days[start[:10]]["workouts"].append([
            start[11:19], end[11:19], kind or "", source or ""
        ])
    return dict(days)
