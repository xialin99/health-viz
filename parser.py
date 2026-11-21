#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Apple Health 导出解析器

从 iPhone 健康 App 导出的 zip 里提取：
- 耳机聆听（HeadphoneAudioExposure）
- 手表佩戴（AppleStandHour）
- 睡眠（SleepAnalysis）
- 心率（HeartRate）

只用标准库，零依赖。
"""
import zipfile
from datetime import datetime
from xml.etree import ElementTree as ET

TYPES = {
    "HKQuantityTypeIdentifierHeadphoneAudioExposure": "headphone",
    "HKCategoryTypeIdentifierAppleStandHour": "stand",
}


def _dt(s):
    if not s:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(s[:19], fmt)
        except ValueError:
            continue
    return None


def parse(zip_path, progress=None):
    """Stream the health XML without extracting files to disk."""
    out = {key: [] for key in TYPES.values()}
    with zipfile.ZipFile(zip_path) as archive:
        members = [
            item for item in archive.infolist()
            if not item.is_dir() and item.filename.lower().endswith(".xml")
        ]
        members.sort(key=lambda item: item.filename.rsplit("/", 1)[-1].lower() not in ("export.xml", "导出.xml"))
        selected = None
        for item in members:
            try:
                with archive.open(item) as candidate:
                    _, root = next(ET.iterparse(candidate, events=("start",)))
                    if root.tag == "HealthData":
                        selected = item
                        break
            except (ET.ParseError, StopIteration):
                continue
        if selected is None:
            raise ValueError("这个 ZIP 不包含 Apple 健康数据。请选择 iPhone 健康 App 导出的原始 ZIP。")

        with archive.open(selected) as source:
            events = ET.iterparse(source, events=("start", "end"))
            _, root = next(events)
            if root.tag != "HealthData":
                raise ValueError("文件不是 Apple 健康数据导出")
            depth = 1
            count = 0
            for event, element in events:
                if event == "start":
                    depth += 1
                    continue
                depth -= 1
                if depth != 1:
                    continue
                kind = TYPES.get(element.get("type")) if element.tag == "Record" else None
                if kind:
                    start, end = _dt(element.get("startDate")), _dt(element.get("endDate"))
                    if start and end:
                        out[kind].append([start.isoformat(), end.isoformat(), element.get("value")])
                root.remove(element)
                count += 1
                if progress and count % 500000 == 0:
                    progress("已扫描 {:,} 项".format(count))
    return out

