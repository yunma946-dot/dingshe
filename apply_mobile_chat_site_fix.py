#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import re
import shutil
import sys
import tempfile
from pathlib import Path


PATCH_DIR = Path(__file__).resolve().parent
VERSION = "20260926c"
CSS_START = "/* HQ_SERVER_CHAT_ONLY_CLEANUP_START */"
CSS_END = "/* HQ_SERVER_CHAT_ONLY_CLEANUP_END */"
JS_START = "/* HQ_SERVER_CHAT_ONLY_RUNTIME_CLEANUP_START */"
JS_END = "/* HQ_SERVER_CHAT_ONLY_RUNTIME_CLEANUP_END */"

CSS_BLOCK = f"""{CSS_START}
/* The live chat launcher and theme come only from chat.hqvip.xyz/widget.js. */
.floating-chat {{
  display: none !important;
  visibility: hidden !important;
  opacity: 0 !important;
  pointer-events: none !important;
}}
{CSS_END}"""

JS_BLOCK = f"""{JS_START}
(() => {{
  const cleanupLegacyWebsiteChat = () => {{
    document.querySelectorAll('.floating-chat').forEach((node) => {{
      node.hidden = true;
      node.style.setProperty('display', 'none', 'important');
      node.style.setProperty('pointer-events', 'none', 'important');
    }});

    const host = document.getElementById('hq-chat-widget-host');
    const legacyTheme = host && host.shadowRoot
      ? host.shadowRoot.getElementById('dingshe-chat-widget-theme')
      : null;
    if (legacyTheme) legacyTheme.remove();
  }};

  if (document.readyState === 'loading') {{
    document.addEventListener('DOMContentLoaded', cleanupLegacyWebsiteChat, {{ once: true }});
  }} else {{
    cleanupLegacyWebsiteChat();
  }}

  let attempts = 0;
  const timer = window.setInterval(() => {{
    cleanupLegacyWebsiteChat();
    attempts += 1;
    if (attempts >= 40) window.clearInterval(timer);
  }}, 250);
}})();
{JS_END}"""


def find_project_root() -> Path:
    candidates = [PATCH_DIR, PATCH_DIR.parent]
    for candidate in candidates:
        if (candidate / "assets" / "style.css").is_file() and (candidate / "assets" / "site.js").is_file():
            return candidate
    raise RuntimeError(
        "未找到项目根目录。请把 dingshe-mobile-chat-fix 文件夹放到 dingshe-site 根目录中。"
    )


def replace_marked_block(text: str, start: str, end: str, block: str) -> str:
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)
    if pattern.search(text):
        return pattern.sub(block, text, count=1)
    return text.rstrip() + "\n\n" + block + "\n"


def excluded(path: Path, root: Path) -> bool:
    try:
        parts = path.relative_to(root).parts
    except ValueError:
        return True
    return any(
        part in {".git", "node_modules", "__pycache__"}
        or part.startswith("chat-ui-backup-")
        for part in parts
    )


def update_versions(text: str) -> tuple[str, int]:
    replacements = 0
    patterns = [
        (
            re.compile(
                r"https://chat\.hqvip\.xyz/widget\.js\?site=site1(?:&|&amp;)v=[A-Za-z0-9._-]+"
            ),
            f"https://chat.hqvip.xyz/widget.js?site=site1&v={VERSION}",
        ),
        (
            re.compile(r"assets/site\.js\?v=[A-Za-z0-9._-]+"),
            f"assets/site.js?v={VERSION}",
        ),
        (
            re.compile(r"assets/style\.css\?v=[A-Za-z0-9._-]+"),
            f"assets/style.css?v={VERSION}",
        ),
    ]
    for pattern, replacement in patterns:
        def replace_match(match: re.Match[str]) -> str:
            nonlocal replacements
            if match.group(0) != replacement:
                replacements += 1
            return replacement

        text = pattern.sub(replace_match, text)
    return text, replacements


def write_if_changed(path: Path, text: str) -> bool:
    original = path.read_text(encoding="utf-8")
    if original == text:
        return False
    path.write_text(text, encoding="utf-8", newline="\n")
    return True


def main() -> int:
    try:
        root = find_project_root()
    except RuntimeError as exc:
        print(f"错误：{exc}")
        return 1

    timestamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    backup_root = Path(tempfile.gettempdir()) / f"dingshe-chat-ui-backup-{timestamp}"
    files_to_backup: list[Path] = []

    for relative in (
        Path("assets/style.css"),
        Path("assets/site.js"),
        Path("dist/assets/style.css"),
        Path("dist/assets/site.js"),
        Path("tools/build_site.py"),
    ):
        candidate = root / relative
        if candidate.is_file():
            files_to_backup.append(candidate)

    for html_path in root.rglob("*.html"):
        if not excluded(html_path, root):
            files_to_backup.append(html_path)

    unique_files = list(dict.fromkeys(files_to_backup))
    for source in unique_files:
        destination = backup_root / source.relative_to(root)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)

    changed: list[Path] = []

    for relative in (Path("assets/style.css"), Path("dist/assets/style.css")):
        path = root / relative
        if path.is_file():
            text = path.read_text(encoding="utf-8")
            text = replace_marked_block(text, CSS_START, CSS_END, CSS_BLOCK)
            if write_if_changed(path, text):
                changed.append(path)

    for relative in (Path("assets/site.js"), Path("dist/assets/site.js")):
        path = root / relative
        if path.is_file():
            text = path.read_text(encoding="utf-8")
            text = replace_marked_block(text, JS_START, JS_END, JS_BLOCK)
            if write_if_changed(path, text):
                changed.append(path)

    version_targets: list[Path] = []
    build_script = root / "tools" / "build_site.py"
    if build_script.is_file():
        version_targets.append(build_script)
    version_targets.extend(
        path for path in root.rglob("*.html") if not excluded(path, root)
    )

    version_replacements = 0
    for path in dict.fromkeys(version_targets):
        text = path.read_text(encoding="utf-8")
        updated, count = update_versions(text)
        version_replacements += count
        if write_if_changed(path, updated):
            changed.append(path)

    git_exclude = root / ".git" / "info" / "exclude"
    if git_exclude.is_file() and PATCH_DIR.parent == root:
        marker = "/dingshe-mobile-chat-fix/"
        current = git_exclude.read_text(encoding="utf-8", errors="replace")
        if marker not in current.splitlines():
            with git_exclude.open("a", encoding="utf-8", newline="\n") as handle:
                if current and not current.endswith("\n"):
                    handle.write("\n")
                handle.write(marker + "\n")

    main_css = (root / "assets" / "style.css").read_text(encoding="utf-8")
    main_js = (root / "assets" / "site.js").read_text(encoding="utf-8")
    if CSS_START not in main_css or JS_START not in main_js:
        print("错误：补丁写入后校验失败，未继续操作。")
        return 2

    print("网站端客服按钮修复完成。")
    print(f"修改文件数量：{len(dict.fromkeys(changed))}")
    print(f"客服与静态资源缓存版本替换数量：{version_replacements}")
    print(f"备份目录：{backup_root}")
    print("未运行一键更新网站；Excel、JSON、图片和视频均未修改。")
    print("下一步：安装服务器补丁，然后运行 上传到GitHub.bat。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
