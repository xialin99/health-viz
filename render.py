"""Local HTML views for HealthViz."""
from html import escape
from calendar import Calendar
from datetime import date

STYLE = """
.days a.cell{display:grid;place-items:center;text-decoration:none}.day-back{display:inline-block;margin-bottom:16px;color:var(--green);font-weight:700}.day-detail{margin-top:18px}.day-detail .panel h2{margin-bottom:6px}
.detail-nav{display:flex;gap:12px;flex-wrap:wrap;margin:20px 0}.detail-nav a{color:var(--green)}.daily-select{margin:0 0 20px}.daily-select input{font:inherit;margin-left:8px}.daily-detail{border-top:1px solid var(--line);padding:12px 0}.daily-detail summary,.metric-detail summary{cursor:pointer;color:var(--green);font-weight:700}.detail-group{display:grid;gap:8px}.metric-detail{padding:8px 0;border-bottom:1px solid var(--line)}.day-track{height:12px;position:relative;background:#e7ede8;border-radius:6px;margin-top:12px}.day-track i{position:absolute;height:100%;background:var(--green);border-radius:6px}.day-axis{display:flex;justify-content:space-between;color:var(--muted);font-size:.78rem}
.dashboard{display:grid;gap:18px}.dash-head{display:flex;justify-content:space-between;gap:12px;align-items:center;flex-wrap:wrap}.dash-head h2{margin:0}.months{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}.month{padding:12px;background:#f7faf7;border:1px solid var(--line);border-radius:12px}.month h4{margin:0 0 8px}.days{display:grid;grid-template-columns:repeat(7,minmax(0,1fr));gap:3px;text-align:center}.days span{font-size:.68rem;color:var(--muted)}.cell{aspect-ratio:1;border:0;border-radius:4px;padding:0;background:var(--tone,#e7ede8);color:#203e34;font:inherit;font-size:.68rem;cursor:pointer}.cell[data-level="4"],.cell[data-level="5"]{color:white}.cell:hover{outline:2px solid #182c26}.year{margin:12px 0}.year summary{cursor:pointer;font-weight:800;padding:8px 0}.legend{display:flex;gap:6px;align-items:center;flex-wrap:wrap;margin:10px 0;font-size:.82rem;color:var(--muted)}.swatch{width:13px;height:13px;border-radius:3px;background:var(--tone)}.readout{display:block;min-height:1.8em;color:var(--green);font-weight:700;margin:8px 0}.matrix-wrap{overflow:auto}.matrix{min-width:660px;display:grid;grid-template-columns:2.6rem repeat(24,minmax(0,1fr));gap:3px;align-items:center;text-align:center;font-size:.68rem}.matrix .cell{width:100%}.stat strong{overflow-wrap:anywhere}@media(max-width:950px){.months{grid-template-columns:repeat(3,minmax(0,1fr))}}@media(max-width:680px){.months{grid-template-columns:repeat(2,minmax(0,1fr))}.month{padding:8px}.days{gap:2px}}@media(max-width:350px){.months{grid-template-columns:1fr}}

:root{color-scheme:light;--ink:#182c26;--muted:#51635c;--paper:#f3f5ef;--green:#145745;--line:#d9e3d9}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 "Microsoft YaHei",system-ui,sans-serif}
header,main,footer{width:min(1120px,calc(100% - 40px));margin:auto}
header{padding:24px 0;border-bottom:1px solid var(--line);display:flex;align-items:center;justify-content:space-between;gap:12px}
.brand{font-weight:800;letter-spacing:-.03em;color:var(--ink);text-decoration:none}.brand b{color:var(--green)}
header span,footer,.muted{color:var(--muted);font-size:.9rem}
main{padding:36px 0}.hero{padding:clamp(24px,5vw,62px);border-radius:26px;background:#123b30;color:#fff}
.hero p{color:#d0e5d9;margin-bottom:0}.hero small{color:#abe0c2}
h1{font-size:clamp(2rem,5vw,3.9rem);line-height:1.2;letter-spacing:-.04em;margin:.28em 0}
h2{margin:0 0 12px;font-size:1.35rem}h3{margin:0 0 10px;font-size:1rem}
.cols,.stats{display:grid;gap:16px;margin:20px 0}.cols{grid-template-columns:1.45fr 1fr}.stats{grid-template-columns:repeat(3,minmax(0,1fr))}
.panel,.stat{background:#fff;border:1px solid var(--line);border-radius:18px;padding:22px;min-width:0}
.stat strong{display:block;font-size:clamp(1.3rem,3vw,2rem);margin-top:6px;font-variant-numeric:tabular-nums}
.drop{display:grid;place-content:center;width:100%;min-height:150px;border:1px dashed #75a58d;border-radius:14px;background:#e7f2ea;color:var(--green);cursor:pointer;font:inherit;font-weight:700}
.drop:hover,.drop.drag{background:#d4ebdc}.drop small{display:block;font-weight:400}.drop:disabled{cursor:wait}
progress{width:100%;accent-color:var(--green)}#msg{overflow-wrap:anywhere}ol{padding-left:1.4em;color:var(--muted)}li{margin:.65em 0}
section{margin:32px 0}.bars{display:grid;gap:7px;max-height:340px;overflow:auto;padding-right:6px}
.row{display:grid;grid-template-columns:6.6rem minmax(0,1fr) 5rem;align-items:center;gap:8px;font-size:.82rem}
.row meter{width:100%;height:14px;accent-color:var(--green)}.row output{text-align:right;font-variant-numeric:tabular-nums}
footer{border-top:1px solid var(--line);padding:16px 0 30px}a{color:var(--green)}:focus-visible{outline:3px solid #268260;outline-offset:4px}
@media(max-width:680px){.cols{grid-template-columns:minmax(0,1fr)}.stats{gap:8px}.stat{padding:12px}.stat .muted{font-size:.77rem}.row{grid-template-columns:5.7rem minmax(0,1fr) 4.5rem}}
"""


