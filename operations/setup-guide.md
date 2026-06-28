# セットアップガイド

## 重要な区別

- Claude Code契約: 人がターミナルでClaude Codeを使うための契約。
- Anthropic API: n8nが無人でClaudeを呼ぶための従量課金API。Claude Code契約とは別。
- OpenAI API: GitHub ActionsのCodex Actionが記事を書くために使用。
- n8n Public API: GitHubからn8nを自動管理するためのAPI。手動インポートでは不要。

## GitHub Secrets

`Settings → Secrets and variables → Actions`へ登録します。

| Secret | 用途 |
| --- | --- |
| `OPENAI_API_KEY` | Codex Action |
| `SLACK_BOT_TOKEN` | 草稿PRのSlack通知（任意） |
| `SLACK_CHANNEL_ID` | 通知先チャンネルID（任意） |

`GITHUB_TOKEN`はActionsが自動発行するため登録不要です。

## n8n Credentials

n8nのワークフローへ次を接続します。

| Credential | 必要値 |
| --- | --- |
| Anthropic API | Anthropic Consoleで発行したAPIキー |
| GitHub API | `Auto-AI-Memo`のIssuesを読み書きできるPAT |
| Slack API | Slack Bot Token |

## n8n手動インポート

1. n8nで新規ワークフローを作る。
2. 右上の三点メニューから`Import from File`。
3. `operations/n8n/01-weekly-proposals.json`を選ぶ。
4. `Claudeで記事提案`へAnthropic Credentialを接続。
5. `GitHub Issue作成`へGitHub Credentialを接続。
6. `Slackへ通知`へSlack Credentialを接続。
7. `Slack通知を組み立て`ノード内の`SET_SLACK_CHANNEL_ID`を実際のチャンネルIDへ変更。
8. 保存して手動実行する。
9. Issueが3件作られ、Slackへ3件通知されたことを確認してからActiveにする。

## GitHub側の確認

1. GitHubに`提案`ラベルを作成。
2. 提案Issueへ`/採用`とコメント。
3. `Article Writer with Codex`が成功することを確認。
4. `articles/issue-N-draft.md`を含むPRが作成されることを確認。

## n8nのプラン画面

手動インポートではn8n Public APIを使わないため、`N8N_API_TOKEN`は不要です。すでにトライアル後の契約があるのにAPIメニューが見えない場合は、n8n Cloud管理画面の契約状態と、実際のインスタンス所有者アカウントが一致しているかを確認します。
