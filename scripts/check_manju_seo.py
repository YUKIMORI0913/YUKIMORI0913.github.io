#!/usr/bin/env python3
"""Audit the production Manju site and detect legacy Wix references."""

from __future__ import annotations

import json
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://manju.unagitani.com/"
EXPECTED_CANONICAL = BASE_URL
LEGACY_MARKERS = ("wix.com", "wixsite.com", "unagitanibass")
USER_AGENT = "UNAGITANI-Manju-SEO-Audit/1.0"


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title = ""
        self.h1: list[str] = []
        self.meta: list[dict[str, str]] = []
        self.links: list[dict[str, str]] = []
        self.json_ld: list[str] = []
        self._capture: str | None = None
        self._text: list[str] = []
        self._script_type = ""

    def handle_starttag(self, tag: str, attrs) -> None:
        values = dict(attrs)
        if tag in {"title", "h1"}:
            self._capture, self._text = tag, []
        elif tag == "meta":
            self.meta.append(values)
        elif tag == "link":
            self.links.append(values)
        elif tag == "script":
            self._capture, self._text = "script", []
            self._script_type = values.get("type", "").lower()

    def handle_data(self, data: str) -> None:
        if self._capture:
            self._text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag != self._capture:
            return
        value = " ".join("".join(self._text).split())
        if tag == "title":
            self.title = value
        elif tag == "h1":
            self.h1.append(value)
        elif tag == "script" and self._script_type == "application/ld+json":
            self.json_ld.append(value)
        self._capture, self._text = None, []


def fetch(url: str) -> tuple[int, dict[str, str], bytes]:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=20) as response:
        return response.status, dict(response.headers.items()), response.read()


def meta_value(page: PageParser, key: str) -> str:
    for item in page.meta:
        item_key = (item.get("name") or item.get("property") or "").lower()
        if item_key == key.lower():
            return item.get("content", "").strip()
    return ""


def canonical(page: PageParser) -> str:
    for item in page.links:
        if "canonical" in item.get("rel", "").lower().split():
            return item.get("href", "")
    return ""


def schema_types(payload) -> set[str]:
    nodes = payload.get("@graph", []) if isinstance(payload, dict) else []
    if isinstance(payload, dict) and payload.get("@type"):
        nodes = [payload, *nodes]
    result: set[str] = set()
    for node in nodes:
        value = node.get("@type") if isinstance(node, dict) else None
        result.update(value if isinstance(value, list) else [value] if value else [])
    return result


def report(ok: bool, label: str, detail: str = "") -> int:
    print(f"[{'PASS' if ok else 'FAIL'}] {label}" + (f": {detail}" if detail else ""))
    return 0 if ok else 1


def public_wix_references() -> list[str]:
    candidates = [ROOT / "index.html", ROOT / "gallery.html", ROOT / "robots.txt", ROOT / "sitemap.xml"]
    candidates.extend((ROOT / "assets/js").glob("*.js"))
    matches = []
    for path in candidates:
        text = path.read_text(encoding="utf-8", errors="replace").lower()
        if any(marker in text for marker in LEGACY_MARKERS):
            matches.append(str(path.relative_to(ROOT)))
    return matches


def main() -> int:
    failures = 0
    try:
        status, headers, body = fetch(BASE_URL)
        robots_status, _, robots_body = fetch(BASE_URL + "robots.txt")
        sitemap_status, _, sitemap_body = fetch(BASE_URL + "sitemap.xml")
    except (HTTPError, URLError, TimeoutError) as exc:
        return report(False, "production fetch", str(exc))

    page = PageParser()
    page.feed(body.decode("utf-8", errors="replace"))
    schemas = []
    valid_json_ld = True
    for raw in page.json_ld:
        try:
            schemas.append(json.loads(raw))
        except json.JSONDecodeError:
            valid_json_ld = False
    types = set().union(*(schema_types(item) for item in schemas)) if schemas else set()
    robots = robots_body.decode("utf-8", errors="replace")
    try:
        ET.fromstring(sitemap_body)
        valid_sitemap = True
    except ET.ParseError:
        valid_sitemap = False
    robots_meta = meta_value(page, "robots").lower()
    x_robots = headers.get("X-Robots-Tag", "").lower()

    checks = [
        (status == 200, "homepage HTTP 200", str(status)),
        (robots_status == 200 and "Allow: /" in robots and BASE_URL + "sitemap.xml" in robots, "robots.txt", str(robots_status)),
        (sitemap_status == 200 and valid_sitemap, "sitemap.xml", str(sitemap_status)),
        (canonical(page) == EXPECTED_CANONICAL, "canonical", canonical(page)),
        (page.title.startswith("鰻谷饅頭"), "title", page.title),
        (bool(meta_value(page, "description")), "meta description", meta_value(page, "description")),
        (any("鰻谷" in value and "饅頭" in value for value in page.h1), "H1", " | ".join(page.h1)),
        ("noindex" not in robots_meta and "noindex" not in x_robots, "no noindex"),
        (valid_json_ld and bool(schemas), "valid JSON-LD"),
        ("Person" in types, "Person schema"),
        ("WebSite" in types, "WebSite schema"),
        (all(meta_value(page, key) for key in ("og:title", "og:description", "og:url", "og:image", "og:type", "twitter:card")), "OGP/Twitter metadata"),
        (not public_wix_references(), "no Wix reference in public output", ", ".join(public_wix_references())),
    ]
    for ok, label, *detail in checks:
        failures += report(ok, label, detail[0] if detail else "")
    print(f"Result: {'PASS' if failures == 0 else f'{failures} failure(s)'}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
