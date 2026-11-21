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
import os, json, zipfile, tempfile, shutil
from datetime import datetime
from xml.etree import ElementTree as ET

TYPES = {
    "HKQuantityTypeIdentifierHeadphoneAudioExposure": "headphone",
    "HKCategoryTypeIdentifierAppleStandHour": "stand",
    "HKCategoryTypeIdentifierSleepAnalysis": "sleep",
    "HKQuantityTypeIdentifierHeartRate": "heart",
    "HKQuantityTypeIdentifierStepCount": "steps",
    "HKQuantityTypeIdentifierRestingHeartRate": "resting_hr",
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


def find_health_xml(root):
    """在解压目录里找健康数据 XML（文件名可能是 export.xml 或 导出.xml）"""
    for dirpath, _, files in os.walk(root):
        for f in files:
            if f.lower().endswith(".xml") and f.lower() not in ("export_cda.xml",):
                p = os.path.join(dirpath, f)
                if os.path.getsize(p) > 1024 * 1024:  # 至少 1MB
                    return p
    return None


def parse(zip_path, progress=None):
    """解析 zip，返回各类型记录"""
    tmp = tempfile.mkdtemp(prefix="healthviz_")
    try:
        # 手动解压：Windows 版健康 App 导出的 zip 里文件名是 GBK，直接 extractall 会乱码
        with zipfile.ZipFile(zip_path) as z:
            for info in z.infolist():
                name = info.filename
                if not info.flag_bits & 0x800:   # 没有 UTF-8 标记，按 GBK 还原
                    try:
                        name = name.encode("cp437").decode("gbk")
                    except (UnicodeEncodeError, UnicodeDecodeError):
                        pass
                target = os.path.join(tmp, name)
                target = os.path.abspath(target)
                if not target.startswith(os.path.abspath(tmp)):
                    continue   # 防目录穿越
                if info.is_dir():
                    os.makedirs(target, exist_ok=True)
                    continue
                os.makedirs(os.path.dirname(target), exist_ok=True)
                with z.open(info) as src, open(target, "wb") as dst:
                    shutil.copyfileobj(src, dst)
        xml = find_health_xml(tmp)
        if not xml:
            raise RuntimeError("zip 里找不到健康数据 XML")
        if progress:
            progress("找到健康数据（%.0f MB），开始解析…" % (os.path.getsize(xml) / 1048576))

        out = {k: [] for k in TYPES.values()}
        n = 0
        for _, el in ET.iterparse(xml, events=("end",)):
            if el.tag != "Record":
                el.clear()
                continue
            kind = TYPES.get(el.get("type", ""))
            if kind:
                s = _dt(el.get("startDate"))
                e = _dt(el.get("endDate"))
                if s and e:
                    v = el.get("value")
                    out[kind].append([s.isoformat(), e.isoformat(), v])
            el.clear()
            n += 1
            if progress and n % 500000 == 0:
                progress("已扫描 %d 条记录" % n)
        return out
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
