# 鰻谷饅頭 Official Site

GitHub Pages で公開する静的サイトです。Photo Archive は `assets/data/photos.json` を索引として、一覧では軽量な WebP サムネイルだけを読み込みます。20枚単位のページネーション、lazy load、元画像のオンデマンド表示に対応しています。

## 写真を追加・編集する

初回だけ依存パッケージを入れ、ローカル管理画面を起動します。

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python photo_admin.py
```

ブラウザで `http://127.0.0.1:4173` を開きます。管理画面では次の操作ができます。

- JPG / JPEG / PNG / WebP をドラッグ＆ドロップで最大120枚まで一括追加
- タイトル、説明、代替テキスト、表示順の編集
- 公開・非公開の切り替え、削除
- 元画像の保存と720px以下のWebPサムネイル自動生成

変更後は通常どおり Git でコミット・push してください。追加時に処理されるのは新しい画像だけで、既存画像の再生成やAI解析は行いません。元画像は `assets/images/photos/originals/`、サムネイルは `assets/images/photos/thumbnails/` に保存されます。

公開サイトだけをローカル確認する場合は `python3 -m http.server 8080` を実行し、`http://localhost:8080/` を開きます。

公開前に `docs/CONTENT_REVIEW.md` の未確定事項を確認してください。
