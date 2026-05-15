# platform-detect

> Multi-platform path detection for AI agent skills.

**Supports**: Hermes (profile) / OpenClaw (workspace) / Claude Code / Codex / Cursor / VSCode

## Install

```bash
pip install platform-detect
```

## Usage

```python
from platform_detect import detect, skill_dir, config_dir, state_file

# Detect current platform
platform = detect()  # -> 'hermes' | 'openclaw' | 'claude_code' | 'codex' | 'cursor' | 'vscode' | 'unknown'

# Skill installation directory
skill_dir('target-skill')  # -> ~/.hermes/skills/target-skill (Hermes)

# Skill config/state directory (profile/workspace isolated)
config_dir('my-skill')  # -> ~/.hermes/profiles/baijie/.my-skill

# State file path
state_file('.my-state.json')  # -> ~/.hermes/profiles/baijie/.my-state.json
```

## Platform paths

| Platform | Skill Dir | Config Dir |
|----------|-----------|------------|
| Hermes | `~/.hermes/skills/<name>/` | `~/.hermes/profiles/<profile>/.<name>/` |
| OpenClaw | `~/.openclaw/<workspace>/skills/<name>/` | `~/.openclaw/<workspace>/.<name>/` |
| Claude Code | `~/.claude/skills/<name>/` | `~/.claude/.config/<name>/` |
| Codex | `~/.codex/skills/<name>/` | `~/.codex/.config/<name>/` |
| Cursor | `~/.cursor/plugins/<name>/` | `~/.cursor/.config/<name>/` |
| VSCode | `~/.vscode/extensions/<name>/` | `~/.vscode/.config/<name>/` |

## Zero dependencies

Only uses Python standard library (`pathlib`, `os`, `platform`).

## License

MIT
