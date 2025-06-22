import sublime
import sublime_plugin
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import _thread
import threading
import os
from os import path
from datetime import datetime

def slugify(name):
    return ''.join(c if c.isalnum() or c in ['_', '-'] else '_' for c in name).strip('_')

def load_template(template_path, fallback_template):
    template_path = os.path.expanduser(template_path)
    if template_path and path.exists(template_path):
        with open(template_path, "r", encoding="utf8") as f:
            return f.read()
    return fallback_template

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
    tests_file_suffix = foc_settings.get("tests_file_suffix", "_tests.txt")
    use_title = foc_settings.get("use_title_as_filename", True)
    template_path = foc_settings.get("template_file", None)
    fallback_template = make_cpp_template("NAME", "URL", "GROUP", "1000", "256")

    # ✅ 使用今天的日期构造路径
    today = datetime.today()
    base_dir = os.path.expanduser("~/c++")
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

                title = data.get("title", "untitled") or "untitled"
                name = data.get("name", "Unknown Problem") or "Unknown Problem"
                title = slugify(title)
                url = data.get("url", "")
                group = data.get("group", "")
                time_limit = data.get("timeLimit", 1000)
                memory_limit = data.get("memoryLimit", 256)
                tests = data.get("tests", [])

                filename_base = slugify(title if use_title else name)
                cpp_path = path.join(cpp_output_dir, "{}.cpp".format(filename_base))
                os.makedirs(cpp_output_dir, exist_ok=True)

                if not path.exists(cpp_path):
                    template_content = load_template(template_path, fallback_template)
                    template_content = template_content.format(
                        name=name,
                        url=url,
                        group=group,
                        time_limit=time_limit,
                        memory_limit=memory_limit
                    )
                    with open(cpp_path, "w", encoding="utf8") as f:
                        f.write(template_content)

                os.makedirs(test_output_dir, exist_ok=True)
                test_path = path.join(test_output_dir, "{}{}".format(filename_base, tests_file_suffix))
                formatted_tests = []
                for test in tests:
                    formatted_tests.append({
                        "test": test["input"],
                        "correct_answers": [test["output"].strip()]
                    })
                with open(test_path, "w", encoding="utf8") as f:
                    f.write(json.dumps(formatted_tests, indent=2))

                sublime.active_window().open_file(cpp_path)
                print("[Hook] Created: {}".format(cpp_path))
                print("[Hook] Test cases: {}".format(test_path))
            except Exception as e:
                print("[Hook] Error:", e)

    return HandleRequests

class CompetitiveCompanionServer:
    def startServer(foc_settings):
        host = 'localhost'
        port = 12345
        HandlerClass = MakeHandlerClass(foc_settings)
        httpd = HTTPServer((host, port), HandlerClass)
        print("[Hook] Listening on {}:{} ...".format(host, port))
        httpd.serve_forever()

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