def page(title, content):
    return f"""<!doctype html><html lang="zh-CN"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)} · HealthViz</title><style>{STYLE}</style>
<header><a class="brand" href="/">Health<b>Viz</b></a><span>Apple 健康数据看板</span></header>
<main>{content}</main><footer>在本机解析与绘制 · <a href="/">导入另一份文件</a></footer></html>"""


def upload_page():
    return page("导入健康数据", """
<div class="hero"><small>耳机聆听与 Apple Watch</small><h1>看懂你的健康记录</h1>
<p>导入 Apple 健康 ZIP，查看每天的聆听时长与估算佩戴小时。</p></div>
<div class="cols"><div class="panel"><h2>导入导出文件</h2>
<button id="drop" class="drop" type="button">选择 ZIP 文件<small>也可拖放到这里 · 最大 2 GiB</small></button>
<input id="file" type="file" accept=".zip" hidden>
<progress id="progress" max="100" hidden></progress><p id="msg" role="status" class="muted"></p></div>
<aside class="panel"><h2>怎么导出</h2><ol><li>在 iPhone 打开「健康」并点头像。</li>
<li>选择「导出所有健康数据」。</li><li>把保存好的 ZIP 文件放到左侧。</li></ol></aside></div>
<script>
const drop = document.querySelector('#drop'), file = document.querySelector('#file');
const progress = document.querySelector('#progress'), msg = document.querySelector('#msg');
const fail = text => { msg.textContent = text; drop.disabled = false; progress.hidden = true; };
drop.onclick = () => file.click();
file.onchange = () => { const selected = file.files[0]; file.value = ''; upload(selected); };
drop.ondragover = event => { event.preventDefault(); drop.classList.add('drag'); };
drop.ondragleave = () => drop.classList.remove('drag');
drop.ondrop = event => { event.preventDefault(); drop.classList.remove('drag'); upload(event.dataTransfer.files[0]); };
async function poll() {
    try {
        const response = await fetch('/status');
        if (!response.ok) throw new Error();
        const status = await response.json();
        msg.textContent = status.progress;
        if (status.status === 'done') location.href = '/result';
        else if (status.status === 'error') fail(status.error);
        else setTimeout(poll, 800);
    } catch { fail('无法读取进度，请确认本地服务仍在运行。'); }
}
function upload(selected) {
    if (drop.disabled || !selected) return;
    if (!selected.name.toLowerCase().endsWith('.zip')) return fail('请选择 ZIP 文件。');
    drop.disabled = true;
    progress.hidden = false;
    progress.value = 0;
    msg.textContent = '正在传给本地解析服务…';
    const request = new XMLHttpRequest();
    request.open('POST', '/upload');
    request.setRequestHeader('Content-Type', 'application/zip');
    request.upload.onprogress = event => {
        if (event.lengthComputable) progress.value = 100 * event.loaded / event.total;
    };
    request.onload = () => {
        if (request.status === 200) { progress.removeAttribute('value'); poll(); }
        else fail(request.responseText || '导入失败，请重试。');
    };
    request.onerror = () => fail('无法连接本地服务，请重试。');
    request.send(selected);
}
</script>""")


