# mobius-tui

Native TUI monitor for [Mobius](https://github.com/tabtoyou/mobius) workflows, built with [SuperLightTUI](https://github.com/subinium/SuperLightTUI).

Reads the same `~/.mobius/mobius.db` as the Python TUI. Run it in a separate terminal while `mob run` or `mob evolve` executes.

## Install

```bash
# From source (requires Rust toolchain)
cd crates/mobius-tui
cargo install --path .

# Via mobius CLI
mobius tui monitor --backend slt
```

## Usage

```bash
mobius-tui                           # default DB path
mobius-tui --db-path /path/to/db     # custom DB
mobius-tui --mock                    # demo mode
mobius-tui --help                    # show all options
```

## Screens

| Key | Shortcut | Screen |
|-----|----------|--------|
| `1` | | Dashboard — Double Diamond phase bar, AC tree, node detail |
| `2` | | Execution — Phase outputs, event timeline |
| `3` | `l` | Logs — Sortable/filterable table |
| `4` | `d` | Debug — State dump, drift/cost sparklines, events |
| `5` | `e` | Lineage — Evolutionary generation history |
| | `s` | Session Selector |

## Keys

`q` quit · `p`/`r` pause/resume · `1-5` screens · `Ctrl+P` command palette · `↑↓` navigate · `Enter` select · mouse click
