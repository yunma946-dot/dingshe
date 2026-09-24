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

TARGET_URL = "https://chat.hqvip.xyz/widget.js?site=site1&v=20260923a"
TARGET_TAG = f'<script src="{TARGET_URL}"></script>'
CACHE_VERSION = "20260924-chat1"


def read_source(path: Path) -> tuple[str, str]:
    raw = path.read_bytes()
    newline = "\r\n" if b"\r\n" in raw else "\n"
    return raw.decode("utf-8").replace("\r\n", "\n"), newline


def write_source(path: Path, text: str, newline: str) -> None:
    path.write_bytes(text.replace("\n", newline).encode("utf-8"))


def stop(message: str) -> None:
    raise RuntimeError(message)


def update_site_js(text: str) -> str:
    return re.sub(
        r"https://chat\.hqvip\.xyz/widget\.js\?[^'\"\s<]+",
        TARGET_URL,
        text,
    )


def update_builder(text: str) -> str:
    # Remove old direct widget tags, then add exactly one canonical tag before site.js.
    text = re.sub(
        r"[ \t]*<script\b(?=[^>]*\bsrc=['\"]https://chat\.hqvip\.xyz/widget\.js\?[^'\"]+['\"])[^>]*>\s*</script>\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    site_script_pattern = r'(<script src="\{prefix\}assets/site\.js\?v=[^\"]+" defer></script>)'
    if not re.search(site_script_pattern, text):
        stop("没有找到网站公共脚本位置，未修改任何文件。")

    text = re.sub(
        site_script_pattern,
        TARGET_TAG + "\n" + r"\1",
        text,
        count=1,
    )
    text, version_count = re.subn(
        r"assets/site\.js\?v=[^\"']+",
        f"assets/site.js?v={CACHE_VERSION}",
        text,
        count=1,
    )
    if version_count != 1:
        stop("没有找到网站脚本缓存版本，未修改任何文件。")
    return text


def verify() -> None:
    dist = ROOT / "dist"
    built_js = dist / "assets" / "site.js"
    if not built_js.exists():
        stop("检查失败：dist/assets/site.js 不存在。")

    pages = []
    missing = []
    for page in dist.rglob("*.html"):
        html = page.read_text(encoding="utf-8")
        if "assets/site.js?v=" not in html:
            continue
        pages.append(page)
        if TARGET_TAG not in html:
            missing.append(str(page.relative_to(ROOT)))

    if not pages:
        stop("检查失败：没有找到生成后的网页。")
    if missing:
        stop("检查失败：以下网页没有新客服代码：" + "、".join(missing[:5]))

    targets = [SITE_JS, BUILDER, built_js, *pages]
    old_urls = []
    pattern = re.compile(r"https://chat\.hqvip\.xyz/widget\.js\?[^'\"\s<]+")
    for path in targets:
        for url in pattern.findall(path.read_text(encoding="utf-8")):
            if url != TARGET_URL:
                old_urls.append(f"{path.relative_to(ROOT)}: {url}")
    if old_urls:
        stop("检查失败：仍有旧客服地址：" + "；".join(old_urls[:5]))

    print(f"客服代码检查通过：{len(pages)} 个网站页面已全部更新。")


def main() -> None:
    if not SITE_JS.exists() or not BUILDER.exists() or not CHECKER.exists():
        stop("请把补丁中的两个文件解压到 dingshe-site 项目根目录后再运行。")

    site_js_text, site_js_newline = read_source(SITE_JS)
    builder_text, builder_newline = read_source(BUILDER)
    new_site_js = update_site_js(site_js_text)
    new_builder = update_builder(builder_text)

    backup_dir = ROOT / ("客服代码修改前备份_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
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

    print("\n客服代码更新完成：")
    print(TARGET_TAG)
    print("Excel、profiles.json、site_content.json 均未被补丁替换。")
    print("备份目录：" + str(backup_dir))
    print("请先预览 dist\\index.html，确认后运行‘上传到GitHub.bat’。")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("\n更新失败：" + str(exc))
        raise SystemExit(1)
