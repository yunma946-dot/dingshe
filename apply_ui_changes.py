from __future__ import annotations

import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent
STYLE_PATH = ROOT / "assets" / "style.css"
BUILDER_PATH = ROOT / "tools" / "build_site.py"

HOME_CITY_SECTION = """<section class="section"><div class="wrap"><div class="section-head"><div><span class="kicker">{esc(home['city_section_kicker'])}</span><h2>{esc(home['city_section_title'])}</h2></div></div><div class="city-grid">{city_cards}</div></div></section>
"""

CITY_EXTRA_SECTIONS = """<section class="city-editorial"><div class="wrap city-editorial-grid"><div class="city-copy"><span class="kicker">{esc(city['editorial_kicker'])}</span><h2>{esc(city['editorial_title'])}</h2>{paragraphs}</div><div class="city-highlights">{highlights}</div></div></section>
{featured_section}
"""

MOBILE_MARKER = "/* Mobile direct four-item navigation (safe update 20260924) */"
MOBILE_CSS = r"""

/* Mobile direct four-item navigation (safe update 20260924) */
@media(max-width:760px){
  .nav-shell{
    height:auto;
    min-height:0;
    flex-wrap:wrap;
    gap:8px;
    padding-block:8px 10px;
  }
  .brand{
    width:100%;
    min-width:0;
    margin-right:0;
    justify-content:center;
  }
  .brand-logo{width:42px;height:42px}
  .brand-wordmark strong{font-size:1.08rem}
  .menu-toggle{display:none!important}
  .nav-links,
  .nav-links.open{
    position:relative;
    inset:auto;
    order:2;
    display:grid;
    grid-template-columns:repeat(4,minmax(0,1fr));
    width:100%;
    gap:4px;
    padding:0;
    border:0;
    background:transparent;
    box-shadow:none;
    overflow:visible;
  }
  .nav-links .nav-item{
    width:100%;
    min-width:0;
    height:40px;
    justify-content:center;
    gap:4px;
    padding:0 3px;
    white-space:nowrap;
  }
  .nav-links .nav-text{font-size:.76rem;letter-spacing:.02em}
  .resource-menu{position:static;display:block;width:auto;min-width:0}
  .resource-trigger{width:100%;min-width:0!important}
  .nav-chevron{margin-left:1px}
  .resource-dropdown{
    position:absolute;
    z-index:75;
    top:calc(100% + 8px);
    left:0;
    right:0;
    width:100%;
    max-height:min(70vh,520px);
    margin:0;
    padding:12px;
    overflow:auto;
    transform:none;
  }
  .resource-dropdown.open{display:block;transform:none}
}

@media(max-width:380px){
  .nav-links .nav-item{height:38px;padding-inline:2px}
  .nav-links .nav-text{font-size:.7rem}
  .nav-chevron{display:none}
}
"""


def read_source(path: Path) -> tuple[str, str]:
    raw = path.read_bytes()
    newline = "\r\n" if b"\r\n" in raw else "\n"
    return raw.decode("utf-8").replace("\r\n", "\n"), newline


def write_source(path: Path, text: str, newline: str) -> None:
    path.write_bytes(text.replace("\n", newline).encode("utf-8"))


def stop(message: str) -> None:
    raise RuntimeError(message)


def main() -> None:
    if not STYLE_PATH.exists() or not BUILDER_PATH.exists():
        stop("请把本补丁放在 dingshe-site 项目根目录后再运行。")

    style_text, style_newline = read_source(STYLE_PATH)
    builder_text, builder_newline = read_source(BUILDER_PATH)

    new_builder = builder_text
    home_count = new_builder.count(HOME_CITY_SECTION)
    city_count = new_builder.count(CITY_EXTRA_SECTIONS)

    if home_count == 1:
        new_builder = new_builder.replace(HOME_CITY_SECTION, "", 1)
    elif home_count > 1:
        stop("首页城市模块出现多次，未修改任何文件。")
    elif '<div class="city-grid">{city_cards}</div>' in new_builder:
        stop("首页城市模块结构与预期不同，未修改任何文件。")

    if city_count == 1:
        new_builder = new_builder.replace(CITY_EXTRA_SECTIONS, "", 1)
    elif city_count > 1:
        stop("城市浏览指南模块出现多次，未修改任何文件。")
    elif 'class="city-editorial"' in new_builder or "{featured_section}" in new_builder:
        stop("城市模块结构与预期不同，未修改任何文件。")

    new_builder, version_count = re.subn(
        r"style\.css\?v=[^\"']+",
        "style.css?v=20260924-safe1",
        new_builder,
        count=1,
    )
    if version_count != 1:
        stop("没有找到样式版本位置，未修改任何文件。")

    new_style = style_text
    if MOBILE_MARKER not in new_style:
        new_style = new_style.rstrip() + MOBILE_CSS + "\n"

    if new_builder == builder_text and new_style == style_text:
        print("本次界面修改已经存在，无需重复应用。")
        return

    backup_dir = ROOT / ("界面修改前备份_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
    (backup_dir / "assets").mkdir(parents=True)
    (backup_dir / "tools").mkdir(parents=True)
    shutil.copy2(STYLE_PATH, backup_dir / "assets" / "style.css")
    shutil.copy2(BUILDER_PATH, backup_dir / "tools" / "build_site.py")

    write_source(STYLE_PATH, new_style, style_newline)
    write_source(BUILDER_PATH, new_builder, builder_newline)

    try:
        subprocess.run([sys.executable, str(ROOT / "tools" / "build_site.py")], cwd=ROOT, check=True)
        subprocess.run([sys.executable, str(ROOT / "tools" / "check_site.py")], cwd=ROOT, check=True)

        home_html = (ROOT / "dist" / "index.html").read_text(encoding="utf-8")
        if '<div class="city-grid">' in home_html:
            stop("检查失败：首页按城市浏览模块仍然存在。")

        remaining_city_sections = []
        for city_page in (ROOT / "dist").glob("*/index.html"):
            html = city_page.read_text(encoding="utf-8")
            if 'class="city-editorial"' in html or 'class="city-featured"' in html:
                remaining_city_sections.append(str(city_page.relative_to(ROOT)))
        if remaining_city_sections:
            stop("检查失败：城市页面仍存在旧模块：" + "、".join(remaining_city_sections))

        built_css = (ROOT / "dist" / "assets" / "style.css").read_text(encoding="utf-8")
        if MOBILE_MARKER not in built_css:
            stop("检查失败：手机导航样式没有生成。")
    except Exception:
        shutil.copy2(backup_dir / "assets" / "style.css", STYLE_PATH)
        shutil.copy2(backup_dir / "tools" / "build_site.py", BUILDER_PATH)
        print("\n生成或检查失败，程序文件已自动恢复。")
        print("备份目录：" + str(backup_dir))
        raise

    print("\n本次修改完成：")
    print("1. 手机端隐藏右上角导航按钮，四个导航项直接横排显示。")
    print("2. 删除所有城市页的浏览指南和精选入口。")
    print("3. 删除首页的按城市浏览模块。")
    print("4. Excel、profiles.json、site_content.json 均未被补丁替换。")
    print("备份目录：" + str(backup_dir))
    print("请先预览 dist\\index.html，确认后再运行“上传到GitHub.bat”。")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("\n更新失败：" + str(exc))
        raise SystemExit(1)
