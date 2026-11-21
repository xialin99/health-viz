#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""HealthViz — Apple Health 数据可视化

用法：
    python3 app.py

零依赖，只用 Python 标准库。启动后自动打开浏览器。
数据全部留在本地，不上传任何服务器。
"""
import os, sys, json, tempfile, threading, webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from parser import parse
from analyze import headphone_sessions, watch_wear, summarize
import render

PORT = int(os.environ.get("PORT", 8765))

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
        if not sessions and not wear:
            raise ValueError("没有找到支持的耳机或手表记录")
        STATE["result"] = result
        STATE["status"] = "done"
        STATE["progress"] = "完成"
    except Exception as e:
        STATE["status"] = "error"
        STATE["error"] = str(e)
        STATE["progress"] = "失败"
    finally:
        os.unlink(zip_path)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, body, ctype="text/html; charset=utf-8", code=200):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
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
            if STATE["status"] == "parsing":
                self._send("请等待当前分析结束", code=409)
                return
            STATE.update({"status": "idle", "progress": "", "result": None, "error": ""})
            self.send_response(302)
            self.send_header("Location", "/")
            self.end_headers()
        else:
            self._send("not found", code=404)

    def do_POST(self):
        if self.path != "/upload":
            self._send("not found", code=404); return
        if STATE["status"] == "parsing":
            self._send("请等待当前分析结束", code=409)
            return
        if self.headers.get("Content-Type") != "application/zip":
            self._send("请选择 ZIP 文件", code=415)
            return
        try:
            remaining = int(self.headers.get("Content-Length", ""))
        except ValueError:
            remaining = 0
        if not 0 < remaining <= 2 * 1024**3:
            self._send("ZIP 文件大小须在 0 至 2 GiB 之间", code=413)
            return
        saved = None
        try:
            self.connection.settimeout(30)
            with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as output:
                saved = output.name
                while remaining:
                    block = self.rfile.read(min(remaining, 1024 * 1024))
                    if not block:
                        raise ValueError("上传中断，请重新选择文件")
                    output.write(block)
                    remaining -= len(block)
        except (OSError, ValueError):
            if saved:
                os.unlink(saved)
            self._send("未能接收完整 ZIP 文件", code=400)
            return
        STATE.update({"status": "parsing", "progress": "开始处理", "result": None, "error": ""})
        threading.Thread(target=run_analysis, args=(saved,), daemon=True).start()
        self._send(json.dumps({"ok": True}), "application/json")


def main():
    try:
        server = HTTPServer(("127.0.0.1", PORT), Handler)
    except OSError as error:
        if error.errno not in (48, 98, 10048):
            raise
        server = HTTPServer(("127.0.0.1", 0), Handler)
    with server:
        url = "http://127.0.0.1:%d/" % server.server_port
        print("HealthViz: " + url, flush=True)
        print("Keep this window open while using HealthViz. Press Ctrl+C to stop.", flush=True)
        threading.Thread(target=webbrowser.open, args=(url,), daemon=True).start()
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()

