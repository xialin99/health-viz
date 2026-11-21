#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""统计：耳机聆听 + 手表佩戴"""
import collections
from datetime import datetime, timedelta


def _dt(s):
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None


def headphone_sessions(records, gap_seconds=120, min_minutes=1.0):
    """把连续的耳机暴露记录切成「聆听会话」"""
    recs = []
    for s, e, v in records:
        st, en = _dt(s), _dt(e)
        if st and en and en > st:
            try:
                db = float(v) if v else None
            except (TypeError, ValueError):
                db = None
            recs.append((st, en, db))
    recs.sort(key=lambda x: x[0])

    sessions, cur_s, cur_e, dbs = [], None, None, []
    intervals = []
    for st, en, db in recs:
        if cur_s is None:
            cur_s, cur_e, dbs = st, en, ([db] if db else [])
            intervals = [(st, en)]
        elif (st - cur_e).total_seconds() <= gap_seconds:
            cur_e = max(cur_e, en)
            if st <= intervals[-1][1]:
                intervals[-1] = (intervals[-1][0], cur_e)
            else:
                intervals.append((st, en))
            if db:
                dbs.append(db)
        else:
            m = sum((end - start).total_seconds() for start, end in intervals) / 60
            if m >= min_minutes:
                sessions.append({"start": cur_s.isoformat(), "minutes": m, "intervals": intervals,
                                 "avg_db": round(sum(dbs) / len(dbs), 1) if dbs else None})
            cur_s, cur_e, dbs = st, en, ([db] if db else [])
            intervals = [(st, en)]
    if cur_s:
        m = sum((end - start).total_seconds() for start, end in intervals) / 60
        if m >= min_minutes:
            sessions.append({"start": cur_s.isoformat(), "minutes": m, "intervals": intervals,
                             "avg_db": round(sum(dbs) / len(dbs), 1) if dbs else None})
    return sessions


def watch_wear(records):
    """手表佩戴：用 AppleStandHour 的整点记录反推

    每个整点一条记录（idle / stood），只有戴表才有。
    有记录的小时 = 戴表了。
    """
    by_day = collections.defaultdict(set)
    for s, e, v in records:
        st = _dt(s)
        if st:
            by_day[st.date().isoformat()].add(st.hour)
    return by_day


def summarize(sessions, wear_by_day):
    by_day = collections.defaultdict(float)
    by_hour = collections.defaultdict(float)
    by_weekday = collections.defaultdict(float)
    by_week_hour = collections.defaultdict(float)
    total = 0.0
    max_day = ("", 0)
    max_sess = 0
    high_db = 0

    for s in sessions:
        for start, end in s["intervals"]:
            while start < end:
                boundary = start.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
                stop = min(end, boundary)
                minutes = (stop - start).total_seconds() / 60
                day = start.date().isoformat()
                by_day[day] += minutes
                by_hour[start.hour] += minutes
                by_weekday[start.weekday()] += minutes
                by_week_hour[start.weekday(), start.hour] += minutes
                if by_day[day] > max_day[1]:
                    max_day = (day, by_day[day])
                start = stop
        total += s["minutes"]
        if s["minutes"] > max_sess:
            max_sess = s["minutes"]
        if s.get("avg_db") and s["avg_db"] > 80:
            high_db += 1

    days = sorted(by_day.keys())
    period = (datetime.fromisoformat(days[-1]) - datetime.fromisoformat(days[0])).days + 1 if days else 0

    # 手表佩戴
    wear_days = len(wear_by_day)
    wear_hours = sum(len(v) for v in wear_by_day.values())
    wear_by_day_list = [{"d": k, "h": len(v)} for k, v in sorted(wear_by_day.items())]

    return {
        "listen": {
            "totalSessions": len(sessions),
            "totalMinutes": round(total),
            "avgSession": round(total / len(sessions)) if sessions else 0,
            "maxSession": round(max_sess),
            "maxDay": {"date": max_day[0], "minutes": round(max_day[1])},
            "daysUsed": len(days),
            "avgPerUsedDay": round(total / len(days)) if days else 0,
            "highDbSessions": high_db,
            "periodStart": days[0] if days else "",
            "periodEnd": days[-1] if days else "",
            "periodDays": period,
            "byHour": [{"h": h, "min": round(by_hour.get(h, 0))} for h in range(24)],
            "byWeekHour": [[round(by_week_hour[d, h], 1) for h in range(24)] for d in range(7)],
            "byWeekday": [round(by_weekday.get(i, 0)) for i in range(7)],
            "byDay": [{"d": k, "min": round(v)} for k, v in sorted(by_day.items())],
        },
        "watch": {
            "daysWorn": wear_days,
            "totalHours": wear_hours,
            "avgHoursPerWornDay": round(wear_hours / wear_days, 1) if wear_days else 0,
            "byDay": wear_by_day_list,
            "periodStart": wear_by_day_list[0]["d"] if wear_by_day_list else "",
            "periodEnd": wear_by_day_list[-1]["d"] if wear_by_day_list else "",
        },
    }
