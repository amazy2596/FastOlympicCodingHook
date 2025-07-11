import sublime
import sublime_plugin
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import _thread
import threading
import os
from os import path
from datetime import datetime
import traceback

def slugify(name):
    if not isinstance(name, str):
        name = str(name) if name is not None else "untitled"
    return ''.join(c if c.isalnum() or c == '_' else '_' for c in name).strip('_')

def make_cpp_template(name, url, group, time_limit, memory_limit):
    return (
        "#include <bits/stdc++.h>\n"
        "#define uint uint64_t\n"
        "#define int long long\n"
        "using namespace std;\n\n"
        "// Problem: {name}\n"
        "// Contest: {group}\n"
        "// URL: {url}\n\n"
        "vector<pair<int, int>> dir8 = {{ {{1, 0}}, {{1, 1}}, {{0, 1}}, {{-1, 1}}, {{-1, 0}}, {{-1, -1}}, {{0, -1}}, {{1, -1}} }};\n"
        "vector<pair<int, int>> dir4 = {{ {{1, 0}}, {{0, 1}}, {{-1, 0}}, {{0, -1}} }};\n"
        "const int inf = 1e18;\n\n"
        "mt19937_64 rng(chrono::steady_clock::now().time_since_epoch().count());\n"
        "auto rnd = [](uint l, uint r) {{ return (l <= r ? uniform_int_distribution<uint>(l, r)(rng) : 0); }};\n\n"
        "void solve()\n"
        "{{\n"
        "    \n"
        "}}\n\n"
        "signed main()\n"
        "{{\n"
        "    // ios::sync_with_stdio(false);\n"
        "    // cout.tie(nullptr);\n"
        "    // cin.tie(nullptr);\n"
        "    // init();\n"
        "    int T = 1;\n"
        "    // cin >> T;\n"
        "    while (T--)\n"
        "        solve();\n"
        "    return 0;\n"
        "}}\n"
    ).format(name=name, url=url, group=group, time_limit=time_limit, memory_limit=memory_limit)

def MakeHandlerClass(foc_settings):
    tests_file_suffix = foc_settings.get("tests_file_suffix", "_tests.in")
    use_title = foc_settings.get("use_title_as_filename", True)

    # 基于日期的输出路径
    today = datetime.today()
    base_dir = os.path.expanduser("C:/c++")
    cpp_output_dir = os.path.join(
        base_dir,
        "program_{:04d}".format(today.year),
        "program_{:02d}".format(today.month),
        "program_{:02d}".format(today.day)
    )
    test_output_dir = os.path.join(base_dir, "data", "input")

    class HandleRequests(BaseHTTPRequestHandler):
        def do_POST(self):
            try:
                content_length = int(self.headers['Content-Length'])
                body = self.rfile.read(content_length)
                data = json.loads(body.decode('utf8'))

                # 字段防御
                title = data.get("title") or "untitled"
                name = data.get("name") or "Unknown Problem"
                url = data.get("url", "")
                group = data.get("group", "")
                time_limit = data.get("timeLimit", 1000)
                memory_limit = data.get("memoryLimit", 256)
                tests = data.get("tests", [])

                filename_base = slugify(title if use_title else name)
                cpp_filename = filename_base + ".cpp"
                cpp_path = path.join(cpp_output_dir, cpp_filename)
                os.makedirs(cpp_output_dir, exist_ok=True)

                # 写入 cpp 文件
                if not path.exists(cpp_path):
                    template_content = make_cpp_template(
                        name=name,
                        url=url,
                        group=group,
                        time_limit=time_limit,
                        memory_limit=memory_limit
                    )
                    with open(cpp_path, "w", encoding="utf8") as f:
                        f.write(template_content)

                # 写入测试数据
                os.makedirs(test_output_dir, exist_ok=True)
                test_filename = filename_base + ".cpp_tests.in"  # e.g. A___G1.cpp_tests.in
                test_path = path.join(test_output_dir, test_filename)
                formatted_tests = []
                for test in tests:
                    formatted_tests.append({
                        "test": test["input"],
                        "correct_answers": [test["output"].strip()]
                    })
                with open(test_path, "w", encoding="utf8") as f:
                    f.write(json.dumps(formatted_tests, indent=2))

                # 打开 cpp 文件
                sublime.active_window().open_file(cpp_path)
                print("[Hook] Created: {}".format(cpp_path))
                print("[Hook] Test cases: {}".format(test_path))
            except Exception as e:
                print("[Hook] Error:", e)
                traceback.print_exc()

    return HandleRequests

class CompetitiveCompanionServer:
    def startServer(foc_settings):
        host = 'localhost'
        port = 12345
        HandlerClass = MakeHandlerClass(foc_settings)
        try:
            httpd = HTTPServer((host, port), HandlerClass)
            print("[Hook] Listening on {}:{} ...".format(host, port))
            httpd.serve_forever()
        except OSError as e:
            print("[Hook] Port {} in use or failed: {}".format(port, e))

def plugin_loaded():
    try:
        foc_settings = sublime.load_settings("FastOlympicCoding.sublime-settings")
        _thread.start_new_thread(
            CompetitiveCompanionServer.startServer,
            (foc_settings,)
        )
        print("[Hook] Auto-listening for Competitive Companion...")
    except Exception as e:
        print("[Hook] Auto-startup error:", e)
