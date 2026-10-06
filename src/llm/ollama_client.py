from dataclasses import dataclass
import json
import urllib.error
import urllib.request

from settings import get_ollama_base_url, get_ollama_timeout, get_recommended_model


@dataclass
class LLMResult:
    ok: bool
    text: str = ""
    error: str = ""


class OllamaClient:
    def __init__(self, model=None, base_url=None, timeout=None):
        self.model = model or get_recommended_model()
        self.base_url = (base_url or get_ollama_base_url()).rstrip("/")
        self.timeout = timeout if timeout is not None else get_ollama_timeout()

    def generate(self, prompt):
        try:
            request = urllib.request.Request(
                f"{self.base_url}/api/generate",
                data=json.dumps(
                    {
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "think": False,
                        "options": {"num_predict": 160},
                    }
                ).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )

            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.URLError as error:
            return LLMResult(ok=False, error=f"Ollama unavailable: {error.reason}")
        except TimeoutError:
            return LLMResult(ok=False, error="Ollama request timed out")
        except OSError as error:
            return LLMResult(ok=False, error=f"Ollama request failed: {error}")
        except json.JSONDecodeError:
            return LLMResult(ok=False, error="Ollama returned an invalid response")
        except (UnicodeDecodeError, ValueError):
            return LLMResult(ok=False, error="Ollama configuration or response is invalid")

        if not isinstance(payload, dict):
            return LLMResult(ok=False, error="Ollama returned an invalid response")

        text = payload.get("response", "")

        if not isinstance(text, str):
            return LLMResult(ok=False, error="Ollama returned an invalid response")

        text = text.strip()

        if not text:
            return LLMResult(ok=False, error="Ollama returned an empty response")

        return LLMResult(ok=True, text=text)
