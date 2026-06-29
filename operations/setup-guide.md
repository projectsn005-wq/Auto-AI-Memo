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
| `N8N_BASE_URL` | `https://snproject.app.n8n.cloud` |
| `N8N_API_TOKEN` | n8n Public APIキー |
| `N8N_ANTHROPIC_CREDENTIAL_ID` | n8nのAnthropic Credential ID |
| `N8N_GITHUB_CREDENTIAL_ID` | n8nのGitHub Credential ID |
| `N8N_SLACK_CREDENTIAL_ID` | n8nのSlack Credential ID |
| `SLACK_APPROVER_IDS` | 採用を許可するSlackユーザーID。複数はカンマ区切り |
| `SLACK_INTERACTION_SECRET` | 推測困難なランダム文字列 |

`GITHUB_TOKEN`はActionsが自動発行するため登録不要です。

## n8n Credentials

n8nのワークフローへ次を接続します。

| Credential | 必要値 |
| --- | --- |
| Anthropic API | Anthropic Consoleで発行したAPIキー |
| GitHub API | `Auto-AI-Memo`のIssuesを読み書きできるPAT |
| Slack API | Slack Bot Token |

## n8n初回認証

1. n8n左メニューの`Credentials`でAnthropic、GitHub、Slackをそれぞれ1回だけ登録する。Slack Appには`chat:write` Bot Token Scopeを付け、OAuthで接続する。
2. 各Credentialの編集画面URL末尾、またはエクスポート情報からCredential IDを確認する。
3. n8nの`Settings → n8n API`でAPIキーを作る。表示されない場合はインスタンス所有者とプランを確認する。
4. 上表の値をGitHub Secretsへ登録する。Secret値はIssueやチャットへ貼らない。
5. GitHubの`Actions → Deploy n8n workflows → Run workflow`を実行する。
6. Actionsログ末尾の`Slack Interactivity URL`をコピーする。
7. Slack API管理画面で対象Appを開き、`Interactivity & Shortcuts`をONにしてRequest URLへ設定する。
8. Botを通知先チャンネルへ招待する。

この初回設定後、ワークフローJSONの変更は`main`への反映時にn8nへ自動配備・有効化されます。

## GitHub側の確認

1. n8nの週次提案ワークフローを手動実行する。
2. Slackの`採用して記事化`ボタンを押す。
3. `Article Writer with Codex`が成功することを確認。
4. PRに記事、見出し画像、`note-package/issue-N`、`memory/articles/issue-N.md`、`admin/content-index.csv`が含まれることを確認する。
5. Actionsの成果物からnote投稿パッケージを取得する。

## n8nのプラン画面

自動配備ではn8n Public APIを使うため、`N8N_API_TOKEN`が必要です。すでに契約があるのにAPIメニューが見えない場合は、n8n Cloud管理画面の契約状態と、実際のインスタンス所有者アカウントが一致しているかを確認します。

## noteへの投稿

noteには一般利用者向けの公式投稿APIがありません。このリポジトリは次の3点を自動生成します。

- `title.txt`: noteタイトル欄へ貼る文字列
- `body.md`: note本文欄へ貼る原稿
- `cover.png`: noteの見出し画像

非公式API、Cookieの保存、ブラウザへのパスワード自動入力は行いません。最終公開は内容確認を兼ねてnote画面で実施します。

公開後のnote URLは、GitHub Actionsの`Register published note URL`を実行して登録します。

1. GitHubの`Actions → Register published note URL → Run workflow`を開く。
2. `issue_number`へ対象Issue番号、`note_url`へ公開済みnote URLを入力する。
3. 作成されたPRを確認してマージする。
4. `admin/content-index.csv`と`memory/articles/issue-N.md`からnoteへリンクできるようになります。

## Obsidian外部記憶

`memory/`フォルダはObsidianでそのままVaultとして開けます。AIに毎回すべてを覚えさせるのではなく、GitHub上のMarkdownを正本として保持し、次回以降の調査・改善・記事再利用時に参照します。

- `memory/articles/issue-N.md`: 記事ごとの判断、生成物、リンク、次アクション
- `admin/content-index.csv`: スプレッドシートで管理しやすい一覧

Google Sheetsへ直接同期したい場合は、別途Google Sheets APIまたはn8nのGoogle Sheets Credentialが必要です。まずは`admin/content-index.csv`をGoogle Sheetsへインポートすれば、追加APIなしで管理できます。