def stats(entries):
    return '<div class="stats">' + ''.join(
        f'<div class="stat"><span class="muted">{label}</span><strong>{value}</strong></div>'
        for label, value in entries
    ) + '</div>'



COLORS = ("#e7ede8", "#cbe6d5", "#9bd0b3", "#68b694", "#28775c", "#154b3b")
WEEK = "一二三四五六日"


def cell(label, value, limits, unit, face="", day=""):
    level = 0 if value is None else 1 + sum(value >= limit for limit in limits)
    detail = f"{label} · {value:g} {unit}" if value is not None else f"{label} · 无记录"
    safe = escape(detail, quote=True)
    attrs = f'class="cell" data-level="{level}" style="--tone:{COLORS[level]}" title="{safe}" aria-label="{safe}"'
    if day:
        return f'<a {attrs} href="/day/{day}">{face}</a>'
    return f'<button {attrs} type="button">{face}</button>'


def legend(limits, unit):
    labels = ["无记录"] + [
        f"{a}–<{b} {unit}" for a, b in zip((0, *limits), limits)
    ] + [f"≥{limits[-1]} {unit}"]
    return '<div class="legend">' + ''.join(
        f'<span class="swatch" style="--tone:{color}"></span><span>{label}</span>'
        for color, label in zip(COLORS, labels)
    ) + '</div>'


def calendar_map(rows, key, unit, limits):
    values = {date.fromisoformat(row["d"]): row[key] for row in rows}
    first, last = min(values), max(values)
    content = ['<div class="panel heat"><div class="dash-head"><h3>每日热力图</h3>'
               f'<span class="muted">{first} 至 {last}</span></div>',
               legend(limits, unit), '<output class="readout">点选一天查看当天详情</output>']
    for year in range(last.year, first.year - 1, -1):
        start = first.month if year == first.year else 1
        end = last.month if year == last.year else 12
        expanded = ' open' if year == last.year else ''
        content.append(f'<details class="year"{expanded}><summary>{year} 年</summary><div class="months">')
        for month in range(start, end + 1):
            content.append(f'<div class="month"><h4>{month} 月</h4><div class="days">')
            content.extend(f'<span>{weekday}</span>' for weekday in WEEK)
            for day in Calendar().itermonthdates(year, month):
                if day.month != month or not first <= day <= last:
                    content.append('<span></span>')
                else:
                    content.append(cell(str(day), values.get(day), limits, unit, day.day, day.isoformat()))
            content.append('</div></div>')
        content.append('</div></details>')
    return ''.join(content) + '</div>'


def rhythm(matrix):
    limits = (60, 300, 900, 1800)
    labels = ''.join(f'<span>{hour:02d}</span>' for hour in range(24))
    rows = []
    for day, hours in zip(WEEK, matrix):
        rows.append(f'<strong>周{day}</strong>')
        rows.extend(cell(f"周{day} {hour:02d}:00", value or None, limits, "分钟")
                    for hour, value in enumerate(hours))
    return ('<div class="panel heat"><h3>每周聆听节奏</h3><p class="muted">按星期与小时汇总。颜色越深，累计聆听时间越长。</p>'
            + legend(limits, "分钟") + '<output class="readout" aria-live="polite">点选格子查看数值</output>'
            + '<div class="matrix-wrap"><div class="matrix"><span></span>' + labels + ''.join(rows) + '</div></div></div>')


