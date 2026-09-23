#!/usr/bin/env python3
"""写真グリッドを静的HTMLへ焼き込みます。

トップページの5枚と Photo Archive の1ページ目（20枚）は、これまで
`assets/data/photos.json` を読んだJavaScriptだけが組み立てていました。
検索エンジンが最初に取得するHTMLは空のままで、画像もalt属性も含まれません。

このスクリプトは同じ内容をHTMLへ書き出します。`main.js` と `archive.js` は
`replaceChildren()` で描画するため、ブラウザでは同じDOMに置き換わるだけで
二重表示にはなりません。

    python3 scripts/render_photos.py          # 書き込み
    python3 scripts/render_photos.py --check  # 差分検査のみ
"""

from __future__ import annotations

import json
import sys
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME_COUNT = 5
ARCHIVE_PER_PAGE = 20


def published_photos() -> list[dict]:
    data = json.loads((ROOT / "assets/data/photos.json").read_text(encoding="utf-8"))
    photos = [p for p in data["photos"] if p.get("is_published") is not False]
    return sorted(photos, key=lambda p: p["sort_order"], reverse=True)


def label(photo: dict) -> str:
    return photo.get("title") or f"ARCHIVE {str(photo['sort_order']).zfill(2)}"


def alt_text(photo: dict) -> str:
    return (
        photo.get("alt_text")
        or photo.get("title")
        or f"鰻谷饅頭 Photo Archive {str(photo['sort_order']).zfill(2)}"
    )


def figure(photo: dict, *, css_class: str, eager: bool) -> str:
    return (
        f'<figure class="{css_class}" tabindex="0">'
        f'<img src="{escape(photo["thumbnail_url"])}" alt="{escape(alt_text(photo))}" '
        f'width="{photo["width"]}" height="{photo["height"]}" '
        f'loading="{"eager" if eager else "lazy"}" decoding="async">'
        f"<figcaption>{escape(label(photo))}</figcaption></figure>"
    )


def replace_inner(html: str, opening: str, closing: str, inner: str, file: str) -> str:
    start = html.find(opening)
    if start == -1:
        raise SystemExit(f"[FAIL] {file} に {opening} がありません")
    body_start = start + len(opening)
    end = html.find(closing, body_start)
    if end == -1:
        raise SystemExit(f"[FAIL] {file} の {opening} を閉じられません")
    return html[:body_start] + inner + html[end:]


def render_home(photos: list[dict]) -> None:
    file = ROOT / "index.html"
    html = file.read_text(encoding="utf-8")
    inner = "".join(
        figure(
            photo,
            css_class="photo-slot photo-slot--large" if index == 0 else "photo-slot",
            eager=index == 0,
        )
        for index, photo in enumerate(photos[:HOME_COUNT])
    )
    write(file, replace_inner(html, '<div class="photo-grid" aria-label="写真アーカイブ">', "</div>", inner, "index.html"))


def render_archive(photos: list[dict]) -> None:
    file = ROOT / "gallery.html"
    html = file.read_text(encoding="utf-8")
    inner = "".join(figure(photo, css_class="photo-slot", eager=index < 3) for index, photo in enumerate(photos[:ARCHIVE_PER_PAGE]))
    html = replace_inner(html, '<div class="archive-grid" aria-label="写真アーカイブ">', "</div>", inner, "gallery.html")
    count = f"COLLECTION 01&nbsp;&nbsp;/&nbsp;&nbsp;{len(photos)} IMAGES"
    html = replace_inner(html, '<p class="archive-count" aria-live="polite">', "</p>", count, "gallery.html")
    write(file, html)


PENDING: dict[Path, str] = {}


def write(file: Path, html: str) -> None:
    PENDING[file] = html


def main() -> int:
    photos = published_photos()
    render_home(photos)
    render_archive(photos)

    check_only = "--check" in sys.argv
    drifted = []
    for file, html in PENDING.items():
        if file.read_text(encoding="utf-8") == html:
            continue
        if check_only:
            drifted.append(file.name)
        else:
            file.write_text(html, encoding="utf-8")
            print(f"[WRITE] {file.name}")

    if check_only:
        if drifted:
            print("[FAIL] 静的HTMLが photos.json と一致していません: " + ", ".join(drifted))
            print("       python3 scripts/render_photos.py を実行してください")
            return 1
        print("[PASS] 静的HTMLは photos.json と一致しています")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
