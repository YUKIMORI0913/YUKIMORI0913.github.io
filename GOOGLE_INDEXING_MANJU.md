# 鰻谷饅頭 Googleインデックス・旧Wix削除運用

## 現在の公式サイト

- 公式URL: https://manju.unagitani.com/
- robots.txt: https://manju.unagitani.com/robots.txt
- sitemap.xml: https://manju.unagitani.com/sitemap.xml
- Photo Archive: https://manju.unagitani.com/gallery.html

2026年8月14日にGoogle Search ConsoleのURLプレフィックスプロパティ登録、HTMLタグによる所有権確認、サイトマップ送信、トップページとPhoto Archiveのインデックス登録リクエストを実施済みです。確認用metaタグは削除しないでください。

## 旧Wix検索結果

Google検索で確認された旧URLは次のとおりです。

- https://unagitanibass.wixsite.com/official
- https://unagitanibass.wixsite.com/official/live-1
- https://unagitanibass.wixsite.com/official/lesson

2026年8月14日時点で、上記URLはいずれもHTTP 404です。Wixで正しい301リダイレクトを設定できる場合は各旧URLから `https://manju.unagitani.com/` の対応内容へ301転送する方法を優先します。301が設定できない場合は、空の移転案内ページを200で復活させず、現在の404を維持します。

同日、現在のGoogleアカウントに旧WixのSearch Consoleプロパティが存在しないことを確認し、上記3 URLをGoogleの「古いコンテンツの更新」へ申請しました。現在のステータスは「保留」です。

## 旧WixをSearch Consoleで所有している場合

旧Wixプロパティを管理できるGoogleアカウントで次を実施します。

1. Search Consoleで旧Wixプロパティを選ぶ
2. 「削除」または「非表示」を開く
3. 「新しいリクエスト」を選ぶ
4. `https://unagitanibass.wixsite.com/official` を入力する
5. 「このURLのみを削除」または旧サイト全体が対象ならプレフィックス削除を選ぶ
6. リクエストを送信する
7. `/official/live-1` と `/official/lesson` も必要に応じて申請する

Search Consoleの削除は一時的な非表示処理です。恒久的な削除には旧URLの404/410継続、または新URLへの301が必要です。

## 旧Wixを所有していない場合

Googleの「古いコンテンツの更新」ツールを使用します。

1. https://search.google.com/search-console/remove-outdated-content を開く
2. 「新しいリクエスト」を選ぶ
3. Google検索に残っている旧Wix URLを正確に入力する
4. ページが存在しないことを確認する申請を送信する
5. 検索に残る各旧URLについて繰り返す

この申請は、現在の所有権を持たない第三者サイトの古い検索結果を更新するための手段です。Googleの再確認と処理には時間がかかります。

## 新公式サイト側の継続運用

コード側ではcanonical、Person・WebSite・MusicAlbum構造化データ、OGP、画像サイトマップ、通常HTMLリンクを設定済みです。次の変更後はSearch ConsoleのURL検査を利用します。

- トップページのプロフィールや作品情報を大きく更新したとき
- Photo Archiveの構造やURLを変更したとき
- 新しい独立ページを公開したとき

`python3 scripts/check_manju_seo.py` で本番のSEO状態と公開出力内のWix URL残存を確認できます。

## SNSプロフィール

Instagram、X、YouTube、Bandcamp等の本人管理プロフィールに旧Wix URLが残っている場合は、リンク先を `https://manju.unagitani.com/` に統一してください。外部プロフィールの変更は各サービスの本人アカウントで行います。

## 注意

Search Consoleへの登録や削除申請は、検索結果の即時変更や順位を保証しません。旧Wixの404継続、新公式サイトのクロール可能性、公式SNSからのリンク統一を保ちながら、Googleの再クロールとインデックス更新を待ちます。
