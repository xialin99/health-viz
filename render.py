#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""HTML 渲染"""
import json

HEAD = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title>
<script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>
<style>
:root{--bg:#050708;--card:rgba(255,255,255,.035);--line:rgba(255,255,255,.075);--fg:#e8f3ef;--dim:#7d9a90;--acc:#38e0b0;--acc2:#4ab8d8}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--fg);font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;padding:28px 24px 60px;max-width:1120px;margin:0 auto;min-height:100vh;position:relative;overflow-x:hidden}
body::before{content:"";position:fixed;inset:0;pointer-events:none;background:radial-gradient(900px 500px at 15% -5%,rgba(56,224,176,.10),transparent 60%),radial-gradient(700px 420px at 88% 8%,rgba(74,184,216,.075),transparent 60%),radial-gradient(600px 500px at 50% 110%,rgba(56,224,176,.04),transparent 60%)}
h1{font-size:52px;font-weight:700;letter-spacing:-1px;background:linear-gradient(120deg,#fff 20%,#9fe8d0 60%,#38e0b0);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:10px}
.sub{color:var(--dim);font-size:13.5px;line-height:1.7}
.tag{display:inline-block;font-size:11px;color:var(--acc);border:1px solid rgba(56,224,176,.3);border-radius:99px;padding:3px 10px;margin-bottom:16px;background:rgba(56,224,176,.06)}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(158px,1fr));gap:12px;margin:22px 0}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:16px 16px 14px;backdrop-filter:blur(20px);position:relative;overflow:hidden}
.card::before{content:"";position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,rgba(255,255,255,.18),transparent)}
.card .idx{position:absolute;top:12px;right:14px;font-size:10px;color:rgba(255,255,255,.18);font-variant-numeric:tabular-nums}
.card .k{color:var(--dim);font-size:11px;margin-bottom:10px;letter-spacing:.3px}
.card .v{font-size:32px;font-weight:700;color:var(--fg);font-variant-numeric:tabular-nums;line-height:1}
.card .v small{font-size:13px;font-weight:500;color:var(--dim);margin-left:3px}
.card .n{color:var(--dim);font-size:10.5px;margin-top:8px}
.panel{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:18px;margin-bottom:14px;backdrop-filter:blur(20px);position:relative}
.panel::before{content:"";position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,rgba(255,255,255,.15),transparent)}
.ph{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:14px;flex-wrap:wrap;gap:6px}
.ph h2{font-size:13px;color:var(--dim);font-weight:500;letter-spacing:.4px}
.ph .meta{font-size:11px;color:var(--dim)}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.chart{width:100%;height:240px}
.note{color:var(--dim);font-size:11px;text-align:center;margin-top:22px}
a{color:var(--acc);text-decoration:none}
@media(max-width:760px){h1{font-size:38px}.grid2{grid-template-columns:1fr}body{padding:20px 16px 50px}}
</style>
</head><body>"""

UPLOAD = """
<div class="tag">本地运行 · 数据不出机器</div>
<h1>HealthViz</h1>
<div class="sub">把你的 Apple Health 数据变成一眼能看懂的可视化。<br>上传 iPhone 导出的 zip，解析在本机完成，不发送到任何服务器。</div>

<div class="panel" style="margin-top:26px">
  <div class="ph"><h2>上传健康数据</h2><div class="meta">.zip · 从健康 App 导出</div></div>
  <div id="drop" style="border:1.5px dashed rgba(56,224,176,.35);border-radius:14px;padding:48px 20px;text-align:center;cursor:pointer;transition:.2s">
    <div style="color:var(--acc);font-size:14px;margin-bottom:6px">点击选择文件</div>
    <div style="color:var(--dim);font-size:12px">或拖拽到此处</div>
  </div>
  <input type="file" id="file" accept=".zip" style="display:none">
  <div id="prog" style="display:none;margin-top:16px">
    <div style="height:3px;background:rgba(255,255,255,.08);border-radius:2px;overflow:hidden"><i id="bar" style="display:block;height:100%;width:0;background:var(--acc);transition:width .25s"></i></div>
    <div id="msg" style="color:var(--dim);font-size:12px;margin-top:10px">准备中…</div>
  </div>
</div>

<div class="panel">
  <div class="ph"><h2>怎么导出</h2></div>
  <div class="sub" style="font-size:12.5px;line-height:2">
    1. iPhone 打开「健康」App<br>
    2. 点右上角头像<br>
    3. 拉到最下面，点「导出所有健康数据」<br>
    4. 等几分钟，得到 export.zip<br>
    5. 把它拖到上面
  </div>
</div>

