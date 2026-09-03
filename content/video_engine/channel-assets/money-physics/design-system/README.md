# Money Physics — Claude Design bundle

Preview cards for the Claude Design "Design System" pane. Each `*.html`
carries a first-line `<!-- @dsCard group="…" -->` marker; the pane builds
its card index from those. `tokens.json` mirrors `../brand-tokens.json`.
`assets/` holds the reference images the cards embed.

Source of truth is `../BRAND-SHEET.md` and the files it names; edit there,
then regenerate or hand-edit these cards.

## Push (one interactive step first)

1. Run `/design-login` once from an interactive Claude Code session on
   this machine.
2. Then, from any session, with the DesignSync tool:
   - `list_projects` → pick or `create_project` "Money Physics"
   - `finalize_plan` with `localDir` = this folder and writes
     `["*.html", "tokens.json", "assets/*"]`
   - `write_files` with `localPath` for each file
