"""
platform_detect — Multi-platform path detection for AI agent skills.

Supports: Hermes (profile) / OpenClaw (workspace) / Claude Code / Codex / Cursor / VSCode

Usage:
    from platform_detect import detect, skill_dir, config_dir, state_file

    platform = detect()           # -> 'hermes', 'openclaw', 'claude_code', ...
    skill_dir('target-skill')    # -> Path('~/.claude/skills/target-skill')
    config_dir('my-skill')       # -> Path('~/.config/my-skill')
    state_file('.target-state.json')  # -> Path('~/.hermes/profiles/baijie/.target-state.json')
"""

import os
import platform as _platform_mod
from pathlib import Path
from typing import Literal, Optional

__version__ = "0.1.1"
__all__ = ["detect", "skill_dir", "config_dir", "state_file"]

# ─── 内部工具 ────────────────────────────────────────────────────────────────


def _cwd() -> Path:
    """安全获取当前工作目录，cwd 被删除时回退到 home"""
    try:
        return Path.cwd().resolve()
    except FileNotFoundError:
        return Path.home()


def _home() -> Path:
    """获取实际用户 home 目录，WSL Hermes profile 环境下返回 /home/<user>"""
    if _platform_mod.system() == "Linux" and os.path.exists("/proc/version"):
        with open("/proc/version") as f:
            if "WSL" in f.read():
                return Path(f"/home/{os.environ.get('USER', 'root')}")
    return Path.home()


def _ensure_dir(path: Path) -> Path:
    """确保目录存在，返回 path 本身"""
    path.mkdir(parents=True, exist_ok=True)
    return path


# ─── 平台检测 ────────────────────────────────────────────────────────────────


def detect() -> Literal["hermes", "openclaw", "claude_code", "codex", "cursor", "vscode", "unknown"]:
    """
    检测当前运行环境属于哪个平台。

    判断优先级：
    1. HERMES_PLATFORM 环境变量（显式设置）
    2. Hermes profile：Path.home() 包含 .hermes/profiles/
    3. OpenClaw：cwd 在 ~/.openclaw/workspace*/ 下
    4. Claude Code：~/.claude/ 目录存在
    5. Codex：~/.codex/ 目录存在
    6. Cursor：~/.cursor/ 目录存在
    7. VSCode：VSCODE_CLI... 环境变量
    8. unknown
    """
    # 显式环境变量
    env_platform = os.environ.get("HERMES_PLATFORM", "")
    if env_platform in ("hermes", "openclaw", "claude_code", "codex", "cursor", "vscode", "unknown"):
        return env_platform  # type: ignore[return-value]

    home = Path.home().resolve()
    home_str = str(home)

    # Hermes profile 环境
    if ".hermes" in home_str and "profiles" in home_str:
        return "hermes"

    # OpenClaw workspace 环境
    openclaw_base = home / ".openclaw"
    if openclaw_base.exists():
        cwd = _cwd()
        for parent in [cwd] + list(cwd.parents):
            if str(parent).startswith(str(openclaw_base / "workspace")):
                return "openclaw"

    # Claude Code
    if (home / ".claude").exists():
        return "claude_code"

    # Codex
    if (home / ".codex").exists():
        return "codex"

    # Cursor
    if (home / ".cursor").exists():
        return "cursor"

    # VSCode
    if os.environ.get("VSCODE_CLI"):
        return "vscode"

    return "unknown"


def _detect_hermes_profile() -> str:
    """检测 Hermes profile 名称，返回如 'baijie'"""
    home = Path.home().resolve()
    for parent in [home] + list(home.parents):
        parts = parent.parts
        for i, part in enumerate(parts):
            if part == "profiles" and i + 2 < len(parts):
                name = parts[i + 1]
                if parts[i + 2] == "home":
                    return name
    return "default"


def _detect_openclaw_workspace() -> str:
    """检测 OpenClaw workspace 名称，返回如 'workspace'、'workspace-bailong'"""
    home = Path.home().resolve()
    openclaw_base = home / ".openclaw"
    if not openclaw_base.exists():
        return "workspace"

    cwd = _cwd()
    for parent in [cwd] + list(cwd.parents):
        parent_str = str(parent)
        if parent_str.startswith(str(openclaw_base / "workspace")):
            parts = parent.parts
            for part in reversed(parts):
                if part == "workspace" or part.startswith("workspace-"):
                    return part
            return "workspace"
    return "workspace"


# ─── 标准路径 API ────────────────────────────────────────────────────────────


def skill_dir(skill_name: str) -> Path:
    """
    返回指定 skill 的安装目录（平台相关）。

    - Hermes:  ~/.hermes/skills/<skill>/
    - OpenClaw: ~/.openclaw/<workspace>/skills/<skill>/
    - Claude Code: ~/.claude/skills/<skill>/
    - Codex:     ~/.codex/skills/<skill>/
    - Cursor:    ~/.cursor/plugins/<skill>/
    - VSCode:    ~/.vscode/extensions/<skill>/
    """
    home = _home()
    p = detect()

    if p == "hermes":
        return _ensure_dir(home / ".hermes" / "skills" / skill_name)
    elif p == "openclaw":
        ws = _detect_openclaw_workspace()
        return _ensure_dir(home / ".openclaw" / ws / "skills" / skill_name)
    elif p == "claude_code":
        return _ensure_dir(home / ".claude" / "skills" / skill_name)
    elif p == "codex":
        return _ensure_dir(home / ".codex" / "skills" / skill_name)
    elif p == "cursor":
        return _ensure_dir(home / ".cursor" / "plugins" / skill_name)
    elif p == "vscode":
        return _ensure_dir(home / ".vscode" / "extensions" / skill_name)
    else:
        # unknown：回退到 Hermes
        return _ensure_dir(home / ".hermes" / "skills" / skill_name)


def config_dir(skill_name: Optional[str] = None) -> Path:
    """
    返回 skill 的配置目录（平台相关，profile/workspace 隔离）。

    - Hermes:  ~/.hermes/profiles/<profile>/.<skill>/
    - OpenClaw: ~/.openclaw/<workspace>/.<skill>/
    - Claude Code: ~/.claude/.config/<skill>/
    - Codex:     ~/.codex/.config/<skill>/
    - Cursor:    ~/.cursor/.config/<skill>/
    - VSCode:    ~/.vscode/.config/<skill>/

    如果 skill_name 为 None，返回平台配置根目录。
    """
    home = _home()
    p = detect()

    if p == "hermes":
        profile = _detect_hermes_profile()
        root = home / ".hermes" / "profiles" / profile
    elif p == "openclaw":
        ws = _detect_openclaw_workspace()
        root = home / ".openclaw" / ws
    elif p == "claude_code":
        root = home / ".claude"
    elif p == "codex":
        root = home / ".codex"
    elif p == "cursor":
        root = home / ".cursor"
    elif p == "vscode":
        root = home / ".vscode"
    else:
        root = home / ".hermes"

    if skill_name:
        return _ensure_dir(root / f".{skill_name}")
    return _ensure_dir(root)


def state_file(filename: str) -> Path:
    """
    返回 skill 状态文件路径（平台相关，profile/workspace 隔离）。

    文件永远存放在平台配置目录下，与 skill 安装目录分离。

    - Hermes:  ~/.hermes/profiles/<profile>/<filename>
    - OpenClaw: ~/.openclaw/<workspace>/<filename>
    - 其他：   ~/.hermes/profiles/default/<filename>
    """
    return config_dir() / filename
