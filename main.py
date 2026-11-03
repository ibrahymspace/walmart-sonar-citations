"""One Perplexity Sonar call about Walmart, sent through OpenRouter.

Prints the answer text, then every citation URL from the response's own
citation field (never from the answer text).

  python main.py            # live call
  python main.py --sample   # same printing code on openrouter_sonar_sample_response.json
"""

import argparse
import json
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "perplexity/sonar"
SAMPLE = Path(__file__).with_name("openrouter_sonar_sample_response.json")

QUESTION = """Research Walmart for a B2B sales rep preparing a first meeting. Cover three things:
1. Strategic priorities from the last 4 quarters of earnings calls or investor material.
2. Public evidence of a rival data platform in production, such as Databricks, Google BigQuery,
   Teradata or Azure Synapse. If no source shows one in production, say so plainly; do not guess.
3. Current data and AI initiatives.
Cite a source for every claim."""


def call_sonar() -> dict:
    # override=True: the key in .env wins over any stale OPENROUTER_API_KEY
    # already exported in the shell.
    load_dotenv(override=True)
    key = os.environ.get("OPENROUTER_API_KEY", "").strip().strip('"').strip("'")
    if not key:
        sys.exit("OPENROUTER_API_KEY is empty. Put it in .env after OPENROUTER_API_KEY=")
    if not key.startswith("sk-or-"):
        sys.exit(f"OPENROUTER_API_KEY doesn't look like an OpenRouter key "
                 f"(should start with sk-or-, is {len(key)} chars). Re-copy it from "
                 "openrouter.ai/settings/keys.")
    resp = requests.post(
        URL,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json={"model": MODEL, "messages": [{"role": "user", "content": QUESTION}]},
        timeout=120,
    )
    if resp.status_code != 200:
        sys.exit(f"Error {resp.status_code}: {resp.text}")
    return resp.json()


def citation_urls(payload: dict) -> list[str]:
    """URLs from the response's citation field, not the answer text.

    Perplexity returns them as a top-level `citations` list. OpenRouter may also
    (or instead) put them in message.annotations as url_citation entries.
    """
    urls = list(payload.get("citations") or [])
    message = payload["choices"][0]["message"]
    for ann in message.get("annotations") or []:
        url = (ann.get("url_citation") or {}).get("url")
        if url and url not in urls:
            urls.append(url)
    return urls


def print_result(payload: dict) -> None:
    print("=== Answer ===")
    print(payload["choices"][0]["message"]["content"])
    urls = citation_urls(payload)
    print("\n=== Citations ===")
    for i, url in enumerate(urls, 1):
        print(f"{i}. {url}")
    if len(urls) < 2:
        print(f"Only {len(urls)} citation URL(s) came back.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", action="store_true",
                        help=f"print from {SAMPLE.name} instead of calling the API")
    args = parser.parse_args()
    if args.sample:
        if not SAMPLE.exists():
            sys.exit(f"{SAMPLE.name} not found next to main.py")
        payload = json.loads(SAMPLE.read_text())
    else:
        payload = call_sonar()
    print_result(payload)


if __name__ == "__main__":
    main()
