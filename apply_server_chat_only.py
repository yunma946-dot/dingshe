from __future__ import annotations

import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SITE_JS = ROOT / "assets" / "site.js"
BUILDER = ROOT / "tools" / "build_site.py"
CHECKER = ROOT / "tools" / "check_site.py"

TARGET_URL = "https://chat.hqvip.xyz/widget.js?site=site1&v=20260924b"
TARGET_TAG = f'<script src="{TARGET_URL}"></script>'
SITE_JS_CACHE = "20260924-chat2"

MINIMAL_CHAT_BUTTONS = """
  document.querySelectorAll('[data-chat-open]').forEach(function (button) {
    button.addEventListener('click', function () {
      if (window.HQChatWidget && typeof window.HQChatWidget.toggle === 'function') {
        window.HQChatWidget.toggle();
      } else {
        window.dispatchEvent(new CustomEvent('hq-chat-open'));
      }
    });
  });"""


def read_source(path: Path) -> tuple[str, str]:
    raw = path.read_bytes()
    newline = "\r\n" if b"\r\n" in raw else "\n"
    return raw.decode("utf-8").replace("\r\n", "\n"), newline


def write_source(path: Path, text: str, newline: str) -> None:
    path.write_bytes(text.replace("\n", newline).encode("utf-8"))


def stop(message: str) -> None:
    raise RuntimeError(message)


def update_site_js(text: str) -> str:
    if "applyDingsheChatTheme" not in text and "chatScriptUrl" not in text:
        if "window.HQChatWidget.toggle()" in text:
            return text
        stop("没有找到网站端客服代码，未修改任何文件。")

    pattern = re.compile(
        r"\n  let nativeChatLauncher = null;.*?"
        r"\n  window\.addEventListener\('load', function \(\) \{.*?"
        r"\n  \}, \{ once: true \}\);",
        re.DOTALL,
    )
    new_text, count = pattern.subn("\n" + MINIMAL_CHAT_BUTTONS, text, count=1)
    if count != 1:
        stop("网站端客服代码结构与预期不同，未修改任何文件。")
    return new_text


def update_builder(text: str) -> str:
    # Remove the website's custom floating launcher. The server widget supplies it.
    text = re.sub(
        r"\n<button class=\"floating-chat\"[^>]*>.*?</button>\n",
        "\n",
        text,
        count=1,
        flags=re.DOTALL,
    )

    # Remove every old direct widget tag, then insert one canonical tag.
    text = re.sub(
        r"[ \t]*<script\b(?=[^>]*\bsrc=['\"]https://chat\.hqvip\.xyz/widget\.js\?[^'\"]+['\"])[^>]*>\s*</script>\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )
    site_script_pattern = r'(<script src="\{prefix\}assets/site\.js\?v=[^\"]+" defer></script>)'
    if not re.search(site_script_pattern, text):
        stop("没有找到网站公共脚本位置，未修改任何文件。")
    text = re.sub(site_script_pattern, TARGET_TAG + "\n" + r"\1", text, count=1)

    text, count = re.subn(
        r"assets/site\.js\?v=[^\"']+",
        f"assets/site.js?v={SITE_JS_CACHE}",
        text,
        count=1,
    )
    if count != 1:
        stop("没有找到网站脚本缓存版本，未修改任何文件。")
    return text


def verify() -> None:
    dist = ROOT / "dist"
    built_js = dist / "assets" / "site.js"
    if not built_js.exists():
        stop("检查失败：dist/assets/site.js 不存在。")

    forbidden = (
        "applyDingsheChatTheme",
        "dingshe-chat-widget-theme",
        "chatScriptUrl",
        "ensureChatLoaded",
        "hq-native-launcher-hidden",
    )
    for path in (SITE_JS, built_js):
        text = path.read_text(encoding="utf-8")
        found = [marker for marker in forbidden if marker in text]
        if found:
            stop(f"检查失败：{path.relative_to(ROOT)} 仍有网站端客服主题代码：{', '.join(found)}")

    pages = []
    missing = []
    for page in dist.rglob("*.html"):
        html = page.read_text(encoding="utf-8")
        if "assets/site.js?v=" not in html:
            continue
        pages.append(page)
        if html.count(TARGET_TAG) != 1:
            missing.append(str(page.relative_to(ROOT)))
        if 'class="floating-chat"' in html:
            stop("检查失败：仍存在网站自定义客服悬浮按钮。")

    if not pages:
        stop("检查失败：没有找到生成后的网页。")
    if missing:
        stop("检查失败：客服代码不正确的页面：" + "、".join(missing[:5]))

    print(f"客服代码检查通过：{len(pages)} 个网站页面全部使用 {TARGET_URL}")


def main() -> None:
    if not SITE_JS.exists() or not BUILDER.exists() or not CHECKER.exists():
        stop("请把补丁中的两个文件解压到 dingshe-site 项目根目录后再运行。")

    site_js_text, site_js_newline = read_source(SITE_JS)
    builder_text, builder_newline = read_source(BUILDER)
    new_site_js = update_site_js(site_js_text)
    new_builder = update_builder(builder_text)

    backup_dir = ROOT / ("删除网站客服主题前备份_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
    (backup_dir / "assets").mkdir(parents=True)
    (backup_dir / "tools").mkdir(parents=True)
    shutil.copy2(SITE_JS, backup_dir / "assets" / "site.js")
    shutil.copy2(BUILDER, backup_dir / "tools" / "build_site.py")

    write_source(SITE_JS, new_site_js, site_js_newline)
    write_source(BUILDER, new_builder, builder_newline)

    try:
        subprocess.run([sys.executable, str(BUILDER)], cwd=ROOT, check=True)
        subprocess.run([sys.executable, str(CHECKER)], cwd=ROOT, check=True)
        verify()
    except Exception:
        shutil.copy2(backup_dir / "assets" / "site.js", SITE_JS)
        shutil.copy2(backup_dir / "tools" / "build_site.py", BUILDER)
        print("\n生成或检查失败，程序文件已自动恢复。")
        print("备份目录：" + str(backup_dir))
        raise

    print("\n修改完成：")
    print("1. 已删除网站端客服主题、重复加载和隐藏服务器按钮的代码。")
    print("2. 已删除网站自定义客服悬浮按钮，改用服务器客服按钮。")
    print("3. 资料页和联系页的咨询按钮仍可打开服务器客服。")
    print("4. 客服版本号已更新为 v=20260924b。")
    print("5. Excel、profiles.json、site_content.json 均未被补丁替换。")
    print("备份目录：" + str(backup_dir))
    print("请先预览 dist\\index.html，确认后运行‘上传到GitHub.bat’。")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("\n更新失败：" + str(exc))
        raise SystemExit(1)
