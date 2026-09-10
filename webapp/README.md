# 広報取り込みアプリ

陸前高田市広報の取り込み・受給者名簿との照合・見出し案内・高田町8区のごみ収集日/分別早見表をまとめた、単体で動くWebアプリ。

**`koho-app.html` を開けば、そのまま(ネット接続なしで)動きます。** ブラウザ内の保存(localStorage)にのみデータが残り、外部には一切送信されません。

## 構成

```
webapp/
  src/template.html      アプリ本体のテンプレート(プレースホルダー入り)
  seed/                  アプリに埋め込む初期データ
    bunbetsu/*.json       ごみの分別区分(10区分)
    gomi-items.json        分別早見表の検索用品目インデックス
    koho-issues.json       取り込み済みの広報号の記録
    headlines.json         各号の見出し案内
    gomi-schedule.json     高田町8区のごみ収集日(月ごと)
  vendor/pdfjs/           PDF読み取り用に同梱している pdf.js 一式(vendor、変更しない)
  build.py                上記を組み合わせて koho-app.html を生成するビルドスクリプト
  koho-app.html           配布用の完成ファイル(build.py の出力。手で編集しない)
```

## ビルド方法

```
cd webapp
python3 build.py
```

外部ネットワークへのアクセスは不要。`koho-app.html` が生成される。

`src/template.html` や `seed/*` を直したら、必ず `python3 build.py` を実行してから `koho-app.html` をコミットすること(koho-app.html は生成物なので、テンプレートやseedと食い違わないようにする)。

## データの更新

- **新しい号の見出し・ごみ収集日を追加したい場合**: `seed/koho-issues.json` `seed/headlines.json` `seed/gomi-schedule.json` に項目を足して再ビルドする。既存のエントリの書き方をそのまま真似れば形式は揃う。
- **分別区分・品目を増やしたい場合**: `seed/bunbetsu/*.json`(区分カード)と `seed/gomi-items.json`(検索用の品目)を編集する。出典は市ホームページ「家庭ごみ・資源」(まちづくり推進課生活環境係)。
- **受給者名簿・照合記録**: アプリの中でユーザーが登録するデータなので、このリポジトリには含まれない(ブラウザのlocalStorageにのみ保存される)。

## pdf.js について

`vendor/pdfjs/` には以下の3ファイルを同梱している(npm の `pdfjs-dist@3.11.174` から取得したもの):

- `pdf.min.js` / `pdf.worker.min.js` — pdf.js 本体
- `Adobe-Japan1-UCS2.bcmap` — 日本語文字の字形表(これが無いと日本語が正しく読み取れない)

アプリ内でPDFを読み取る機能(号の自動判別・慶弔欄との照合・見出し候補の抽出)は、すべて端末内(ブラウザ)で完結する。PDFのファイルも中身も外部には送信されない。

pdf.js を更新する場合は `npm install pdfjs-dist@<version>` した上で、上記3ファイルを `vendor/pdfjs/` に上書きし、再ビルドして動作確認すること。

## 制約・注意点

- ごみ収集日の表は紙面のレイアウトが崩れやすく、自動取り込みでは誤読のリスクが高いため、`seed/gomi-schedule.json` は手動での更新を前提にしている(PDFからの自動取り込みは見出し・慶弔欄照合のみ)。
- 生年月日は和暦(`H12.3.7` `平成12年3月7日` 等)・西暦のどちらのCSVにも対応。Excel保存のShift_JIS CSVにも対応している。
