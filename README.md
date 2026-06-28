# Auto AI Memo

Claude、n8n、Codex、GitHub、Slackを役割分担して記事提案から草稿PRまでを自動化するリポジトリです。

## 構成

```text
n8n（毎週月曜 9:00 JST）
  → Claude APIで記事提案を3件生成
  → GitHub Issueを作成
  → Slackへ通知

GitHub Issueへ /採用
  → GitHub ActionsでCodexを実行
  → articles/へ草稿を生成
  → Pull Requestを作成
```

Claude Codeはリポジトリの開発・保守担当です。自動実行時のClaude呼び出しには、Claude Codeの契約とは別にAnthropic APIキーが必要です。

## 導入

1. [operations/setup-guide.md](operations/setup-guide.md)に従ってGitHub Secretsを設定する。
2. [operations/n8n/01-weekly-proposals.json](operations/n8n/01-weekly-proposals.json)をn8nへ手動インポートする。
3. n8n上でAnthropic、GitHub、SlackのCredentialsを接続する。
4. 手動実行でIssue 3件とSlack通知を確認する。
5. GitHub Issueへ `/採用` とコメントし、草稿PRが作られることを確認する。

## 正本

GitHubを正本とし、`main`への直接変更は行いません。変更はブランチとPull Requestを経由します。