<div class="note">HealthViz · 开源 · 所有解析在本机完成</div>
<script>
const drop=document.getElementById('drop'),file=document.getElementById('file'),
prog=document.getElementById('prog'),bar=document.getElementById('bar'),msg=document.getElementById('msg');
drop.onmouseenter=()=>drop.style.borderColor='rgba(56,224,176,.7)';
drop.onmouseleave=()=>drop.style.borderColor='rgba(56,224,176,.35)';
drop.onclick=()=>file.click();
drop.ondragover=e=>e.preventDefault();
drop.ondrop=e=>{e.preventDefault();if(e.dataTransfer.files[0])up(e.dataTransfer.files[0])};
file.onchange=()=>{if(file.files[0])up(file.files[0])};
function up(f){
  if(!f.name.toLowerCase().endsWith('.zip')){alert('只接受 .zip');return}
  const fd=new FormData();fd.append('file',f);
  const xhr=new XMLHttpRequest();
  prog.style.display='block';
  xhr.upload.onprogress=e=>{if(e.lengthComputable){bar.style.width=(e.loaded/e.total*100)+'%';msg.textContent='上传中 '+(e.loaded/1048576).toFixed(0)+' / '+(e.total/1048576).toFixed(0)+' MB'}};
  xhr.onload=()=>{
    if(xhr.status!==200){msg.textContent='上传失败';return}
    msg.textContent='上传完成，正在解析…';
    const t=setInterval(()=>{
      fetch('/status').then(r=>r.json()).then(s=>{
        msg.textContent=s.progress||'处理中…';
        if(s.status==='done'){clearInterval(t);location.href='/result'}
        else if(s.status==='error'){clearInterval(t);msg.innerHTML='<span style="color:#ff6b6b">失败：'+s.error+'</span>'}
      });
    },800);
  };
  xhr.onerror=()=>{msg.textContent='网络错误'};
  xhr.open('POST','/upload');xhr.send(fd);
}
</script></body></html>"""

def upload_page():
    return HEAD.replace("__TITLE__", "HealthViz") + UPLOAD

def result_page(S):
    return HEAD.replace("__TITLE__", "HealthViz · 分析结果") + '<script>window.__DATA__ = ' + json.dumps(S, ensure_ascii=False) + ';</script>' + RESULT

RESULT = """
<div class="tag">分析完成</div>
<h1>HealthViz</h1>
<div class="sub" id="lead"></div>

<div style="margin-top:22px;margin-bottom:8px;color:var(--dim);font-size:12px;letter-spacing:1px">耳机聆听</div>
<div class="cards" id="lc"></div>
<div class="panel"><div class="ph"><h2>每天听了多久</h2><div class="meta" id="heatMeta"></div></div><div id="heat" style="padding:4px 0"></div></div>
<div class="grid2">
  <div class="panel"><div class="ph"><h2>时段分布</h2><div class="meta" id="hourMeta"></div></div><div class="chart" id="hourChart"></div></div>
  <div class="panel"><div class="ph"><h2>一周分布</h2><div class="meta" id="weekMeta"></div></div><div class="chart" id="weekChart"></div></div>
</div>

<div style="margin-top:26px;margin-bottom:8px;color:var(--dim);font-size:12px;letter-spacing:1px">手表佩戴</div>
<div class="cards" id="wc"></div>
<div class="panel"><div class="ph"><h2>每天戴了几小时</h2><div class="meta" id="wearMeta"></div></div><div id="wear" style="padding:4px 0"></div></div>

<div class="note">数据只保存在本机 · <a href="/reset">重新上传</a></div>

<script>
const S = window.__DATA__;
const L = S.listen, W = S.watch;
const fmt = m => m>=60 ? Math.floor(m/60)+" 小时 "+(m%60)+" 分" : m+" 分钟";
const fmtD = d => d.replace(/-/g,'.');

document.getElementById("lead").innerHTML =
  fmtD(L.periodStart)+' — '+fmtD(L.periodEnd)+' · '+L.periodDays+' 天里有 '+L.daysUsed+' 天戴着耳机';

function card(k,v,u,n,idx){
  return '<div class="card"><div class="idx">'+idx+'</div><div class="k">'+k+'</div><div class="v">'+v+(u?'<small>'+u+'</small>':'')+'</div>'+(n?'<div class="n">'+n+'</div>':'')+'</div>';
}
document.getElementById("lc").innerHTML =
  card('使用次数', L.totalSessions.toLocaleString(), '次', '不足 1 分钟不计', '01')+
  card('平均每次', L.avgSession, '分钟', '连续聆听时长', '02')+
  card('最长一次', L.maxSession, '分钟', '= '+fmt(L.maxSession), '03')+
  card('单日最多', L.maxDay.minutes, '分钟', L.maxDay.date, '04')+
  card('使用天数', L.daysUsed, '天', '占 '+L.periodDays+' 天的 '+Math.round(L.daysUsed/L.periodDays*100)+'%', '05')+
  card('使用日平均', L.avgPerUsedDay, '分钟', '只算有记录的日子', '06');

