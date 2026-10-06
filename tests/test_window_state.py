import json
import os
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "desktop"))

import window_state as ws
import launcher as desktop_launcher


class WindowStateTests(unittest.TestCase):
    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        self.patcher = patch.dict(os.environ, {"APPDATA": self.temp_directory.name})
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        self.temp_directory.cleanup()

    def test_returns_defaults_when_no_file_exists(self):
        state = ws.load_state()

        self.assertEqual(
            state,
            {"width": ws.DEFAULT_WIDTH, "height": ws.DEFAULT_HEIGHT, "x": None, "y": None, "maximized": False},
        )

    def test_saves_and_restores_state(self):
        ws.save_state(1600, 950, True)

        self.assertEqual(
            ws.load_state(),
            {"width": 1600, "height": 950, "x": None, "y": None, "maximized": True},
        )

    def test_clamps_saved_window_size_to_available_display_bounds(self):
        state = ws.clamp_state_to_bounds(
            {"width": 1796, "height": 1113, "x": 0, "y": 0, "maximized": False}, 1536, 816
        )

        self.assertEqual(state, {"width": 1536, "height": 816, "x": 0, "y": 0, "maximized": False})

    def test_clamps_saved_position_to_display_work_area(self):
        state = ws.clamp_state_to_bounds(
            {"width": 900, "height": 700, "x": -400, "y": 900, "maximized": False},
            1536,
            816,
            0,
            0,
        )

        self.assertEqual(state, {"width": 900, "height": 700, "x": 0, "y": 116, "maximized": False})

    def test_persists_window_position(self):
        ws.save_state(1200, 750, False, 64, 38)

        self.assertEqual(ws.load_state(), {"width": 1200, "height": 750, "x": 64, "y": 38, "maximized": False})

    def test_minimized_window_dimensions_are_not_persisted(self):
        window = MagicMock(width=199, height=34)

        with patch("launcher.save_state") as save:
            persisted = desktop_launcher._persist_window_state(window, False)

        self.assertFalse(persisted)
        save.assert_not_called()

    def test_persist_window_state_saves_normal_geometry(self):
        window = MagicMock(width=1200, height=800, x=72, y=46)

        with patch("launcher.save_state") as save:
            self.assertTrue(desktop_launcher._persist_window_state(window, False))

        save.assert_called_once_with(1200, 800, False, 72, 46)

    def test_persisting_maximized_state_keeps_last_normal_geometry(self):
        ws.save_state(1200, 800, False, 72, 46)
        window = MagicMock(width=1536, height=816, x=0, y=0)

        self.assertTrue(desktop_launcher._persist_window_state(window, True))

        self.assertEqual(ws.load_state(), {"width": 1200, "height": 800, "x": 72, "y": 46, "maximized": True})

    def test_falls_back_to_defaults_on_corrupt_file(self):
        path = ws.state_file_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("not json")

        state = ws.load_state()

        self.assertEqual(state["width"], ws.DEFAULT_WIDTH)
        self.assertEqual(state["height"], ws.DEFAULT_HEIGHT)

    def test_clamps_undersized_values_to_defaults(self):
        ws.save_state(10, 10, False)

        state = ws.load_state()

        self.assertEqual(state["width"], ws.DEFAULT_WIDTH)
        self.assertEqual(state["height"], ws.DEFAULT_HEIGHT)

    def test_state_file_lives_under_appdata(self):
        ws.save_state(1440, 900, False)

        path = ws.state_file_path()
        self.assertTrue(str(path).startswith(self.temp_directory.name))
        self.assertEqual(json.loads(path.read_text())["width"], 1440)


class WindowsTaskbarIconTests(unittest.TestCase):
    def test_desktop_window_uses_native_resizable_frame(self):
        webview_module = types.ModuleType("webview")
        webview_module.create_window = MagicMock(return_value=MagicMock())
        webview_module.start = MagicMock()

        with patch.dict(sys.modules, {"webview": webview_module}):
            with patch.object(desktop_launcher, "_set_windows_app_identity"):
                with patch.object(desktop_launcher, "_start_streamlit") as start_server:
                    with patch.object(desktop_launcher, "_wait_until_healthy", return_value=True):
                        with patch.object(desktop_launcher, "_windows_work_area", return_value=None):
                            start_server.return_value.poll.return_value = 0
                            desktop_launcher._run_window(8765)

        options = webview_module.create_window.call_args.kwargs
        self.assertFalse(options["frameless"])
        self.assertTrue(options["resizable"])
        webview_module.create_window.return_value.evaluate_js.assert_not_called()

    def test_streamlit_packaged_flags_disable_development_mode(self):
        options = desktop_launcher._streamlit_flag_options(8765)

        self.assertFalse(options["global_developmentMode"])
        self.assertEqual(options["server_address"], "127.0.0.1")
        self.assertEqual(options["server_port"], 8765)

    def test_applies_shortcut_icon_to_native_window(self):
        window = MagicMock(uid="halo-window")
        form = MagicMock(InvokeRequired=True)
        form.Invoke.side_effect = lambda callback: callback()
        icon = MagicMock(name="native-icon")
        icon_factory = MagicMock(return_value=icon)
        system_module = types.ModuleType("System")
        system_module.Action = lambda callback: callback
        drawing_module = types.ModuleType("System.Drawing")
        drawing_module.Icon = icon_factory
        winforms_module = types.ModuleType("webview.platforms.winforms")
        winforms_module.BrowserView = MagicMock(instances={"halo-window": form})

        with tempfile.TemporaryDirectory() as directory:
            icon_path = Path(directory) / "halo.ico"
            icon_path.write_bytes(b"test-icon")
            with patch.object(desktop_launcher.sys, "platform", "win32"):
                with patch.dict(sys.modules, {
                    "System": system_module,
                    "System.Drawing": drawing_module,
                    "webview.platforms.winforms": winforms_module,
                }):
                    applied = desktop_launcher._set_windows_window_icon(window, icon_path)

        self.assertTrue(applied)
        icon_factory.assert_called_once_with(str(icon_path))
        self.assertIs(form.Icon, icon)
        self.assertTrue(form.ShowIcon)
        self.assertIs(window._halo_taskbar_icon, icon)

if __name__ == "__main__":
    unittest.main()
