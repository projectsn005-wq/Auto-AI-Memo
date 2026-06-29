# コンテンツ管理台帳

`content-index.csv`は、GitHub Actionsが記事生成時に更新する管理用CSVです。

Google SheetsやExcelへ読み込むと、次のリンクを1行で追えます。

- GitHub Issue
- 草稿PR
- Actions実行
- 記事Markdown
- 見出し画像
- note投稿パッケージ
- note公開URL

note公開URLは公開後に手動で追記します。追記用スクリプトは次の通りです。

```bash
python scripts/register_note_url.py --issue-number 1 --note-url https://note.com/...
```
