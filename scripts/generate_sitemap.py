#!/usr/bin/env python3
"""Generate the public sitemap, including discoverable Photo Archive images."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import quote
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://manju.unagitani.com"
SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
IMAGE_NS = "http://www.google.com/schemas/sitemap-image/1.1"

ET.register_namespace("", SITEMAP_NS)
ET.register_namespace("image", IMAGE_NS)


def absolute_url(path: str) -> str:
    return BASE_URL + quote(path, safe="/%:@-._~")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=ROOT / "assets/data/photos.json")
    args = parser.parse_args()
    payload = json.loads(args.data.read_text(encoding="utf-8"))
    photos = [photo for photo in payload.get("photos", []) if photo.get("is_published", True)]

    urlset = ET.Element(f"{{{SITEMAP_NS}}}urlset")
    home = ET.SubElement(urlset, f"{{{SITEMAP_NS}}}url")
    ET.SubElement(home, f"{{{SITEMAP_NS}}}loc").text = f"{BASE_URL}/"

    archive = ET.SubElement(urlset, f"{{{SITEMAP_NS}}}url")
    ET.SubElement(archive, f"{{{SITEMAP_NS}}}loc").text = f"{BASE_URL}/gallery.html"
    for photo in photos:
        image = ET.SubElement(archive, f"{{{IMAGE_NS}}}image")
        ET.SubElement(image, f"{{{IMAGE_NS}}}loc").text = absolute_url(photo["image_url"])
        caption = photo.get("alt_text") or photo.get("title") or f"鰻谷饅頭 Photo Archive {photo.get('sort_order', '')}"
        if caption:
            ET.SubElement(image, f"{{{IMAGE_NS}}}caption").text = caption

    tree = ET.ElementTree(urlset)
    ET.indent(tree, space="  ")
    tree.write(ROOT / "sitemap.xml", encoding="utf-8", xml_declaration=True)


if __name__ == "__main__":
    main()
