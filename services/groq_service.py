import time
from pathlib import Path

import requests

from config import BASE_DIR, GROQ_API_KEY, GROQ_API_URL, GROQ_MODEL

PROMPTS_DIR = BASE_DIR / "prompts"

SYSTEM_MESSAGE = (
    "You are an expert fact-checker, media-literacy analyst and misinformation "
    "researcher. Be objective and evidence-based. Never declare a claim true or "
    "false unless the provided content supports it. Always respond in "
    "well-structured Markdown."
)

MAX_RETRIES = 2


class GroqServiceError(Exception):
    pass


def load_prompt(name: str) -> str:
    path = PROMPTS_DIR / name
    if not path.exists():
        raise GroqServiceError(f"Prompt template missing: {name}")
    return path.read_text(encoding="utf-8")


def analyze(prompt_file: str, **kwargs) -> str:
    """Render a prompt template and call the Groq chat completions API."""
    if not GROQ_API_KEY:
        raise GroqServiceError(
            "GROQ_API_KEY is not configured. Copy .env.example to .env and add your key."
        )
    user_prompt = load_prompt(prompt_file).format(**kwargs)

    for attempt in range(MAX_RETRIES + 1):
        try:
            resp = requests.post(
                GROQ_API_URL,
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": GROQ_MODEL,
                    "messages": [
                        {"role": "system", "content": SYSTEM_MESSAGE},
                        {"role": "user", "content": user_prompt},
                    ],
                    "temperature": 0.2,
                    "max_tokens": 3000,
                },
                timeout=60,
            )
        except requests.Timeout:
            raise GroqServiceError("Groq API request timed out. Please try again.")
        except requests.RequestException as exc:
            raise GroqServiceError(f"Network error reaching Groq API: {exc}")

        if resp.status_code == 429 and attempt < MAX_RETRIES:
            time.sleep(2 ** attempt)
            continue
        if resp.status_code != 200:
            raise GroqServiceError(
                f"Groq API error {resp.status_code}: {resp.text[:300]}"
            )

        data = resp.json()
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError):
            raise GroqServiceError("Unexpected Groq API response format.")

    raise GroqServiceError("Groq API rate limit exceeded. Please try again later.")
