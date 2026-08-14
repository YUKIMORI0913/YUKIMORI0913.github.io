import io
import json

from PIL import Image

import photo_admin


def image_bytes():
    stream = io.BytesIO()
    Image.new("RGB", (1200, 800), "#9b2c25").save(stream, "JPEG")
    stream.seek(0)
    return stream


def test_upload_edit_publish_and_delete(tmp_path, monkeypatch):
    monkeypatch.setattr(photo_admin, "DATA_FILE", tmp_path / "data" / "photos.json")
    monkeypatch.setattr(photo_admin, "ORIGINALS", tmp_path / "originals")
    monkeypatch.setattr(photo_admin, "THUMBNAILS", tmp_path / "thumbnails")
    client = photo_admin.app.test_client()

    response = client.post("/api/photos", data={"photos": (image_bytes(), "新しい写真.jpg")})
    assert response.status_code == 201
    photo = response.get_json()["created"][0]
    assert photo["width"] == 1200 and photo["height"] == 800
    assert (tmp_path / "thumbnails" / f'{photo["id"]}.webp').exists()

    response = client.patch(f'/api/photos/{photo["id"]}', json={"title": "ライブ", "is_published": False, "sort_order": 9})
    assert response.status_code == 200
    assert client.get("/api/public-photos").get_json()["photos"] == []

    assert client.delete(f'/api/photos/{photo["id"]}').status_code == 204
    assert json.loads((tmp_path / "data" / "photos.json").read_text())["photos"] == []


def test_rejects_non_image(tmp_path, monkeypatch):
    monkeypatch.setattr(photo_admin, "DATA_FILE", tmp_path / "photos.json")
    monkeypatch.setattr(photo_admin, "ORIGINALS", tmp_path / "originals")
    monkeypatch.setattr(photo_admin, "THUMBNAILS", tmp_path / "thumbnails")
    response = photo_admin.app.test_client().post("/api/photos", data={"photos": (io.BytesIO(b"no"), "memo.txt")})
    assert response.status_code == 400
