# コンテンツ管理台帳

`content-index.csv`は、GitHub Actionsが記事生成時に更新する管理用CSVです。`main`へ反映されると、`Sync content ledger to Google Sheets`がGoogle Sheetsへ自動同期します。

Google Sheetsでは、次のリンクを1行で追えます。

- GitHub Issue
- 草稿PR
- Actions実行
- 記事Markdown
- 見出し画像
- note投稿パッケージ
- note公開URL

note公開URLは公開後に`Register published note URL` workflowで登録します。ローカルで追記する場合のスクリプトは次の通りです。

```bash
python scripts/register_note_url.py --issue-number 1 --note-url https://note.com/...
```
