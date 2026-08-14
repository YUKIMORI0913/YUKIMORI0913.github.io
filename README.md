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

## SEO・Google Search Console

公開URLは `https://manju.unagitani.com/` です。次のURLをブラウザから直接確認できます。

- https://manju.unagitani.com/robots.txt
- https://manju.unagitani.com/sitemap.xml

`sitemap.xml` にはトップページ、Photo Archive、および公開中のアーカイブ画像を登録します。管理画面で写真を保存するとサイトマップも自動生成されます。手動で再生成する場合は `python3 scripts/generate_sitemap.py` を実行します。両サイトの本番SEO監査は、コーポレートサイトのリポジトリで `python3 scripts/seo_check.py` を実行します。鰻谷饅頭サイト単独の詳細監査と公開出力内の旧Wix URL確認は、当リポジトリで `python3 scripts/check_manju_seo.py` を実行します。

Search Consoleの所有権確認でHTML verification fileを選んだ場合は、Googleからダウンロードした `googleXXXXXXXXXXXXXXXX.html` を内容・ファイル名を変えずこのリポジトリのルートへ配置し、デプロイ後に `https://manju.unagitani.com/googleXXXXXXXXXXXXXXXX.html` が200で取得できることを確認します。HTMLタグ方式の場合は、Google指定の `google-site-verification` metaタグをトップページの `<head>` に追加します。検証用トークンを架空値で公開しないでください。

2026年8月14日に、次のSearch Console作業を実施済みです。

1. Google Search Consoleへ `https://manju.unagitani.com/` のURLプレフィックスプロパティを追加
2. HTMLタグで所有権を確認
3. `https://manju.unagitani.com/sitemap.xml` を送信
4. `https://manju.unagitani.com/` のインデックス登録をリクエスト
5. `https://manju.unagitani.com/gallery.html` のインデックス登録をリクエスト

旧Wix検索結果の削除方法、確認済み旧URL、SNSリンク統一などの運用手順は [GOOGLE_INDEXING_MANJU.md](GOOGLE_INDEXING_MANJU.md) を参照してください。

サイトマップ送信や登録リクエストはインデックスを保証するものではありません。掲載可否と反映時期は検索エンジンが判断します。
