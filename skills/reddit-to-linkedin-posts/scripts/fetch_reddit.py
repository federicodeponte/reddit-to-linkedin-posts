#!/usr/bin/env python3
"""Fetch a Reddit thread as JSON and export clean markdown.

Usage:
    python3 fetch_reddit.py <reddit-url-or-json-file>

Examples:
    python3 fetch_reddit.py "https://www.reddit.com/r/startups/comments/abc123/..."
    python3 fetch_reddit.py ./thread.json

Output is markdown written to stdout.
"""

import json
import re
import sys
import urllib.error
import urllib.request
from html import unescape

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"


def is_local_file(path: str) -> bool:
    try:
        return path.endswith(".json") and len(path) < 2048 and path[:1] not in ("h", "w")
    except Exception:
        return False


def normalize_url(raw: str) -> str:
    """Turn a Reddit URL into a JSON endpoint URL."""
    raw = raw.strip()

    if not raw.startswith("http"):
        raw = "https://" + raw

    # Strip existing .json suffix and query strings/fragments.
    parsed = raw.split("?")[0].split("#")[0]
    parsed = parsed.rstrip("/")
    if parsed.endswith(".json"):
        parsed = parsed[: -len(".json")]

    if "/comments/" not in parsed:
        raise ValueError(f"Not a valid Reddit post URL: {raw}")

    return parsed + ".json?raw_json=1"


def fetch_json(url: str) -> dict:
    """Fetch JSON from Reddit with a browser-like user-agent."""
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def clean_text(text: str) -> str:
    """Unescape HTML entities and normalize whitespace."""
    if not text:
        return ""
    text = unescape(text)
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = text.strip()
    return text


def extract_post(data: dict) -> tuple[str, str, list]:
    """Return (title, selftext, comments) from the Reddit listing."""
    listing = data[0]["data"]["children"][0]["data"]
    title = clean_text(listing.get("title", ""))
    selftext = clean_text(listing.get("selftext", ""))
    comments = data[1]["data"]["children"] if len(data) > 1 else []
    return title, selftext, comments


def format_comment(comment: dict, depth: int = 0) -> str:
    """Recursively format a comment and its replies."""
    lines = []
    kind = comment.get("kind")
    data = comment.get("data", {})

    if kind != "t1":
        return ""

    author = data.get("author", "[deleted]")
    body = clean_text(data.get("body", ""))
    score = data.get("score", 0)

    if not body:
        return ""

    indent = "  " * depth
    lines.append(f"{indent}- **u/{author}** (+{score}):")
    for paragraph in body.split("\n\n"):
        for line in paragraph.split("\n"):
            lines.append(f"{indent}  {line}")
        lines.append("")

    replies = data.get("replies")
    if isinstance(replies, dict):
        for child in replies.get("data", {}).get("children", []):
            child_text = format_comment(child, depth + 1)
            if child_text:
                lines.append(child_text)

    return "\n".join(lines).rstrip()


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        return 1

    raw_input = sys.argv[1]

    try:
        if raw_input.endswith(".json") and not raw_input.startswith("http"):
            with open(raw_input, "r", encoding="utf-8") as fh:
                data = json.load(fh)
        else:
            url = normalize_url(raw_input)
            data = fetch_json(url)
    except urllib.error.HTTPError as exc:
        print(
            f"Error fetching Reddit ({exc.code}): {exc.reason}. "
            "Reddit may be blocking automated requests. Save the JSON from your browser "
            "(add /.json to the post URL) and run: python3 fetch_reddit.py ./thread.json",
            file=sys.stderr,
        )
        return 1
    except FileNotFoundError:
        print(f"File not found: {raw_input}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"Error fetching Reddit: {exc}", file=sys.stderr)
        return 1

    try:
        title, selftext, comments = extract_post(data)
    except (KeyError, IndexError, TypeError) as exc:
        print(f"Error parsing Reddit response: {exc}", file=sys.stderr)
        return 1

    print(f"# {title}\n")
    if selftext:
        print(selftext)
        print()

    if comments:
        print("## Comments\n")
        for comment in comments:
            text = format_comment(comment)
            if text:
                print(text)
                print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
