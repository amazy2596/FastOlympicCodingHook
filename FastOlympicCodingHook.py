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

def make_cpp_template(name, url, group, time_limit, memory_limit):
    return f'''#include <bits/stdc++.h>
#define uint uint64_t
#define int long long
using namespace std;

// Problem: {name}
// Contest: {group}
// URL: {url}

vector<pair<int, int>> dir8 = {{ {{1, 0}}, {{1, 1}}, {{0, 1}}, {{-1, 1}}, {{-1, 0}}, {{-1, -1}}, {{0, -1}}, {{1, -1}} }};
vector<pair<int, int>> dir4 = {{ {{1, 0}}, {{0, 1}}, {{-1, 0}}, {{0, -1}} }};
const int inf = 1e18;

mt19937_64 rng(chrono::steady_clock::now().time_since_epoch().count());
auto rnd = [](uint l, uint r) {{ return (l <= r ? uniform_int_distribution<uint>(l, r)(rng) : 0); }};

void solve()
{{
    
}}

signed main()
{{
    // ios::sync_with_stdio(false);
    // cout.tie(nullptr);
    // cin.tie(nullptr);
    // init();
    int T = 1;
    // cin >> T;
    while (T--)
        solve();
    return 0;
}}
'''

def MakeHandlerClass(base_dir, tests_relative_dir, tests_file_suffix):
    if not tests_file_suffix:
        tests_file_suffix = "_tests.txt"

    class HandleRequests(BaseHTTPRequestHandler):
        def do_POST(self):
            try:
                content_length = int(self.headers['Content-Length'])
                body = self.rfile.read(content_length)
                data = json.loads(body.decode('utf8'))

                # 获取信息
                title = slugify(data.get("title", "untitled"))
                name = data.get("name", "Unknown Problem")
                url = data.get("url", "")
                group = data.get("group", "")
                time_limit = data.get("timeLimit", 1000)
                memory_limit = data.get("memoryLimit", 256)
                tests = data.get("tests", [])

                # 创建 cpp 文件
                os.makedirs(base_dir, exist_ok=True)
                cpp_filename = f"{title}.cpp"
                cpp_path = path.join(base_dir, cpp_filename)

                if not path.exists(cpp_path):
                    with open(cpp_path, "w") as f:
                        f.write(make_cpp_template(name, url, group, time_limit, memory_limit))

                # 保存测试样例
                test_dir = path.join(base_dir, tests_relative_dir) if tests_relative_dir else base_dir
                os.makedirs(test_dir, exist_ok=True)
                test_path = path.join(test_dir, f"{title}{tests_file_suffix}")
                formatted_tests = []
                for test in tests:
                    formatted_tests.append({
                        "test": test["input"],
                        "correct_answers": [test["output"].strip()]
                    })
                with open(test_path, "w") as f:
                    f.write(json.dumps(formatted_tests, indent=2))

                # 打开 cpp 文件
                sublime.active_window().open_file(cpp_path)
                print(f"Created: {cpp_path}")
                print(f"Saved test cases: {test_path}")
            except Exception as e:
                print("Error:", e)
            threading.Thread(target=self.server.shutdown, daemon=True).start()

    return HandleRequests

class CompetitiveCompanionServer:
    def startServer(base_dir, foc_settings):
        host = 'localhost'
        port = 12345
        tests_relative_dir = foc_settings.get("tests_relative_dir")
        tests_file_suffix = foc_settings.get("tests_file_suffix")
        HandlerClass = MakeHandlerClass(base_dir, tests_relative_dir, tests_file_suffix)
        httpd = HTTPServer((host, port), HandlerClass)
        print(f"[Hook] Listening on {host}:{port} ...")
        httpd.serve_forever()
        print("[Hook] Server shutdown.")

class FastOlympicCodingHookCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        try:
            foc_settings = sublime.load_settings("FastOlympicCoding.sublime-settings")
            base_dir = path.expanduser("~/cp")  # <<< 改成你喜欢保存的目录
            os.makedirs(base_dir, exist_ok=True)

            _thread.start_new_thread(
                CompetitiveCompanionServer.startServer,
                (base_dir, foc_settings)
            )

            sublime.message_dialog("FastOlympicCodingHook: Listening for Competitive Companion...")

        except Exception as e:
            print("Hook Error:", e)
