import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from settings import UI_DEFAULTS, load_ui_preferences, preferences_path, save_ui_preferences
from llm.reasoner import _build_prompt


class UIPreferencesTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.environment = patch.dict(os.environ, {"APPDATA": self.directory.name})
        self.environment.start()

    def tearDown(self):
        self.environment.stop()
        self.directory.cleanup()

    def test_defaults_and_saved_choices_round_trip(self):
        self.assertEqual(load_ui_preferences(), UI_DEFAULTS)
        chosen = dict(UI_DEFAULTS, theme="Light", accent="Blue", response_style="Detailed", default_page="Tasks", show_completed=False)
        save_ui_preferences(chosen)
        self.assertEqual(load_ui_preferences(), chosen)

    def test_invalid_or_damaged_preferences_fall_back(self):
        preferences_path().parent.mkdir(parents=True, exist_ok=True)
        preferences_path().write_text(json.dumps({"theme": "unknown", "show_completed": 1, "accent": "Purple"}))
        self.assertEqual(load_ui_preferences(), dict(UI_DEFAULTS, accent="Purple"))
        preferences_path().write_text("{not-json")
        self.assertEqual(load_ui_preferences(), UI_DEFAULTS)

    def test_response_styles_change_only_delivery_instructions(self):
        prompts = {style: _build_prompt("Answer", "Work plan", {}, style) for style in ("Concise", "Balanced", "Detailed")}
        self.assertIn("one short sentence", prompts["Concise"])
        self.assertIn("two short sentences", prompts["Balanced"])
        self.assertIn("one short paragraph", prompts["Detailed"])
        for prompt in prompts.values():
            self.assertIn("Do not invent meetings", prompt)

    def test_settings_widgets_save_and_apply_preferences(self):
        app = AppTest.from_file(str(PROJECT_ROOT / "ui" / "app.py"), default_timeout=30).run()
        app.radio[0].set_value("Settings").run()
        self.assertFalse(app.exception)
        self.assertEqual([control.label for control in app.get("button_group")], ["Theme", "Accent Color", "Response Style"])
        self.assertEqual([control.value for control in app.get("button_group")], ["Dark", "Halo Green", "Balanced"])
        self.assertEqual([control.label for control in app.selectbox], ["Default Page"])
        app.get("button_group")[0].set_value("Light").run()
        app.get("button_group")[1].set_value("Blue").run()
        app.get("button_group")[2].set_value("Concise").run()
        app.get("toggle")[0].set_value(False).run()
        app.selectbox[0].set_value("Tasks").run()

        self.assertFalse(app.exception)
        self.assertEqual(app.radio[0].value, "Tasks")
        self.assertEqual(load_ui_preferences(), dict(UI_DEFAULTS, theme="Light", accent="Blue", response_style="Concise", default_page="Tasks", show_completed=False))
        self.assertFalse(any("Completed Tasks" in item.value for item in app.markdown))
        app.radio[0].set_value("Settings").run()
        self.assertEqual([control.value for control in app.get("button_group")], ["Light", "Blue", "Concise"])


if __name__ == "__main__":
    unittest.main()