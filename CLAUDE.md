# CLAUDE.md

Claude Codeは最初に[AGENTS.md](AGENTS.md)を読み、その規約に従ってください。

## Claude Codeの役割

- n8nワークフロー、GitHub Actions、記事ルールの実装と保守
- 障害時の原因調査と最小修正
- Codexでも引き継げる標準的なファイル形式の維持

Claude Codeのサブスクリプションは対話的な開発用です。n8nの無人実行ではAnthropic API Credentialを使用します。

## 変更手順

1. Issueまたは依頼内容を確認する。
2. 作業ブランチを作る。
3. 静的検証と可能な範囲のローカルテストを行う。
4. Pull Requestを作る。
5. 外部連携の実動確認結果と未確認項目を分けて報告する。