def result_page(report):
    listening, watch = report["listen"], report["watch"]
    parts = ['<div class="hero"><small>Apple 健康导入结果</small><h1>健康数据概览</h1>'
             '<p>用颜色找到活跃的日子，再点开查看具体时长。</p></div>'
             '<nav class="detail-nav" aria-label="健康数据模块"><a href="#audio">耳机</a>'
             '<a href="#watch">手表</a><a href="#body">身体状态</a></nav>'
             '<section class="dashboard" id="audio"><h2>耳机聆听</h2>']
    if listening["byDay"]:
        peak = listening["maxDay"]
        hour = max(listening["byHour"], key=lambda row: row["min"])
        weekday = max(range(7), key=lambda day: listening["byWeekday"][day])
        parts.append(stats([
            ("累计聆听", f'{listening["totalMinutes"]:,} 分钟'),
            ("聆听天数 / 记录跨度", f'{listening["daysUsed"]} / {listening["periodDays"]} 天'),
            ("聆听有记录日均", f'{listening["avgPerUsedDay"]} 分钟'),
            ("聆听会话", f'{listening["totalSessions"]:,} 次'),
            ("平均单次会话", f'{listening["avgSession"]} 分钟'),
            ("最长单次会话", f'{listening["maxSession"]} 分钟'),
            ("聆听最多的一天", f'{peak["minutes"]} 分钟 · {peak["date"]}'),
            ("累计最多时段", f'周{WEEK[weekday]} / {hour["h"]:02d}:00（分别统计）'),
            ("会话记录平均值超过 80 dB", f'{listening["highDbSessions"]:,} 次'),
        ]))
        parts.append(calendar_map(listening["byDay"], "min", "分钟", (15, 30, 60, 120)))
        parts.append(rhythm(listening["byWeekHour"]))
    else:
        parts.append('<p class="panel muted">这份导出没有可统计的耳机聆听记录。</p>')
    parts.append('</section><section class="dashboard" id="watch"><h2>Apple Watch 佩戴估算</h2>')
    if watch["byDay"]:
        parts.append(stats([
            ("累计估算", f'{watch["totalHours"]:,} 小时'),
            ("有记录的天数", f'{watch["daysWorn"]} 天'),
            ("有记录日均", f'{watch["avgHoursPerWornDay"]:g} 小时'),
        ]))
        parts.append(calendar_map(watch["byDay"], "h", "小时", (4, 8, 12, 16)))
        parts.append('<p class="muted">每个有站立记录的小时算作 1 小时。灰色表示缺少记录，无法判断当时是否佩戴。</p>')
    else:
        parts.append('<p class="panel muted">这份导出没有可用于估算佩戴的站立记录。</p>')
    dates = sorted(report.get("details", {}))
    parts.append('</section><section class="dashboard" id="body"><h2>身体状态</h2>')
    if dates:
        options = ''.join(f'<option>{day}</option>' for day in reversed(dates))
        parts.append('<div class="panel"><form action="/day" method="get">'
                     f'<label>日期 <select name="date">{options}</select></label> '
                     '<button type="submit">查看当天详情</button></form></div>')
    else:
        parts.append('<p class="panel muted">这份导出没有可查看的日期。</p>')
    parts.append("""</section><script>
const saved = history.state && history.state.overview;
const years = [...document.querySelectorAll('details.year')];
if (saved) {
    years.forEach((year, index) => { year.open = saved.openYears.includes(index); });
    requestAnimationFrame(() => window.scrollTo(0, saved.scroll));
}
function rememberOverview() {
    history.replaceState({overview: {
        openYears: years.flatMap((year, index) => year.open ? [index] : []),
        scroll: window.scrollY
    }}, '');
}
document.addEventListener('click', event => {
    const cell = event.target.closest('.cell');
    if (cell?.matches('a')) rememberOverview();
    else if (cell) cell.closest('.heat').querySelector('.readout').textContent = cell.getAttribute('aria-label');
});
document.querySelector('#body form')?.addEventListener('submit', rememberOverview);
</script>""")
    return page("健康数据概览", ''.join(parts))


