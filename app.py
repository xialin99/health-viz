#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""HealthViz — Apple Health 数据可视化

用法：
    python3 app.py

零依赖，只用 Python 标准库。启动后自动打开浏览器。
数据全部留在本地，不上传任何服务器。
"""
import os, sys, json, re, tempfile, threading, webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from parser import parse
from analyze import headphone_sessions, watch_wear, summarize
import render

PORT = int(os.environ.get("PORT", 8765))
UPLOAD_DIR = os.path.join(HERE, ".uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

STATE = {"status": "idle", "progress": "", "result": None, "error": ""}


def run_analysis(zip_path):
    global STATE
    try:
        STATE["status"] = "parsing"; STATE["progress"] = "正在读取文件…"
        data = parse(zip_path, progress=lambda m: STATE.update(progress=m))
        STATE["progress"] = "正在切分聆听会话…"
        sessions = headphone_sessions(data["headphone"])
        STATE["progress"] = "正在统计手表佩戴…"
        wear = watch_wear(data["stand"])
        STATE["progress"] = "正在汇总…"
        result = summarize(sessions, wear)
        if not result:
            raise RuntimeError("没有找到耳机聆听记录")
        STATE["result"] = result
        STATE["status"] = "done"
        STATE["progress"] = "完成"
    except Exception as e:
        STATE["status"] = "error"
        STATE["error"] = str(e)
        STATE["progress"] = "失败"


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, body, ctype="text/html; charset=utf-8", code=200):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/":
            self._send(render.upload_page())
        elif self.path == "/status":
            self._send(json.dumps({k: v for k, v in STATE.items() if k != "result"}), "application/json")
        elif self.path == "/result":
            if STATE["result"] is None:
                self._send("<h1>还没有数据</h1><a href='/'>返回</a>", code=404)
            else:
                self._send(render.result_page(STATE["result"]))
        elif self.path == "/reset":
            STATE.update({"status": "idle", "progress": "", "result": None, "error": ""})
            self.send_response(302)
            self.send_header("Location", "/")
            self.end_headers()
        else:
            self._send("not found", code=404)

    def do_POST(self):
        if self.path != "/upload":
            self._send("not found", code=404); return
        ctype = self.headers.get("Content-Type", "")
        m = re.search(r"boundary=(.+)", ctype)
        if not m:
            self._send("bad request", code=400); return
        bnd = m.group(1).strip('"').encode()
        clen = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(clen)
        saved = None
        for part in raw.split(b"--" + bnd):
            if b"filename=" not in part:
                continue
            fn = re.search(rb'filename="([^"]+)"', part)
            if not fn:
                continue
            name = os.path.basename(fn.group(1).decode("utf-8", "ignore"))
            if not name.lower().endswith(".zip"):
                continue
            body = part.split(b"\r\n\r\n", 1)[1].rsplit(b"\r\n", 1)[0]
            path = os.path.join(UPLOAD_DIR, "health_export.zip")
            with open(path, "wb") as f:
                f.write(body)
            saved = path
        if not saved:
            self._send("no zip", code=400); return
        STATE.update({"status": "parsing", "progress": "开始处理", "result": None, "error": ""})
        threading.Thread(target=run_analysis, args=(saved,), daemon=True).start()
        self._send(json.dumps({"ok": True}), "application/json")


def main():
    url = "http://127.0.0.1:%d" % PORT
    print("\n  HealthViz 已启动：%s" % url)
    print("  数据全部在本地处理，不上传任何服务器\n")
    threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    HTTPServer(("127.0.0.1", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
