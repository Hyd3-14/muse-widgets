# Firing fixtures

Sample requests and the routing the `figure-first` skill is expected to
produce for each. These fixtures pin the skill's firing behaviour so a
wording change in `SKILL.md` can be checked against them instead of
re-decided from memory.

How to use:

- **Structural check (automatic)**: run
  `python3 check_fixtures.py` in this directory. It verifies that every
  case is well-formed, that figure types come from the allowed set
  below, and that both firing and non-firing cases exist.
- **Behaviour check (manual)**: give each prompt to an agent with the
  skill installed, without showing it this file, and compare what it
  produces with the Expected and Figure type columns. Record the date
  and the result next to the case when a full run is done.

Allowed figure types: `timeline`, `comparison-grid`,
`conditional-comparison`, `structure`, `flow`, `progress-bar`, `chart`,
`card`, `before-after`. For text cases the Figure type is `none`.

| ID | Prompt | Expected | Figure type |
| --- | --- | --- | --- |
| F01 | このプロジェクトで起きたことを週ごとにまとめて | figure | timeline |
| F02 | この3つのノートPCを比べて。価格、重さ、バッテリーで | figure | comparison-grid |
| F03 | どのプランを選ぶべき？ どれくらい使うかによるんだよね | figure | conditional-comparison |
| F04 | デプロイのパイプラインがどう組み上がっているか説明して | figure | structure |
| F05 | ユーザーが購入ボタンを押した後に何が起きるか、順に教えて | figure | flow |
| F06 | 報告: 移行は5フェーズ中3つ完了、フェーズ4は月曜開始 | figure | progress-bar |
| F07 | 今月の支出がカテゴリごとにどう分かれているか見せて | figure | chart |
| F08 | 投票の最終結果を短い告知文で出して | figure | card |
| F09 | 料金ページの旧文案と新文案を並べて見せて。比べたい | figure | before-after |
| N01 | ノルウェーの首都は？ | text | none |
| N02 | この文は文法的に合ってる？「the data is stored」 | text | none |
| N03 | 仕事を辞めるかどうか迷ってる。壁打ち相手になって | text | none |
| N04 | このリデザイン、だいたいいくらくらいかかると思う？ データはまだ無いから勘でいいよ | text | none |
