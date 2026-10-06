"""Desktop window wrapper for Halo.

Starts the existing Streamlit app as a background process and hosts it in a
native window via pywebview, instead of opening it in a browser tab. The
Streamlit UI, pages, and backend are untouched -- this only changes how the
app is presented.

Run directly for development:

    python desktop/launcher.py

Build a standalone Windows executable with PyInstaller using desktop/halo.spec
(see the "Desktop app" section in README.md).

Frozen builds have no separate python.exe to re-invoke as "python -m
streamlit", since the executable itself is the interpreter. To avoid that,
a frozen build re-launches itself with an internal "--halo-server <port>"
flag; that child process runs Streamlit's server directly (bootstrap.run)
on its own main thread, since Streamlit installs signal handlers that only
work on a process's main thread and cannot run on a background thread.
"""

import os
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

SERVER_FLAG = "--halo-server"
APP_USER_MODEL_ID = "HaveshRavi.Halo"
DEFAULT_PORT = 8765
HEALTH_POLL_ATTEMPTS = 40
HEALTH_POLL_INTERVAL = 0.5
WINDOW_STATE_SAVE_DELAY = 0.45

sys.path.insert(0, str(Path(__file__).resolve().parent))
from window_state import MIN_HEIGHT, MIN_WIDTH, clamp_state_to_bounds, load_state, save_state  # noqa: E402


def _is_frozen():
    return bool(getattr(sys, "frozen", False))


def _project_root():
    if _is_frozen():
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).resolve().parent))

    return Path(__file__).resolve().parents[1]


def _app_entry():
    return _project_root() / "ui" / "app.py"


def _shortcut_icon():
    return _project_root() / "assets" / "halo-shortcut.ico"


def _set_windows_app_identity():
    if sys.platform != "win32":
        return

    import ctypes

    result = ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_USER_MODEL_ID)
    if result != 0:
        raise OSError(f"Could not set Halo's Windows taskbar identity: HRESULT {result}")


def _windows_work_area():
    import ctypes

    class Rect(ctypes.Structure):
        _fields_ = [
            ("left", ctypes.c_long),
            ("top", ctypes.c_long),
            ("right", ctypes.c_long),
            ("bottom", ctypes.c_long),
        ]

    rect = Rect()
    success = ctypes.windll.user32.SystemParametersInfoW(
        0x0030,
        0,
        ctypes.byref(rect),
        0,
    )
    if not success:
        return None

    return rect.right - rect.left, rect.bottom - rect.top


def _set_windows_window_icon(window, icon_path=None):
    if sys.platform != "win32":
        return False

    icon_path = Path(icon_path or _shortcut_icon())
    if not icon_path.is_file():
        return False

    from System import Action
    from System.Drawing import Icon
    from webview.platforms.winforms import BrowserView

    form = BrowserView.instances.get(window.uid)
    if form is None:
        return False

    icon = Icon(str(icon_path))

    def apply_icon():
        form.Icon = icon
        form.ShowIcon = True

    if form.InvokeRequired:
        form.Invoke(Action(apply_icon))
    else:
        apply_icon()

    window._halo_taskbar_icon = icon
    return True


def _persist_window_state(window, maximized):
    previous = load_state()
    if maximized:
        save_state(previous["width"], previous["height"], True, previous.get("x"), previous.get("y"))
        return True

    width, height = window.width, window.height
    if width < MIN_WIDTH or height < MIN_HEIGHT:
        return False

    save_state(width, height, False, window.x, window.y)
    return True


def _port():
    try:
        return int(os.getenv("HALO_DESKTOP_PORT", DEFAULT_PORT))
    except ValueError:
        return DEFAULT_PORT


def _popen_kwargs():
    kwargs = {"cwd": str(_project_root())}
    if sys.platform.startswith("win"):
        kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
    else:
        kwargs["start_new_session"] = True
    return kwargs


def _start_streamlit(port):
    if _is_frozen():
        command = [sys.executable, SERVER_FLAG, str(port)]
    else:
        command = [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(_app_entry()),
            "--server.headless=true",
            "--server.address=127.0.0.1",
            f"--server.port={port}",
            "--browser.gatherUsageStats=false",
        ]

    return subprocess.Popen(command, **_popen_kwargs())


def _streamlit_flag_options(port):
    return {
        "server_headless": True,
        "server_address": "127.0.0.1",
        "server_port": port,
        "browser_gatherUsageStats": False,
        "global_developmentMode": False,
    }


def _run_server_inline(port):
    """Run Streamlit's server directly in this process's main thread.

    Only used by the child process a frozen build spawns for itself; never
    called from the window-hosting process, since this call blocks forever.
    """
    from streamlit.web import bootstrap

    flag_options = _streamlit_flag_options(port)
    bootstrap.load_config_options(flag_options=flag_options)
    bootstrap.run(str(_app_entry()), False, [], flag_options)


def _wait_until_healthy(url):
    health_url = f"{url}/_stcore/health"

    for _ in range(HEALTH_POLL_ATTEMPTS):
        try:
            with urllib.request.urlopen(health_url, timeout=2) as response:
                if response.status == 200:
                    return True
        except (urllib.error.URLError, ConnectionError, TimeoutError):
            pass

        time.sleep(HEALTH_POLL_INTERVAL)

    return False


def _run_window(port):
    _set_windows_app_identity()
    import webview

    url = f"http://127.0.0.1:{port}"
    process = _start_streamlit(port)

    try:
        if not _wait_until_healthy(url):
            print("Halo did not start in time. Check that port", port, "is free.")
            return

        state = load_state()
        if sys.platform == "win32":
            work_area = _windows_work_area()
            if work_area:
                state = clamp_state_to_bounds(state, *work_area)

        window = webview.create_window(
            "Halo",
            url,
            width=state["width"],
            height=state["height"],
            x=state.get("x"),
            y=state.get("y"),
            min_size=(MIN_WIDTH, MIN_HEIGHT),
            maximized=state["maximized"],
            resizable=True,
            frameless=False,
        )

        maximized_flag = {"value": state["maximized"]}

        pending_state_save = {"timer": None}

        def _persist_now():
            pending_state_save["timer"] = None
            _persist_window_state(window, maximized_flag["value"])

        def _schedule_persist(*_):
            current = pending_state_save["timer"]
            if current:
                current.cancel()
            timer = threading.Timer(WINDOW_STATE_SAVE_DELAY, _persist_now)
            timer.daemon = True
            pending_state_save["timer"] = timer
            timer.start()

        def _persist_on_close(*_):
            timer = pending_state_save["timer"]
            if timer:
                timer.cancel()
                pending_state_save["timer"] = None
            _persist_now()

        def _mark_maximized():
            maximized_flag["value"] = True
            _persist_on_close()

        def _mark_restored():
            maximized_flag["value"] = False
            _schedule_persist()

        if sys.platform == "win32":
            def _finish_native_window_setup():
                _set_windows_window_icon(window)

            window.events.shown += _finish_native_window_setup

        window.events.resized += _schedule_persist
        window.events.moved += _schedule_persist
        window.events.closing += _persist_on_close
        window.events.maximized += _mark_maximized
        window.events.restored += _mark_restored

        webview.start()
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()


def main():
    if len(sys.argv) >= 3 and sys.argv[1] == SERVER_FLAG:
        _run_server_inline(int(sys.argv[2]))
        return

    _run_window(_port())


if __name__ == "__main__":
    main()
