import json
import urllib.request
from dataclasses import dataclass

from playcall_intel.llm_client import LLMClient


@dataclass
class OllamaClient(LLMClient):
    model: str
    base_url: str = "http://localhost:11434"
    timeout_s: int = 120

    def complete_json(self, prompt: str) -> str:
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:
            body = json.loads(resp.read().decode("utf-8"))

        return body["response"]