def _hour(time):
    hours, minutes, seconds = map(int, time.split(":"))
    return hours + minutes / 60 + seconds / 3600


def _timeline(ranges):
    bars = ''.join(f'<i style="left:{start / 24:.4%};width:{(end - start) / 24:.4%}"></i>'
                   for start, end in ranges)
    return ('<div aria-hidden="true"><div class="day-track">' + bars +
            '</div><div class="day-axis"><span>00:00</span><span>06:00</span>'
            '<span>12:00</span><span>18:00</span><span>24:00</span></div></div>')


def day_page(report, day):
    data = report.get("details", {}).get(day, {})
    audio, watch = data.get("audio", []), data.get("watch", [])
    workouts, body = data.get("workouts", []), data.get("body", {})
    parts = [
        '<a class="day-back" id="day-back" href="/result">← 返回健康数据概览</a>',
        f'<div class="hero"><small>当天详情</small><h1>{escape(day)}</h1></div>',
        '<div class="dashboard day-detail">',
        '<section class="panel detail-group"><h2>耳机聆听</h2>',
    ]
    if audio:
        parts.append('<p class="muted">按聆听记录推算起止。短间隔可能并入同一会话。</p>')
        parts.append(_timeline((_hour(start), _hour(end)) for start, end, _ in audio))
        parts.extend(f'<div>{start} 至 {end} · 记录 {minutes:g} 分钟</div>' for start, end, minutes in audio)
    else:
        parts.append('<p class="muted">当天没有聆听记录。</p>')
    parts.append('</section><section class="panel detail-group"><h2>Apple Watch</h2>')
    if watch:
        parts.append('<p class="muted">整点范围表示有站立记录。空白时段的佩戴状态未知。</p>')
        parts.append(_timeline(watch))
        parts.extend(f'<div>{start:02d}:00 至 {end:02d}:00 · 有记录</div>' for start, end in watch)
    else:
        parts.append('<p class="muted">当天没有站立记录。</p>')
    parts.append(f'<details class="metric-detail"><summary>锻炼记录 · {len(workouts)} 次</summary>')
    for start, end, kind, source in workouts:
        label = kind[len("HKWorkoutActivityType"):] if kind.startswith("HKWorkoutActivityType") else kind
        row = " · ".join(piece for piece in (f"{start} 至 {end}", label, source) if piece)
        parts.append(f'<div>{escape(row)}</div>')
    if not workouts:
        parts.append('<div>当天没有独立的锻炼记录。</div>')
    parts.append('</details></section><section class="panel detail-group"><h2>身体状态</h2>')
    for name, readings in body.items():
        preview = f'{readings[0][1]:g} {readings[0][2]}' if len(readings) == 1 else "按来源查看"
        parts.append(f'<details class="metric-detail"><summary>{escape(name)} · {escape(preview)}</summary>')
        for method, number, unit, source, count in readings:
            row = f"{method} · {number:g} {unit}".rstrip()
            if source:
                row += f" · {source}（{count} 条记录）"
            parts.append(f'<div>{escape(row)}</div>')
        parts.append('</details>')
    if not body:
        parts.append('<p class="muted">当天没有可展示的身体状态记录。</p>')
    parts.append("""</section></div><script>
document.getElementById('day-back').addEventListener('click', event => {
    if (event.button === 0 && !event.ctrlKey && !event.metaKey && !event.shiftKey && !event.altKey &&
        document.referrer === location.origin + '/result' && history.length > 1) {
        event.preventDefault();
        history.back();
    }
});
</script>""")
    return page(f"{day} · 当天详情", ''.join(parts))