document.getElementById("wc").innerHTML =
  card('佩戴天数', W.daysWorn, '天', '', '01')+
  card('累计佩戴', W.totalHours.toLocaleString(), '小时', '', '02')+
  card('日均佩戴', W.avgHoursPerWornDay, '小时', '只算戴表的日子', '03');

// 热力图渲染
function heatmap(el, data, maxV, unit, label){
  const map={}; data.forEach(x=>map[x.d]=x[unit]);
  const days=[]; const d0=new Date(data[0].d), d1=new Date(data[data.length-1].d);
  for(let d=new Date(d0); d<=d1; d.setDate(d.getDate()+1)) days.push(d.toISOString().slice(0,10));
  const cols={}; days.forEach(dd=>{ const k=dd.slice(0,7); (cols[k]=cols[k]||[]).push([dd, map[dd]||0]); });
  let html='<div style="display:flex;gap:10px;flex-wrap:wrap">';
  for(const k of Object.keys(cols)){
    const cells=cols[k].map(([dd,v])=>{
      const t=v/maxV;
      const bg=t<=0?'rgba(255,255,255,.04)':t<.2?'rgba(56,224,176,.18)':t<.4?'rgba(56,224,176,.35)':t<.6?'rgba(56,224,176,.55)':t<.8?'rgba(56,224,176,.75)':'rgba(56,224,176,.95)';
      return '<i title="'+dd+'：'+(v?v+label:'无')+'" style="display:block;width:11px;height:11px;border-radius:2px;background:'+bg+'"></i>';
    }).join('');
    html+='<div><div style="color:var(--dim);font-size:9.5px;margin-bottom:4px">'+k.slice(2)+'</div><div style="display:grid;grid-template-columns:repeat(7,11px);gap:2px">'+cells+'</div></div>';
  }
  html+='</div>';
  el.innerHTML=html;
}
const maxMin = Math.max(...L.byDay.map(x=>x.min),1);
heatmap(document.getElementById("heat"), L.byDay, maxMin, 'min', ' 分钟');
document.getElementById("heatMeta").textContent = '最深 '+L.maxDay.date+' · '+fmt(L.maxDay.minutes);
heatmap(document.getElementById("wear"), W.byDay, 24, 'h', ' 小时');
document.getElementById("wearMeta").textContent = W.periodStart+' — '+W.periodEnd;

const hourC = echarts.init(document.getElementById("hourChart"));
hourC.setOption({
  tooltip:{trigger:"axis",formatter:p=>p[0].axisValue+'：'+fmt(p[0].value)},
  grid:{left:8,right:8,top:28,bottom:6,containLabel:true},
  xAxis:{type:"category",data:L.byHour.map(x=>x.h),axisLabel:{color:"#7d9a90",fontSize:9,interval:2},axisLine:{lineStyle:{color:"rgba(255,255,255,.1)"}},axisTick:{show:false}},
  yAxis:{type:"value",show:false},
  series:[{type:"bar",data:L.byHour.map(x=>x.min),itemStyle:{color:new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:"#38e0b0"},{offset:1,color:"rgba(56,224,176,.15)"}]),borderRadius:[3,3,0,0]},
    label:{show:true,position:"top",color:"#38e0b0",fontSize:9,formatter:p=>p.value>0?p.value:''}}]
});
const peak = L.byHour.reduce((a,b)=>b.min>a.min?b:a);
document.getElementById("hourMeta").textContent = '峰值 '+peak.h+':00 · '+fmt(peak.min);

const weekC = echarts.init(document.getElementById("weekChart"));
const wd=["周一","周二","周三","周四","周五","周六","周日"];
weekC.setOption({
  tooltip:{trigger:"axis",formatter:p=>p[0].axisValue+'：'+fmt(p[0].value)},
  grid:{left:8,right:8,top:28,bottom:6,containLabel:true},
  xAxis:{type:"category",data:wd,axisLabel:{color:"#7d9a90",fontSize:9},axisLine:{lineStyle:{color:"rgba(255,255,255,.1)"}},axisTick:{show:false}},
  yAxis:{type:"value",show:false},
  series:[{type:"bar",data:L.byWeekday,itemStyle:{color:new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:"#4ab8d8"},{offset:1,color:"rgba(74,184,216,.15)"}]),borderRadius:[3,3,0,0]},
    label:{show:true,position:"top",color:"#4ab8d8",fontSize:9}}]
});
const maxW = L.byWeekday.indexOf(Math.max(...L.byWeekday));
document.getElementById("weekMeta").textContent = wd[maxW]+' 听得最多';
window.addEventListener("resize",()=>{hourC.resize();weekC.resize()});
</script>
"""
