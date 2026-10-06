import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from llm.ollama_client import OllamaClient
from settings import DEFAULT_OLLAMA_TIMEOUT, get_ollama_timeout


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception, traceback):
        return False

    def read(self):
        return self.payload


class OllamaClientTests(unittest.TestCase):
    def test_default_timeout_allows_slow_local_inference(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(get_ollama_timeout(), 300)

    def test_parses_successful_response(self):
        payload = json.dumps({"response": "  Ready to help.  "}).encode("utf-8")

        with patch("urllib.request.urlopen", return_value=FakeResponse(payload)):
            result = OllamaClient().generate("hello")

        self.assertTrue(result.ok)
        self.assertEqual(result.text, "Ready to help.")

    def test_limits_generated_tokens(self):
        payload = json.dumps({"response": "Ready."}).encode("utf-8")

        with patch("urllib.request.urlopen", return_value=FakeResponse(payload)) as urlopen:
            OllamaClient().generate("hello")

        request = urlopen.call_args.args[0]
        request_body = json.loads(request.data.decode("utf-8"))
        self.assertFalse(request_body["think"])
        self.assertEqual(request_body["options"]["num_predict"], 160)

    def test_handles_non_object_json_response(self):
        with patch("urllib.request.urlopen", return_value=FakeResponse(b"[]")):
            result = OllamaClient().generate("hello")

        self.assertFalse(result.ok)
        self.assertEqual(result.error, "Ollama returned an invalid response")

    def test_handles_non_string_response_field(self):
        payload = json.dumps({"response": {"text": "unexpected"}}).encode("utf-8")

        with patch("urllib.request.urlopen", return_value=FakeResponse(payload)):
            result = OllamaClient().generate("hello")

        self.assertFalse(result.ok)
        self.assertEqual(result.error, "Ollama returned an invalid response")

    def test_handles_invalid_json(self):
        with patch("urllib.request.urlopen", return_value=FakeResponse(b"not-json")):
            result = OllamaClient().generate("hello")

        self.assertFalse(result.ok)
        self.assertEqual(result.error, "Ollama returned an invalid response")

    def test_invalid_timeout_configuration_uses_default(self):
        with patch.dict(os.environ, {"OLLAMA_TIMEOUT": "not-a-number"}):
            self.assertEqual(get_ollama_timeout(), DEFAULT_OLLAMA_TIMEOUT)

        with patch.dict(os.environ, {"OLLAMA_TIMEOUT": "0"}):
            self.assertEqual(get_ollama_timeout(), DEFAULT_OLLAMA_TIMEOUT)

    def test_invalid_base_url_falls_back_as_error_result(self):
        result = OllamaClient(base_url="not a valid url").generate("hello")

        self.assertFalse(result.ok)
        self.assertIn("invalid", result.error)


if __name__ == "__main__":
    unittest.main()