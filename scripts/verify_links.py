#!/usr/bin/env python3
"""Verify every URL in categories/*.md by issuing HEAD requests.

Outputs a markdown table summarizing failures (4xx / 5xx / timeouts / DNS).
Always exits 0 — this is a reporter, not a gate.

Usage:
    python scripts/verify_links.py
"""

from __future__ import annotations

import os
import re
import sys
from collections import OrderedDict
from datetime import date, datetime

try:
    import requests
    from requests.exceptions import RequestException
except ImportError:  # pragma: no cover - graceful degradation
    print("ERROR: `requests` not installed. Run: pip install -r requirements.txt", file=sys.stderr)
    sys.exit(0)


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATEGORIES_DIR = os.path.join(REPO_ROOT, "categories")

URL_RE = re.compile(r"https?://[^\s)<>\]\"']+")
ENTRY_HEADER_RE = re.compile(r"^###\s+(.+?)\s*$", re.MULTILINE)
TIMEOUT_SECONDS = 12
USER_AGENT = (
    "Mozilla/5.0 (compatible; radiology-opportunities-link-verifier/1.0; "
    "+https://github.com/shawnktl/radiology-opportunities)"
)


def collect_urls():
    """Return ordered dict: url -> list of (category_file, entry_name)."""
    found: "OrderedDict[str, list[tuple[str, str]]]" = OrderedDict()
    if not os.path.isdir(CATEGORIES_DIR):
        return found
    for fname in sorted(os.listdir(CATEGORIES_DIR)):
        if not fname.endswith(".md"):
            continue
        path = os.path.join(CATEGORIES_DIR, fname)
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        # Walk by entry: split on horizontal rules
        chunks = re.split(r"\n---\n", text)
        for chunk in chunks[1:]:
            name_match = ENTRY_HEADER_RE.search(chunk)
            entry_name = name_match.group(1).strip() if name_match else "(unknown)"
            for url_match in URL_RE.finditer(chunk):
                url = url_match.group(0).rstrip(".,;:)")
                found.setdefault(url, []).append((fname, entry_name))
    return found


def check_url(url: str):
    """Return (status_code_or_none, error_message_or_none)."""
    headers = {"User-Agent": USER_AGENT, "Accept": "*/*"}
    try:
        resp = requests.head(
            url,
            allow_redirects=True,
            timeout=TIMEOUT_SECONDS,
            headers=headers,
        )
        if resp.status_code >= 400:
            # Some servers reject HEAD; retry GET.
            resp = requests.get(
                url,
                allow_redirects=True,
                timeout=TIMEOUT_SECONDS,
                headers=headers,
                stream=True,
            )
            resp.close()
        return resp.status_code, None
    except RequestException as exc:
        return None, str(exc)


def main():
    urls = collect_urls()
    today = date.today().isoformat()
    print(f"# Link Verification Report — {today}")
    print()
    print(f"Checked {len(urls)} unique URLs across categories/*.md.")
    print()

    failures = []
    for url, refs in urls.items():
        status, err = check_url(url)
        ok = status is not None and status < 400
        marker = "OK" if ok else "FAIL"
        # Compact stdout log so progress is visible during long runs.
        sys.stderr.write(f"[{marker}] {status if status else 'ERR'}  {url}\n")
        if not ok:
            failures.append({
                "url": url,
                "status": status,
                "error": err,
                "refs": refs,
            })

    if not failures:
        print("All links resolved with HTTP < 400. No action needed.")
        return 0

    print(f"## {len(failures)} broken or unreachable link(s)")
    print()
    print("| Status | URL | Found in | Entry |")
    print("|--------|-----|----------|-------|")
    for f in failures:
        status_label = str(f["status"]) if f["status"] is not None else (
            f"err: {f['error'][:60]}" if f["error"] else "err"
        )
        for category_file, entry_name in f["refs"]:
            url = f["url"]
            short_url = url if len(url) <= 80 else url[:77] + "..."
            print(
                f"| {status_label} | <{short_url}> | "
                f"`categories/{category_file}` | {entry_name} |"
            )
    return 0


if __name__ == "__main__":
    sys.exit(main())
