import os
import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen


def test_local_runserver_serves_compiled_stylesheets():
    root = Path(__file__).resolve().parent.parent
    env = os.environ.copy()
    env.pop("DJANGO_SETTINGS_MODULE", None)
    env.pop("DJANGO_DEBUG", None)
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    server = subprocess.Popen(
        [sys.executable, "manage.py", "runserver", f"127.0.0.1:{port}", "--noreload"],
        cwd=root,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        for _ in range(100):
            try:
                with urlopen(f"http://127.0.0.1:{port}/", timeout=1) as response:
                    html = response.read().decode()
                break
            except URLError, TimeoutError:
                if server.poll() is not None:
                    raise AssertionError("Development server exited before startup") from None
                time.sleep(0.1)
        else:
            raise AssertionError("Development server did not start")
        for path, expected in [
            ("app.css", b"tailwindcss"),
            ("site.css", b".app-shell"),
            ("premium.css", b".score-ring"),
        ]:
            assert f"/static/css/{path}" in html
            with urlopen(f"http://127.0.0.1:{port}/static/css/{path}", timeout=5) as response:
                assert response.status == 200
                assert response.headers.get_content_type() == "text/css"
                assert expected in response.read()
        for font in ("inter-latin-wght-normal.woff2", "plus-jakarta-sans-latin-wght-normal.woff2"):
            with urlopen(f"http://127.0.0.1:{port}/static/fonts/{font}", timeout=5) as response:
                assert response.status == 200
                assert response.read(4) == b"wOF2"
    finally:
        server.terminate()
        server.wait(timeout=10)
