# Auto AI Memo

Claude、n8n、Codex、GitHub、Slackを役割分担して、記事提案からnote投稿用パッケージまでを自動化するリポジトリです。

## 構成

```text
n8n（毎週月曜 9:00 JST）
  → Claude APIで記事提案を3件生成
  → GitHub Issueを作成
  → Slackへ採用ボタン付きで通知

Slackで「採用して記事化」
  → n8nがGitHub Issueへ /採用 を投稿
  → GitHub ActionsでCodexを実行
  → 記事草稿とGPT Image 2の見出し画像を生成
  → note用パッケージを生成
  → Pull Requestを作成
  → SlackへPRとダウンロードURLを通知
```

Claude Codeはリポジトリの開発・保守担当です。自動実行時のClaude呼び出しには、Claude Codeの契約とは別にAnthropic APIキーが必要です。

## 導入

1. [operations/setup-guide.md](operations/setup-guide.md)に従って初回認証とGitHub Secretsを設定する。
2. GitHub Actionsの`Deploy n8n workflows`を1回実行する。
3. 表示されたURLをSlack AppのInteractivity Request URLへ設定する。
4. 以後はSlackの採用ボタンだけで、記事・画像・note投稿用ZIP相当の成果物まで生成される。

## note公開について

noteには一般利用者向けの公式投稿APIがないため、本文と画像の生成・受け渡しまでを自動化し、最終公開だけはnote画面で行います。非公式APIやログインCookieは使用しません。

## 正本

GitHubを正本とし、`main`への直接変更は行いません。変更はブランチとPull Requestを経由します。
