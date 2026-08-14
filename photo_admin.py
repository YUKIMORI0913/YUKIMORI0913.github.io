#!/usr/bin/env python3
"""Local Photo Archive manager. Only new/changed photos are processed."""

from __future__ import annotations

import argparse
import json
import mimetypes
import re
import subprocess
import sys
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, abort, jsonify, request, send_from_directory
from PIL import Image, ImageOps, UnidentifiedImageError
from werkzeug.utils import secure_filename

ROOT = Path(__file__).resolve().parent
DATA_FILE = ROOT / "assets/data/photos.json"
ORIGINALS = ROOT / "assets/images/photos/originals"
THUMBNAILS = ROOT / "assets/images/photos/thumbnails"
ADMIN_DIR = ROOT / "admin"
ALLOWED = {".jpg", ".jpeg", ".png", ".webp"}
MAX_FILES = 120
MAX_FILE_BYTES = 35 * 1024 * 1024
LOCK = threading.RLock()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def read_photos() -> list[dict]:
    if not DATA_FILE.exists():
        return []
    with DATA_FILE.open(encoding="utf-8") as handle:
        return json.load(handle).get("photos", [])


def write_photos(photos: list[dict]) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    payload = {"version": 1, "updated_at": now_iso(), "photos": photos}
    temporary = DATA_FILE.with_suffix(".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(DATA_FILE)
    subprocess.run([sys.executable, str(ROOT / "scripts/generate_sitemap.py")], check=True)


def make_thumbnail(source: Path, destination: Path) -> tuple[int, int]:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as opened:
        image = ImageOps.exif_transpose(opened)
        width, height = image.size
        if image.mode not in ("RGB", "RGBA"):
            image = image.convert("RGB")
        image.thumbnail((720, 720), Image.Resampling.LANCZOS, reducing_gap=3.0)
        image.save(destination, "WEBP", quality=80, method=6)
    return width, height


def create_photo(upload) -> dict:
    original_name = Path(upload.filename or "").name
    extension = Path(original_name).suffix.lower()
    if extension not in ALLOWED:
        raise ValueError(f"未対応の形式です: {original_name}")
    upload.stream.seek(0, 2)
    size = upload.stream.tell()
    upload.stream.seek(0)
    if size > MAX_FILE_BYTES:
        raise ValueError(f"35MBを超えています: {original_name}")
    photo_id = uuid.uuid4().hex
    safe_stem = secure_filename(Path(original_name).stem)[:60] or "photo"
    stored_name = f"{photo_id}-{safe_stem}{extension}"
    original_path = ORIGINALS / stored_name
    thumb_name = f"{photo_id}.webp"
    thumbnail_path = THUMBNAILS / thumb_name
    ORIGINALS.mkdir(parents=True, exist_ok=True)
    upload.save(original_path)
    try:
        width, height = make_thumbnail(original_path, thumbnail_path)
    except (UnidentifiedImageError, OSError) as exc:
        original_path.unlink(missing_ok=True)
        raise ValueError(f"画像を読み込めません: {original_name}") from exc
    created = now_iso()
    return {
        "id": photo_id, "title": "", "description": "", "alt_text": "",
        "original_filename": original_name,
        "image_url": f"/assets/images/photos/originals/{stored_name}",
        "thumbnail_url": f"/assets/images/photos/thumbnails/{thumb_name}",
        "width": width, "height": height, "file_size": size,
        "mime_type": mimetypes.guess_type(original_name)[0] or "application/octet-stream",
        "sort_order": 0, "is_published": True, "created_at": created, "updated_at": created,
    }


def public_photo(photo: dict) -> dict:
    return {key: photo[key] for key in (
        "id", "title", "description", "alt_text", "original_filename", "image_url",
        "thumbnail_url", "width", "height", "sort_order", "created_at"
    ) if key in photo}


app = Flask(__name__, static_folder=None)
app.config["MAX_CONTENT_LENGTH"] = MAX_FILES * MAX_FILE_BYTES


@app.get("/")
def admin_page():
    return send_from_directory(ADMIN_DIR, "index.html")


@app.get("/admin/<path:name>")
def admin_asset(name):
    return send_from_directory(ADMIN_DIR, name)


@app.get("/assets/<path:name>")
def site_asset(name):
    return send_from_directory(ROOT / "assets", name)


@app.get("/api/photos")
def list_photos():
    with LOCK:
        photos = sorted(read_photos(), key=lambda item: (item.get("sort_order", 0), item["created_at"]), reverse=True)
    return jsonify({"photos": photos})


@app.post("/api/photos")
def upload_photos():
    uploads = request.files.getlist("photos")
    if not uploads or len(uploads) > MAX_FILES:
        return jsonify({"error": f"1回に1〜{MAX_FILES}枚を選択してください"}), 400
    created, errors = [], []
    with LOCK:
        photos = read_photos()
        next_order = max((item.get("sort_order", 0) for item in photos), default=0)
        for upload in uploads:
            try:
                photo = create_photo(upload)
                next_order += 1
                photo["sort_order"] = next_order
                photos.append(photo)
                created.append(photo)
            except ValueError as exc:
                errors.append(str(exc))
        if created:
            write_photos(photos)
    return jsonify({"created": created, "errors": errors}), 201 if created else 400


@app.patch("/api/photos/<photo_id>")
def update_photo(photo_id):
    allowed = {"title", "description", "alt_text", "sort_order", "is_published"}
    changes = request.get_json(silent=True) or {}
    if not set(changes) <= allowed:
        return jsonify({"error": "変更できない項目が含まれます"}), 400
    with LOCK:
        photos = read_photos()
        photo = next((item for item in photos if item["id"] == photo_id), None)
        if not photo:
            abort(404)
        for key, value in changes.items():
            if key == "sort_order": value = int(value)
            if key == "is_published": value = bool(value)
            photo[key] = value
        photo["updated_at"] = now_iso()
        write_photos(photos)
    return jsonify(photo)


@app.delete("/api/photos/<photo_id>")
def delete_photo(photo_id):
    with LOCK:
        photos = read_photos()
        photo = next((item for item in photos if item["id"] == photo_id), None)
        if not photo:
            abort(404)
        # Managed files are removed; legacy gallery originals are intentionally preserved.
        for key in ("image_url", "thumbnail_url"):
            path = ROOT / photo[key].lstrip("/")
            if path.is_relative_to(ORIGINALS) or path.is_relative_to(THUMBNAILS):
                path.unlink(missing_ok=True)
        write_photos([item for item in photos if item["id"] != photo_id])
    return ("", 204)


@app.get("/api/public-photos")
def public_photos():
    photos = [public_photo(item) for item in read_photos() if item.get("is_published", True)]
    photos.sort(key=lambda item: (item.get("sort_order", 0), item["created_at"]), reverse=True)
    return jsonify({"photos": photos})


def import_existing() -> None:
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    pattern = re.compile(r'<figure class="photo-slot[^>]*"><img src="([^"]+)" width="(\d+)" height="(\d+)" alt="([^"]*)"><figcaption>([^<]+)</figcaption>')
    existing = read_photos()
    known = {item["image_url"] for item in existing}
    added = 0
    for position, match in enumerate(pattern.finditer(html), 1):
        image_url, width, height, alt_text, caption = match.groups()
        if image_url in known:
            continue
        source = ROOT / image_url.lstrip("/")
        photo_id = f"legacy-{position:04d}"
        thumb = THUMBNAILS / f"{photo_id}.webp"
        make_thumbnail(source, thumb)
        created = datetime.fromtimestamp(source.stat().st_mtime, timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
        existing.append({
            "id": photo_id, "title": caption, "description": "", "alt_text": alt_text,
            "original_filename": source.name, "image_url": image_url,
            "thumbnail_url": f"/assets/images/photos/thumbnails/{thumb.name}",
            "width": int(width), "height": int(height), "file_size": source.stat().st_size,
            "mime_type": "image/jpeg", "sort_order": position, "is_published": True,
            "created_at": created, "updated_at": created,
        })
        added += 1
    write_photos(existing)
    print(f"Imported {added} existing photos ({len(existing)} total).")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--import-existing", action="store_true")
    parser.add_argument("--port", type=int, default=4173)
    args = parser.parse_args()
    if args.import_existing:
        import_existing()
    else:
        app.run(host="127.0.0.1", port=args.port, debug=False)
