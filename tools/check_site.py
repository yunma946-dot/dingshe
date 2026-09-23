from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
DOMAIN = "https://hqq2.com"
TEMPLATE_MARKERS = ("当前为首批资料模板", "待更新", "示例内容", "预留三张照片", "预留三张图片")


class ResourceParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.urls: list[str] = []
        self.anchor_hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = dict(attrs)
        for name in ("href", "src", "poster"):
            value = data.get(name)
            if value:
                self.urls.append(value)
                if tag == "a" and name == "href":
                    self.anchor_hrefs.append(value)
        srcset = data.get("srcset")
        if srcset:
            self.urls.extend(part.strip().split()[0] for part in srcset.split(",") if part.strip())


def tag_value(pattern: str, html: str) -> str:
    match = re.search(pattern, html, flags=re.I | re.S)
    return re.sub(r"\s+", " ", match.group(1)).strip() if match else ""


def local_target(base_url: str, raw_url: str) -> Path | None:
    if raw_url.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
        return None
    absolute = urljoin(base_url, raw_url)
    parsed = urlparse(absolute)
    if parsed.netloc != urlparse(DOMAIN).netloc:
        return None
    relative = parsed.path.lstrip("/")
    if not relative:
        return DIST / "index.html"
    target = DIST / relative
    if parsed.path.endswith("/"):
        return target / "index.html"
    return target


def sitemap_urls() -> set[str]:
    tree = ET.parse(DIST / "sitemap.xml")
    namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    return {node.text.strip() for node in tree.findall("s:url/s:loc", namespace) if node.text}


def main() -> None:
    errors: list[str] = []
    warnings: list[str] = []
    indexable_pages: dict[str, Path] = {}
    titles: defaultdict[str, list[str]] = defaultdict(list)
    descriptions: defaultdict[str, list[str]] = defaultdict(list)
    html_files = sorted(DIST.rglob("*.html"))
    verification_files = {
        path
        for path in html_files
        if path.parent == DIST
        and (path.name.startswith("google") or path.name.startswith("yandex_"))
    }
    page_files = [path for path in html_files if path not in verification_files]

    for path in page_files:
        html = path.read_text(encoding="utf-8")
        canonical = tag_value(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)', html)
        if not canonical:
            canonical = tag_value(r'<link[^>]+href=["\']([^"\']+)["\'][^>]+rel=["\']canonical["\']', html)
        if not canonical:
            errors.append(f"缺少 canonical：{path.relative_to(DIST)}")
            continue
        robots = tag_value(r'<meta[^>]+name=["\']robots["\'][^>]+content=["\']([^"\']+)', html).lower()
        title = tag_value(r"<title>(.*?)</title>", html)
        description = tag_value(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']*)', html)
        if not title:
            errors.append(f"缺少 title：{canonical}")
        if not description:
            errors.append(f"缺少 description：{canonical}")

        is_indexable = "noindex" not in robots
        if is_indexable:
            indexable_pages[canonical] = path
            titles[title.strip().lower()].append(canonical)
            descriptions[description.strip().lower()].append(canonical)
            marker = next((item for item in TEMPLATE_MARKERS if item in html), None)
            if marker:
                errors.append(f"可收录页面仍含模板文字“{marker}”：{canonical}")

        for script in re.findall(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', html, flags=re.I | re.S):
            try:
                json.loads(script)
            except json.JSONDecodeError as exc:
                errors.append(f"结构化数据不是有效 JSON：{canonical}（{exc.msg}）")

        parser = ResourceParser()
        parser.feed(html)
        for raw_url in parser.anchor_hrefs:
            if raw_url.startswith(("#", "mailto:", "tel:", "javascript:")):
                continue
            parsed_link = urlparse(urljoin(canonical, raw_url))
            if parsed_link.netloc == urlparse(DOMAIN).netloc and parsed_link.path.endswith("/"):
                errors.append(f"内部链接未明确指向 index.html，本地打开会显示目录：{canonical} -> {raw_url}")
        for raw_url in parser.urls:
            target = local_target(canonical, raw_url)
            if target is not None and not target.exists():
                errors.append(f"内部链接或资源不存在：{canonical} -> {raw_url}")

    for label, grouped in (("title", titles), ("description", descriptions)):
        for value, urls in grouped.items():
            if value and len(urls) > 1:
                errors.append(f"重复 {label}：{'、'.join(urls)}")

    sitemap = sitemap_urls()
    expected = set(indexable_pages)
    expected.discard(f"{DOMAIN}/404.html")
    missing = sorted(expected - sitemap)
    extra = sorted(sitemap - expected)
    if missing:
        errors.append("Sitemap 缺少可收录页面：" + "、".join(missing))
    if extra:
        errors.append("Sitemap 包含 noindex 或不存在页面：" + "、".join(extra))

    hero_sizes = []
    for width in (640, 1200, 1680):
        path = DIST / "assets" / f"hero-city-{width}.webp"
        if not path.exists():
            errors.append(f"缺少首页响应式图片：{path.name}")
        else:
            hero_sizes.append(path.stat().st_size)
    if hero_sizes and max(hero_sizes) > 700_000:
        warnings.append("首页最大 WebP 仍超过 700 KB，建议检查源图。")

    for required in (
        "robots.txt",
        "sitemap.xml",
        "image-sitemap.xml",
        "CNAME",
        "73fe7e61a18cb1678580f5a26ccab2a4.txt",
        "yandex_a1a3da35f80c99f0.html",
    ):
        if not (DIST / required).exists():
            errors.append(f"缺少发布文件：{required}")
    home_html = (DIST / "index.html").read_text(encoding="utf-8")
    if "G-Y6RVRSV2Z2" not in home_html:
        errors.append("首页缺少 GA4 代码：G-Y6RVRSV2Z2")
    for required_marker, label in (
        ('data-process-tabs', '预约咨询流程'),
        ('data-random-profiles', '随机资料推荐'),
        ('data-home-faq-question', '首页常见问题'),
    ):
        if required_marker not in home_html:
            errors.append(f"首页缺少{label}模块")
    if 'class="promise"' in home_html:
        errors.append("首页仍包含已要求移除的三栏介绍板块")

    profile_pages = [path for path in page_files if re.search(r"/model-\d+/index\.html$", path.as_posix())]
    for path in profile_pages:
        html = path.read_text(encoding="utf-8")
        if 'data-random-profiles' not in html or 'data-random-count="6"' not in html:
            errors.append(f"资料页缺少 6 个随机相关推荐：{path.relative_to(DIST)}")

    if warnings:
        print("\n检查提醒：")
        for warning in warnings:
            print("- " + warning)
    if errors:
        print("\n网站检查失败：")
        for error in errors:
            print("- " + error)
        raise SystemExit(1)

    noindex_pages = 0
    for path in page_files:
        html = path.read_text(encoding="utf-8")
        if re.search(r'<meta[^>]+name=["\']robots["\'][^>]+content=["\']noindex', html, flags=re.I):
            noindex_pages += 1
    print(
        f"网站检查通过：{len(page_files)} 个页面、{len(verification_files)} 个验证文件、"
        f"{len(profile_pages)} 个资料页、"
        f"{len(sitemap)} 个 Sitemap URL、{noindex_pages} 个 noindex 页面、0 个缺失内部资源。"
    )


if __name__ == "__main__":
    try:
        main()
    except (OSError, ET.ParseError, ValueError) as exc:
        print(f"网站检查失败：{exc}")
        sys.exit(1)
