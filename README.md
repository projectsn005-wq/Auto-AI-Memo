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
  → Obsidian向けMarkdown記憶と管理CSVを更新
  → Pull Requestを作成して自動マージ
  → main更新を契機にGoogle Sheetsへ管理台帳を自動同期
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

## AI外部記憶と管理台帳

採用された記事は、AIのチャット圧縮や文脈消失を補うために、GitHub内へ外部記憶として保存します。

- `memory/articles/issue-N.md`: Obsidianで開ける記事ごとのMarkdown記憶
- `admin/content-index.csv`: Google SheetsやExcelに読み込める管理台帳

台帳にはIssue、PR、Actions、記事Markdown、見出し画像、note投稿パッケージ、公開後のnote URLを集約します。`admin/content-index.csv`が`main`へ入るたびに、`Sync content ledger to Google Sheets`がGoogle Sheetsへ自動同期します。

note公開後はGitHub Actionsの`Register published note URL`を実行すると、公開URLを台帳と記憶へ追記するPRが作られ、自動マージされます。

## 正本

GitHubを正本とし、`main`への直接変更は行いません。変更はブランチとPull Requestを経由します。
