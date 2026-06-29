# AGENTS.md

この文書はClaude Code、Codex、その他のAIエージェント共通の運用規約です。

## 原則

- GitHubを正本とする。
- `main`へ直接コミットしない。
- Slack承認後の生成物PRとnote URL登録PRは、GitHub Actionsが自動マージしてよい。
- Secret、APIキー、Webhook秘密値をコード・Issue・ログへ出さない。
- AIプロバイダー固有処理は境界を明確にし、交換可能に保つ。
- 未確認の外部動作を「動作確認済み」と報告しない。
- n8nの本番Slack投稿を伴うE2Eテストは最後に1回だけ行う。

## 役割分担

| コンポーネント | 役割 |
| --- | --- |
| Claude Code | 対話的な開発、保守、調査 |
| Claude API | n8nからの記事提案生成 |
| n8n | スケジュール、外部サービス連携、通知 |
| Codex Action | 採用後の記事草稿作成 |
| GitHub | Issue承認、PRレビュー、記事保管 |
| Slack | 提案通知、採用操作、運用状況の共有 |
| OpenAI Image API | note見出し画像の生成 |
| Obsidian互換Markdown | AI外部記憶、判断履歴、生成物リンクの保管 |
| 管理CSV / Google Sheets | 記事No、状態、Issue/PR/noteリンクの一覧管理 |

## 記事

- 記事は`articles/`へMarkdownで保存する。
- 見出し画像は`articles/assets/`、noteへ渡す成果物は`note-package/`へ保存する。
- AI外部記憶は`memory/articles/`、管理台帳は`admin/content-index.csv`へ保存する。
- frontmatterには`id`、`title`、`category`、`version`、`review_status`、`public`、`post_to`を含める。
- 捏造した体験談・実績・出典を入れない。
- 結論を先に置き、抽象と具体を往復する。
