from __future__ import annotations

import html
import hashlib
import json
import random
import re
import shutil
from datetime import date
from pathlib import Path
from urllib.parse import urlparse
from xml.sax.saxutils import escape as xml_escape


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
MEDIA_SOURCE = ROOT / "photos"
VERIFICATION_SOURCE = ROOT / "verification"
SEO_STATE_PATH = ROOT / "seo_state.json"
INDEXNOW_PENDING_PATH = ROOT / "indexnow_pending.json"
DOMAIN = "https://hqq2.com"
HOME_URL = f"{DOMAIN}/"
BRAND = "顶奢"
BRAND_EN = "DINGSHE"
CONTACT_EMAIL = "dingshe1@outlook.com"
CONTACT_ADDRESS = "123 Fashion Avenue, Suite 400, New York, NY 10001, USA"
GA4_ID = "G-Y6RVRSV2Z2"

CITIES = [
    {
        "name": "上海", "slug": "shanghai", "line": "海派格调与都会精选",
        "intro": "浏览上海城市精选资料。每套内容均使用独立页面、独立图片说明和稳定网址，方便按风格继续查看。",
        "seo_description": "顶奢上海资源库，集中展示上海城市精选资料、独立图片、视频、风格介绍与相关推荐。",
        "editorial_title": "上海城市资料的浏览方式",
        "paragraphs": [
            "上海页面以都会感和清晰的视觉资料为主。城市页负责汇总入口，详情页则承载每套资料的图片、视频、风格说明与相关内容，避免把所有信息堆在同一个列表中。",
            "浏览时可先从精选推荐进入，再通过详情页底部的相关推荐继续查看。每个重要页面都能回到上海资源库，形成清晰、可抓取的站内路径。",
        ],
        "highlights": [("都会风格", "突出简洁、现代和镜头表现力。"), ("独立媒体", "每页预留三张照片与一个视频位置。"), ("持续扩充", "新增资料时沿用固定结构，不影响现有网址。")],
        "faq": [("怎样查看上海全部资料？", "本页下方会展示当前全部上海资料，点击任意卡片即可进入独立详情页。"), ("上海详情页之间可以继续跳转吗？", "可以。每个详情页均提供相关推荐和返回上海资源库的链接。"), ("图片和视频会单独更新吗？", "可以按页面独立替换媒体文件，其他详情页不会受到影响。")],
    },
    {
        "name": "广州", "slug": "guangzhou", "line": "岭南风尚与城市精选",
        "intro": "广州资源库按独立资料页组织内容，兼顾图片浏览、详细介绍、相关推荐和后续扩展。",
        "seo_description": "顶奢广州资源库，浏览广州城市精选资料、专属图片、视频介绍及相关城市内容。",
        "editorial_title": "广州资源库内容结构",
        "paragraphs": [
            "广州城市页不是简单的卡片集合，而是全部广州详情页的主要入口。资料卡提供清晰摘要，详情页补充媒体、风格与独立文字，让用户和搜索引擎都能判断页面主题。",
            "页面之间通过城市回链和相关推荐连接。后续新增广州资料时，只需加入新的独立页面，即可继续扩展而不打乱现有内容。",
        ],
        "highlights": [("城市入口", "集中连接广州全部独立资料页面。"), ("图文一致", "图片说明、标题与附近文字保持同一主题。"), ("相关推荐", "从一个详情页可自然进入更多相关内容。")],
        "faq": [("广州资源是否都有独立网址？", "是，每套资料均有固定详情页网址，便于分享、收录和后续更新。"), ("如何返回广州城市页？", "详情页的面包屑、正文链接和底部入口都可以返回广州资源库。"), ("新增内容会改变原来的链接吗？", "不会，新增页面会使用独立网址，原有页面网址保持不变。")],
    },
    {
        "name": "深圳", "slug": "shenzhen", "line": "湾区新锐与现代精选",
        "intro": "深圳资源库聚合现代城市风格资料，并通过独立详情页展示图片、视频和更完整的介绍。",
        "seo_description": "顶奢深圳资源库，查看深圳现代城市精选资料、图片展示、视频位置与相关推荐。",
        "editorial_title": "深圳城市内容如何组织",
        "paragraphs": [
            "深圳页面采用城市聚合与独立详情两层结构：城市页用于发现和比较，详情页用于阅读具体资料。这样的组织方式能减少重复文字，也让每个页面拥有明确主题。",
            "精选推荐优先展示代表性入口，完整列表保持所有页面可发现；详情页再通过同城与跨城推荐连接更多内容。",
        ],
        "highlights": [("现代气质", "整体内容强调利落、清晰和当代视觉。"), ("快速发现", "精选入口与完整列表同时保留。"), ("双向内链", "城市页与详情页之间保持可抓取回链。")],
        "faq": [("深圳页面包含哪些内容？", "包含城市简介、精选入口、完整资料列表、专题说明和常见问题。"), ("能否只查看深圳同城推荐？", "详情页会优先推荐同城内容，并保留其他城市入口。"), ("资料图片如何被搜索发现？", "图片使用独立替代文字和说明，并放在主题一致的详情页中。")],
    },
    {
        "name": "北京", "slug": "beijing", "line": "京华气韵与城市精选",
        "intro": "北京资源库以独立、可持续更新的页面展示城市精选内容，并保留明确的上下级导航。",
        "seo_description": "顶奢北京资源库，汇总北京城市精选资料、独立图片、视频、专题说明和相关推荐。",
        "editorial_title": "北京资料页的发现路径",
        "paragraphs": [
            "北京城市页承担资源目录作用，所有重要详情页都能从这里直接进入。详情页的标题、图片说明和正文围绕同一套资料展开，避免只有图片而缺少上下文。",
            "用户可以从首页进入北京资源库，再进入具体资料，并通过面包屑或文末链接返回；这一完整路径也有利于搜索引擎发现页面。",
        ],
        "highlights": [("层级清楚", "首页、北京城市页与详情页形成稳定路径。"), ("独立说明", "每套资料可配置不同标题、介绍和媒体。"), ("相关发现", "详情页之间通过有意义的文字链接互联。")],
        "faq": [("北京资料从哪里进入？", "可从首页城市入口或顶部模特资源库下拉菜单进入北京资源库。"), ("每套资料是否可以单独修改？", "可以，文字、图片、视频和 SEO 信息均可按详情页独立调整。"), ("相关推荐是固定的吗？", "系统会优先展示相关同城内容，并补充其他城市入口。")],
    },
    {
        "name": "杭州", "slug": "hangzhou", "line": "江南雅意与城市精选",
        "intro": "杭州资源库围绕清晰、雅致的城市内容体验组织资料，方便从城市页持续发现独立详情。",
        "seo_description": "顶奢杭州资源库，浏览杭州城市精选资料、三图一视频展示、独立说明与站内推荐。",
        "editorial_title": "杭州城市资料浏览指南",
        "paragraphs": [
            "杭州城市页将资料入口、精选推荐和主题说明放在同一页面中，但每套资料仍保留自己的详情页，确保图片和文字拥有对应的落地页面。",
            "详情页通过返回杭州资源库、同城推荐和其他城市入口组成自然的内部链接网络，用户不需要反复返回首页也能继续浏览。",
        ],
        "highlights": [("雅致呈现", "版面强调留白、层次和内容可读性。"), ("图片落地页", "每组图片对应自己的资料详情页。"), ("自然内链", "以城市与资料名称作为清晰的链接文字。")],
        "faq": [("杭州资源页只是资料列表吗？", "不是，本页还包含城市介绍、精选推荐、主题正文和常见问题。"), ("图片是否有独立说明？", "详情页主图和缩略图均配置与资料主题一致的替代文字，主图下方还有说明。"), ("以后可以继续增加杭州资料吗？", "可以，新增页面会自动进入城市列表、相关推荐和站点地图。")],
    },
]


def load_site_content() -> dict:
    source = ROOT / "site_content.json"
    if not source.exists():
        raise FileNotFoundError("缺少 site_content.json，请使用整站工作表重新生成内容文件。")
    content = json.loads(source.read_text(encoding="utf-8"))
    required = {"home", "footer", "cities", "pages"}
    missing = sorted(required - set(content))
    if missing:
        raise ValueError("site_content.json 缺少字段：" + "、".join(missing))
    if not isinstance(content["cities"], list) or not content["cities"]:
        raise ValueError("site_content.json 的 cities 必须包含城市资料。")
    return content


SITE_CONTENT = load_site_content()
HOME_CONTENT = SITE_CONTENT["home"]
FOOTER_CONTENT = SITE_CONTENT["footer"]
FIXED_PAGES = SITE_CONTENT["pages"]
ALL_CITIES = SITE_CONTENT["cities"]


def display_order(item: dict, fallback: int = 999999) -> int:
    try:
        return int(item.get("display_order", fallback))
    except (TypeError, ValueError):
        return fallback


def is_published(item: dict) -> bool:
    return item.get("publish_status", "已发布") == "已发布"


def is_indexable(item: dict) -> bool:
    return is_published(item) and item.get("allow_index", "是") == "是"


CITIES = sorted(
    [city for city in ALL_CITIES if is_published(city)],
    key=lambda city: (display_order(city), city.get("slug", "")),
)
BRAND = HOME_CONTENT.get("brand_name", BRAND)
BRAND_EN = HOME_CONTENT.get("brand_en", BRAND_EN)
CONTACT_EMAIL = FOOTER_CONTENT.get("email", CONTACT_EMAIL)
CONTACT_ADDRESS = FOOTER_CONTENT.get("address", CONTACT_ADDRESS)

PROFILE_TITLES = [
    "澄光雅集",
    "鎏金映像",
    "云端风尚",
    "星河雅韵",
    "绮境轻奢",
    "摩登画境",
    "静雅臻选",
    "璀璨华章",
    "高定风格",
    "城市绮梦",
]

MEDIA_LABELS = {1: "主图", 2: "侧影图", 3: "氛围图"}


def profiles() -> list[dict]:
    items: list[dict] = []
    for city in CITIES:
        for idx in range(1, 11):
            n = f"{idx:03d}"
            items.append(
                {
                    "city": city["name"],
                    "city_slug": city["slug"],
                    "slug": f"model-{n}",
                    "name": f"{city['name']}{PROFILE_TITLES[idx - 1]}",
                    "tag": ["都会", "雅致", "轻奢", "清新", "典雅"][idx % 5],
                    "summary": f"{city['name']}{PROFILE_TITLES[idx - 1]}主题独立展示页，预留三张照片、一个视频及完整介绍位置。",
                    "intro": "当前为首批资料模板。后续可直接替换专属图片、视频、标题与介绍，页面网址保持不变。",
                    "seo_title": f"{city['name']}{PROFILE_TITLES[idx - 1]}｜图片与视频｜{BRAND}",
                    "seo_description": f"浏览{city['name']}{PROFILE_TITLES[idx - 1]}的独立资料、三张图片、视频介绍与相关推荐。",
                    "body_1": f"{city['name']}{PROFILE_TITLES[idx - 1]}拥有独立内容区域，图片说明与页面文字围绕同一资料主题设置。",
                    "body_2": "本页可独立修改名称、风格、简介、正文、图片和视频，更新后网址保持不变。",
                    "body_3": f"需要查看更多内容时，可返回{city['name']}资源库或继续浏览页面下方的相关推荐。",
                    "process_media": False,
                    "publish_status": "已发布",
                    "allow_index": "否",
                    "home_featured": "否",
                    "display_order": idx,
                    "first_published": "",
                    "last_updated": "",
                    "content_review": "待完善",
                    "path": f"{city['slug']}/model-{n}/",
                    "media_dir": f"photos/{city['slug']}-model-{n}",
                }
            )
    return items


def load_profiles() -> list[dict]:
    source = ROOT / "profiles.json"
    if source.exists():
        items = json.loads(source.read_text(encoding="utf-8"))
        for profile in items:
            match = re.search(r"model-(\d+)$", profile.get("slug", ""))
            if match and re.search(r"精选资料\s*\d+$", profile.get("name", "")):
                index = int(match.group(1))
                if 1 <= index <= len(PROFILE_TITLES):
                    title = PROFILE_TITLES[index - 1]
                    profile["name"] = f"{profile['city']}{title}"
                    profile["summary"] = f"{profile['city']}{title}主题独立展示页，预留三张照片、一个视频及完整介绍位置。"
            profile.pop("city_code", None)
            profile.pop("number", None)
            profile.setdefault("seo_title", f"{profile['name']}｜图片与视频｜{BRAND}")
            profile.setdefault("seo_description", profile["summary"])
            profile.setdefault("body_1", f"{profile['name']}拥有独立内容区域，图片说明与页面文字围绕同一资料主题设置。")
            profile.setdefault("body_2", "本页可独立修改名称、风格、简介、正文、图片和视频，更新后网址保持不变。")
            profile.setdefault("body_3", f"需要查看更多内容时，可返回{profile['city']}资源库或继续浏览页面下方的相关推荐。")
            profile.setdefault("process_media", False)
            profile.setdefault("publish_status", "已发布")
            profile.setdefault("allow_index", "否")
            profile.setdefault("home_featured", "否")
            profile.setdefault("display_order", int(match.group(1)) if match else 999999)
            profile.setdefault("first_published", "")
            profile.setdefault("last_updated", "")
            for slot in range(1, 4):
                profile.setdefault(f"image_{slot}_alt", f"{profile['name']}，{profile.get('tag', '精选')}风格{MEDIA_LABELS[slot]}")
                profile.setdefault(f"image_{slot}_caption", f"{profile['name']} · {MEDIA_LABELS[slot]}")
            profile.setdefault("video_title", "")
            profile.setdefault("video_description", "")
            profile.setdefault("video_poster", "")
            profile.setdefault("video_upload_date", "")
            profile.setdefault("video_duration", "")
            profile.setdefault("content_review", "待完善")
        return items
    return profiles()


ALL_PROFILES = load_profiles()
PUBLISHED_CITY_SLUGS = {city["slug"] for city in CITIES}
PROFILES = sorted(
    [profile for profile in ALL_PROFILES if is_published(profile) and profile.get("city_slug") in PUBLISHED_CITY_SLUGS],
    key=lambda profile: (
        next((display_order(city) for city in CITIES if city["slug"] == profile.get("city_slug")), 999999),
        display_order(profile),
        profile.get("slug", ""),
    ),
)
INDEXABLE_PROFILES = [profile for profile in PROFILES if is_indexable(profile)]


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def root_prefix(depth: int) -> str:
    return "../" * depth


def site_href(prefix: str, route: str = "") -> str:
    """Return a relative HTML file link that also works when opened from disk."""
    cleaned = str(route).strip("/")
    return f"{prefix}{cleaned + '/' if cleaned else ''}index.html"


def nav(prefix: str) -> str:
    city_links = "".join(
        f'<a class="resource-city" href="{site_href(prefix, city["slug"])}" role="menuitem"><span class="resource-copy"><b>{esc(city["name"])}资源</b><small>{esc(city["line"])}</small></span><span class="resource-arrow" aria-hidden="true">↗</span></a>'
        for city in CITIES
    )
    home_link = site_href(prefix)
    return f"""
<a class="skip" href="#main">跳到主要内容</a>
<header class="site-header">
  <div class="wrap nav-shell">
    <a class="brand" href="{home_link}" aria-label="返回{BRAND}首页">
      <img class="brand-logo" src="{prefix}assets/brand-logo.svg" alt="" width="54" height="54">
      <span class="brand-wordmark"><strong><i>顶</i><i>奢</i></strong><small>{BRAND_EN}</small></span>
    </a>
    <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="main-nav"><span class="menu-lines" aria-hidden="true"><i></i><i></i></span><span>导航</span></button>
    <nav id="main-nav" class="nav-links" aria-label="主导航">
      <a class="nav-item" href="{home_link}"><span class="nav-text">{esc(HOME_CONTENT['nav_home_label'])}</span></a>
      <div class="resource-menu">
        <button class="nav-item resource-trigger" type="button" aria-expanded="false" aria-controls="resource-dropdown"><span class="nav-text">{esc(HOME_CONTENT['nav_resources_label'])}</span><span class="nav-chevron" aria-hidden="true"></span></button>
        <div id="resource-dropdown" class="resource-dropdown" role="menu" aria-label="城市资源入口">
          <div class="resource-head"><span>{esc(HOME_CONTENT['nav_resources_en'])}</span><b>{esc(HOME_CONTENT['nav_resources_prompt'])}</b></div>
          <div class="resource-grid">{city_links}</div>
        </div>
      </div>
      <a class="nav-item" href="{site_href(prefix, 'about')}"><span class="nav-text">{esc(HOME_CONTENT['nav_about_label'])}</span></a>
      <a class="nav-item" href="{site_href(prefix, 'contact')}"><span class="nav-text">{esc(HOME_CONTENT['nav_contact_label'])}</span></a>
    </nav>
  </div>
</header>"""


def footer(prefix: str) -> str:
    city_links = "".join(
        f'<a href="{site_href(prefix, city["slug"])}">{city["name"]}</a>' for city in CITIES
    )
    return f"""
<footer class="footer">
  <div class="wrap footer-grid">
    <section><div class="footer-brand">{esc(BRAND)}</div><p>{esc(FOOTER_CONTENT['description'])}</p><address class="footer-contact"><a href="mailto:{esc(CONTACT_EMAIL)}"><span>{esc(FOOTER_CONTENT['email_label'])}</span>{esc(CONTACT_EMAIL)}</a><span><b>{esc(FOOTER_CONTENT['address_label'])}</b>{esc(CONTACT_ADDRESS)}</span></address></section>
    <section><h2>{esc(FOOTER_CONTENT['city_nav_title'])}</h2><div class="footer-links">{city_links}</div></section>
    <section><h2>{esc(FOOTER_CONTENT['site_info_title'])}</h2><div class="footer-links"><a href="{site_href(prefix, 'about')}">{esc(FOOTER_CONTENT['about_label'])}</a><a href="{site_href(prefix, 'contact')}">{esc(FOOTER_CONTENT['contact_label'])}</a><a href="{site_href(prefix, 'privacy')}">{esc(FOOTER_CONTENT['privacy_label'])}</a><a href="{site_href(prefix, 'terms')}">{esc(FOOTER_CONTENT['terms_label'])}</a></div></section>
  </div>
  <div class="wrap footer-bottom"><span>{esc(FOOTER_CONTENT['copyright'])}</span></div>
</footer>
<button class="floating-chat" data-chat-open type="button" aria-label="{esc(FOOTER_CONTENT['chat_aria_label'])}">
  <span class="chat-orbit" aria-hidden="true"></span>
  <span class="chat-emblem" aria-hidden="true"><img src="{prefix}assets/brand-logo.svg" alt="" width="46" height="46"></span>
  <span class="chat-label"><b>{esc(FOOTER_CONTENT['chat_title'])}</b><small>{esc(FOOTER_CONTENT['chat_subtitle'])}</small></span>
</button>
<script src="{prefix}assets/site.js?v=20260923b" defer></script>"""


def page(
    title: str,
    description: str,
    canonical: str,
    depth: int,
    body: str,
    extra_head: str = "",
    *,
    indexable: bool = True,
) -> str:
    prefix = root_prefix(depth)
    robots = "index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1" if indexable else "noindex,follow"
    analytics = f"""<script async src="https://www.googletagmanager.com/gtag/js?id={GA4_ID}"></script>
  <script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','{GA4_ID}',{{anonymize_ip:true}});</script>"""
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}">
  <meta name="robots" content="{robots}">
  <link rel="canonical" href="{esc(canonical)}">
  <meta name="theme-color" content="#080b12">
  <link rel="icon" type="image/svg+xml" href="{prefix}assets/favicon.svg">
  <link rel="stylesheet" href="{prefix}assets/style.css?v=20260923b">
  {analytics}
  {extra_head}
</head>
<body>
{nav(prefix)}
<main id="main">{body}</main>
{footer(prefix)}
</body>
</html>"""


def media_alt(profile: dict, slot: int) -> str:
    return profile.get(f"image_{slot}_alt") or f"{profile['name']}，{profile['tag']}风格{MEDIA_LABELS[slot]}"


def media_caption(profile: dict, slot: int) -> str:
    return profile.get(f"image_{slot}_caption") or f"{profile['name']} · {profile['tag']}风格{MEDIA_LABELS[slot]}"


def existing_profile_image_source(profile: dict, slot: int) -> str | None:
    folder = ROOT / profile["media_dir"]
    for ext in ("jpg", "jpeg", "png", "webp", "avif"):
        candidate = folder / f"{slot:02d}.{ext}"
        if candidate.exists():
            return f"{profile['media_dir']}/{candidate.name}"
    return None


def profile_image_source(profile: dict, slot: int) -> str:
    existing = existing_profile_image_source(profile, slot)
    if existing:
        return existing
    return f"{profile['media_dir']}/{slot:02d}.jpg"


def media_placeholder(prefix: str, profile: dict, slot: int, cls: str = "", eager: bool = False) -> str:
    existing = existing_profile_image_source(profile, slot)
    fallback = f"{prefix}assets/profile-placeholder-{slot}.svg"
    src = f"{prefix}{existing}" if existing else fallback
    srcset = ""
    if existing:
        srcset = (
            f' srcset="{prefix}{profile["media_dir"]}/{slot:02d}-480.webp 480w, '
            f'{prefix}{profile["media_dir"]}/{slot:02d}-800.webp 800w" sizes="(max-width:760px) 92vw, 800px"'
        )
    loading = "eager" if eager else "lazy"
    priority = ' fetchpriority="high"' if eager else ""
    return f'<img class="{cls}" src="{src}"{srcset} alt="{esc(media_alt(profile, slot))}" width="800" height="1000" loading="{loading}" decoding="async"{priority}>'


def card(prefix: str, profile: dict) -> str:
    href = site_href(prefix, profile["path"])
    return f"""<article class="profile-card">
  <a class="card-media" href="{href}">{media_placeholder(prefix, profile, 1)}</a>
  <div class="card-body"><div class="card-meta"><span>{profile['city']}精选</span><span>{profile['tag']}风格</span></div>
  <h3><a href="{href}">{esc(profile['name'])}</a></h3>
  <p>{esc(profile['summary'])}</p><a class="text-link" href="{href}">查看{esc(profile['name'])} <span aria-hidden="true">→</span></a></div>
</article>"""


def profile_card_payload(prefix: str, profile: dict) -> dict:
    existing = existing_profile_image_source(profile, 1)
    image = f"{prefix}{existing}" if existing else f"{prefix}assets/profile-placeholder-1.svg"
    srcset = ""
    if existing:
        srcset = (
            f'{prefix}{profile["media_dir"]}/01-480.webp 480w, '
            f'{prefix}{profile["media_dir"]}/01-800.webp 800w'
        )
    return {
        "href": site_href(prefix, profile["path"]),
        "image": image,
        "srcset": srcset,
        "alt": media_alt(profile, 1),
        "name": profile["name"],
        "city": profile["city"],
        "tag": profile["tag"],
        "summary": profile["summary"],
    }


def random_profile_section(
    section_key: str,
    pool: list[dict],
    prefix: str,
    count: int,
    kicker: str,
    title: str,
    description: str,
    *,
    extra_class: str = "",
    footer_links: str = "",
) -> str:
    if not pool:
        return ""
    count = max(1, min(count, len(pool)))
    initial = random.Random(section_key).sample(pool, count)
    initial_cards = "".join(card(prefix, profile) for profile in initial)
    payload = json.dumps(
        [profile_card_payload(prefix, profile) for profile in pool],
        ensure_ascii=False,
        separators=(",", ":"),
    ).replace("</", "<\\/")
    classes = f"section section-dark random-profiles {extra_class}".strip()
    description_html = f"<p>{esc(description)}</p>" if str(description).strip() else ""
    return f'''<section class="{classes}" data-random-profiles data-random-count="{count}">
  <div class="wrap"><div class="section-head"><div><span class="kicker">{esc(kicker)}</span><h2>{esc(title)}</h2></div>{description_html}</div>
  <div class="profile-grid related-grid" data-random-grid>{initial_cards}</div>{footer_links}
  <script type="application/json" data-random-source>{payload}</script></div>
</section>'''


def available_profile_images(profile: dict) -> list[tuple[int, str, str, str]]:
    found: list[tuple[int, str, str, str]] = []
    for slot in range(1, 4):
        source = existing_profile_image_source(profile, slot)
        if source:
            found.append((slot, f"{DOMAIN}/{source}", media_alt(profile, slot), media_caption(profile, slot)))
    return found


def profile_video_source(profile: dict) -> str | None:
    source = ROOT / profile["media_dir"] / "profile.mp4"
    return f"{profile['media_dir']}/profile.mp4" if source.exists() else None


def profile_video_poster(profile: dict) -> str:
    configured = str(profile.get("video_poster", "")).strip()
    if configured:
        candidate = configured if configured.startswith("photos/") else f"{profile['media_dir']}/{configured}"
        if (ROOT / candidate).exists():
            return candidate
    first_image = existing_profile_image_source(profile, 1)
    return first_image or "assets/video-poster.svg"


def profile_media_label(profile: dict) -> str:
    image_count = len(available_profile_images(profile))
    video_count = 1 if profile_video_source(profile) else 0
    return f"{image_count} 张图 · {video_count} 个视频"


def build_home() -> str:
    home = HOME_CONTENT
    city_cards = "".join(
        f'<a class="city-card" href="{site_href("", city["slug"])}"><div><h3>{esc(city["name"])}</h3><p>{esc(city["line"])}</p></div><span class="city-card-link">{esc(home["city_card_link_label"])} →</span></a>'
        for city in CITIES
    )
    process_defaults = [
        ("联系客服", "打开顶奢专属客服，说明想浏览或咨询的城市资料。"),
        ("告知需求", "提供城市、时间和偏好，方便客服快速筛选合适资料。"),
        ("查看资料", "客服发送可查看的页面与媒体内容，您可以继续比较和筛选。"),
        ("确认安排", "确认选择、时间和必要事项；如有变化请及时沟通。"),
        ("保持联系", "按确认信息进行后续沟通，并通过官方客服核对最新情况。"),
    ]
    process_items = [
        (
            str(home.get(f"process_{index}_label", fallback_label)),
            str(home.get(f"process_{index}_text", fallback_text)),
        )
        for index, (fallback_label, fallback_text) in enumerate(process_defaults, start=1)
    ]
    process_tabs = "".join(
        f'<button class="process-tab{" active" if index == 1 else ""}" type="button" role="tab" aria-selected="{"true" if index == 1 else "false"}" aria-controls="process-panel-{index}" id="process-tab-{index}" data-process-tab="{index}"><span>{index:02d}</span><b>{esc(label)}</b></button>'
        for index, (label, _) in enumerate(process_items, start=1)
    )
    process_panels = "".join(
        f'<article class="process-panel{" active" if index == 1 else ""}" role="tabpanel" id="process-panel-{index}" aria-labelledby="process-tab-{index}" data-process-panel="{index}"{" hidden" if index != 1 else ""}><span>STEP {index:02d}</span><h3>{esc(label)}</h3><p>{esc(text)}</p></article>'
        for index, (label, text) in enumerate(process_items, start=1)
    )
    process_section = f'''<section class="home-process"><div class="wrap"><div class="section-head"><div><span class="kicker">{esc(home.get('process_kicker', 'CONSULTATION PROCESS'))}</span><h2>{esc(home.get('process_title', '预约咨询流程'))}</h2></div><p>按步骤了解咨询方式，具体信息请以官方客服的最新确认为准。</p></div><div class="process-shell" data-process-tabs><div class="process-tabs" role="tablist" aria-label="预约咨询流程">{process_tabs}</div><div class="process-panels">{process_panels}</div></div></div></section>'''
    try:
        random_count = int(home.get("random_count", 8))
    except (TypeError, ValueError):
        random_count = 8
    random_section = random_profile_section(
        "home-random-profiles",
        PROFILES,
        "",
        max(4, min(random_count, 12)),
        str(home.get("random_kicker", "DISCOVER MORE")),
        str(home.get("random_title", "随机资料推荐")),
        "",
        extra_class="home-random",
    )
    faq_defaults = [
        ("如何选择城市资料？", "可先从首页选择城市，再通过资料卡进入独立详情页；也可以联系在线客服说明偏好。"),
        ("每套资料是否有独立页面？", "是。每套资料使用固定详情页，文字、图片和视频可独立更新。"),
        ("图片和视频如何查看？", "已上传的真实媒体会显示在详情页；未上传内容会保留品牌占位图，不会伪造资料。"),
        ("页面内容多久更新？", "城市和资料可持续增加；页面会显示真实更新时间，Sitemap 仅提交允许收录的页面。"),
        ("如何联系顶奢客服？", "点击页面右下角的顶奢专属咨询按钮，即可在当前页面打开客服窗口。"),
        ("后续会增加更多城市吗？", "可以。新增城市和资料会沿用现有结构，并通过首页、城市页和相关推荐连接。"),
    ]
    faq_items = [
        (
            str(home.get(f"home_faq_{index}_question", fallback_question)),
            str(home.get(f"home_faq_{index}_answer", fallback_answer)),
        )
        for index, (fallback_question, fallback_answer) in enumerate(faq_defaults, start=1)
    ]
    faq_html = "".join(
        f'<article class="home-faq-item{" active" if index == 1 else ""}"><h3><button type="button" data-home-faq-question aria-expanded="{"true" if index == 1 else "false"}" aria-controls="home-faq-answer-{index}"><span>{index:02d}</span>{esc(question)}<i aria-hidden="true"></i></button></h3><div class="home-faq-answer" id="home-faq-answer-{index}"{" hidden" if index != 1 else ""}><p>{esc(answer)}</p></div></article>'
        for index, (question, answer) in enumerate(faq_items, start=1)
    )
    faq_section = f'''<section class="home-faq"><div class="wrap faq-grid"><div><span class="kicker">{esc(home.get('home_faq_kicker', 'COMMON QUESTIONS'))}</span><h2>{esc(home.get('home_faq_title', '常见问题'))}</h2><p>{esc(home.get('home_faq_description', '关于资料浏览、媒体更新和客服入口的说明。'))}</p></div><div class="home-faq-list">{faq_html}</div></div></section>'''
    media_count = sum(len(available_profile_images(profile)) + (1 if profile_video_source(profile) else 0) for profile in PROFILES)
    body = f"""
<section class="hero home-hero">
  <picture class="hero-media"><source type="image/webp" srcset="assets/hero-city-640.webp 640w, assets/hero-city-1200.webp 1200w, assets/hero-city-1680.webp 1680w" sizes="100vw"><img class="hero-image" src="assets/hero-city.png" alt="{esc(home['hero_image_alt'])}" width="1680" height="945" loading="eager" decoding="async" fetchpriority="high"></picture>
  <div class="hero-shade"></div>
  <div class="wrap hero-copy"><div class="kicker">{esc(home['hero_kicker'])}</div><h1>{esc(home['hero_title_line1'])}<br><em>{esc(home['hero_title_emphasis'])}</em></h1><p>{esc(home['hero_description'])}</p><div class="hero-stats"><span><b>{len(CITIES)}</b> {esc(home['stat_city_label'])}</span><span><b>{len(PROFILES)}</b> {esc(home['stat_profile_label'])}</span><span><b>{media_count}</b> {esc(home['stat_media_label'])}</span></div></div>
</section>
{process_section}
<section class="section"><div class="wrap"><div class="section-head"><div><span class="kicker">{esc(home['city_section_kicker'])}</span><h2>{esc(home['city_section_title'])}</h2></div></div><div class="city-grid">{city_cards}</div></div></section>
{random_section}
{faq_section}"""
    schema = json.dumps({
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "WebSite", "name": BRAND, "url": f"{DOMAIN}/"},
            {
                "@type": "Organization",
                "name": BRAND,
                "url": f"{DOMAIN}/",
                "email": CONTACT_EMAIL,
                "address": {"@type": "PostalAddress", "streetAddress": CONTACT_ADDRESS},
            },
            {
                "@type": "FAQPage",
                "mainEntity": [
                    {"@type": "Question", "name": question, "acceptedAnswer": {"@type": "Answer", "text": answer}}
                    for question, answer in faq_items
                ],
            },
        ],
    }, ensure_ascii=False)
    return page(home["seo_title"], home["seo_description"], f"{DOMAIN}/", 0, body, f'<script type="application/ld+json">{schema}</script>')


def build_city(city: dict) -> str:
    subset = [p for p in PROFILES if p["city_slug"] == city["slug"]]
    indexable_subset = [p for p in subset if is_indexable(p)]
    cards = "".join(card("../", p) for p in subset)
    highlight_items = [
        (city[f"highlight_{index}_title"], city[f"highlight_{index}_text"])
        for index in range(1, 4)
    ]
    faq_items = [
        (city[f"faq_{index}_question"], city[f"faq_{index}_answer"])
        for index in range(1, 4)
    ]
    highlights = "".join(
        f'<article><h3>{esc(title)}</h3><p>{esc(text)}</p></article>'
        for title, text in highlight_items
    )
    paragraphs = "".join(f"<p>{esc(text)}</p>" for text in [city["paragraph_1"], city["paragraph_2"]] if str(text).strip())
    faqs = "".join(
        f'<details><summary>{esc(question)}</summary><p>{esc(answer)}</p></details>'
        for question, answer in faq_items
    )
    featured_pool = [profile for profile in indexable_subset if profile.get("home_featured") == "是"] or indexable_subset[:3]
    featured_links = "".join(
        f'<a href="{site_href("../", profile["path"])}"><span>精选推荐</span><b>{esc(profile["name"])}</b><small>{esc(profile["tag"])}风格 · 查看独立详情</small></a>'
        for profile in featured_pool[:3]
    )
    featured_section = ""
    if featured_links:
        featured_section = f'''<section class="city-featured"><div class="wrap"><div class="section-head"><div><span class="kicker">{esc(city['featured_kicker'])}</span><h2>{esc(city['featured_title'])}</h2></div><p>{esc(city['featured_description'])}</p></div><div class="city-featured-links">{featured_links}</div></div></section>'''
    other_cities = "".join(
        f'<a href="{site_href("../", other["slug"])}">浏览{other["name"]}资源库 <span aria-hidden="true">→</span></a>'
        for other in CITIES if other["slug"] != city["slug"]
    )
    updated = f'<time class="content-updated" datetime="{esc(city.get("last_updated", ""))}">最后更新：{esc(city.get("last_updated", ""))}</time>' if city.get("last_updated") else ""
    body = f"""
<section class="city-hero"><div class="wrap"><div class="breadcrumbs"><a href="{site_href('../')}">{esc(HOME_CONTENT['nav_home_label'])}</a><span>/</span><span>{esc(city['name'])}资源库</span></div><span class="kicker">{esc(city['hero_kicker'])}</span><h1>{esc(city['hero_title'])}</h1><p>{esc(city['intro'])}</p>{updated}</div></section>
<section class="city-editorial"><div class="wrap city-editorial-grid"><div class="city-copy"><span class="kicker">{esc(city['editorial_kicker'])}</span><h2>{esc(city['editorial_title'])}</h2>{paragraphs}</div><div class="city-highlights">{highlights}</div></div></section>
{featured_section}
<section class="section city-all"><div class="wrap"><div class="section-head"><div><span class="kicker">{esc(city['all_kicker'])}</span><h2>{esc(city['all_title'])}</h2></div></div><div class="profile-grid">{cards}</div></div></section>
<section class="city-faq"><div class="wrap faq-grid"><div><span class="kicker">{esc(city['faq_kicker'])}</span><h2>{esc(city['faq_title'])}</h2><p>{esc(city['faq_description'])}</p></div><div class="faq-list">{faqs}</div></div></section>
<section class="city-crosslinks"><div class="wrap"><span class="kicker">{esc(city['more_kicker'])}</span><h2>{esc(city['more_title'])}</h2><div>{other_cities}</div></div></section>"""
    schema = json.dumps({
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "CollectionPage", "name": city["hero_title"], "description": city["seo_description"], "url": f"{DOMAIN}/{city['slug']}/"},
            {"@type": "ItemList", "name": f"{city['name']}资料列表", "numberOfItems": len(indexable_subset), "itemListElement": [{"@type": "ListItem", "position": idx, "name": p["name"], "url": f"{DOMAIN}/{p['path']}"} for idx, p in enumerate(indexable_subset, start=1)]},
            {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq_items]},
            {"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "首页", "item": HOME_URL}, {"@type": "ListItem", "position": 2, "name": f"{city['name']}资源库", "item": f"{DOMAIN}/{city['slug']}/"}]},
        ],
    }, ensure_ascii=False)
    return page(city["seo_title"], city["seo_description"], f"{DOMAIN}/{city['slug']}/", 1, body, f'<script type="application/ld+json">{schema}</script>', indexable=is_indexable(city))


def build_profile(profile: dict) -> str:
    prefix = "../../"
    related_pool = [p for p in PROFILES if p["path"] != profile["path"]]
    thumbs = "".join(
        f'<button class="thumb{" active" if i == 1 else ""}" type="button" data-gallery-thumb aria-label="查看{MEDIA_LABELS[i]}">{media_placeholder(prefix, profile, i)}</button>'
        for i in range(1, 4)
    )
    image_records = available_profile_images(profile)
    image_urls = [url for _, url, _, _ in image_records]
    video_source = profile_video_source(profile)
    body_paragraphs = "".join(
        f"<p>{esc(text)}</p>"
        for text in [profile.get("body_1", ""), profile.get("body_2", ""), profile.get("body_3", "")]
        if str(text).strip()
    )
    updated_parts = []
    if profile.get("first_published"):
        updated_parts.append(f'<time datetime="{esc(profile["first_published"])}">首次发布：{esc(profile["first_published"])}</time>')
    if profile.get("last_updated"):
        updated_parts.append(f'<time datetime="{esc(profile["last_updated"])}">最后更新：{esc(profile["last_updated"])}</time>')
    date_meta = f'<div class="content-dates">{"".join(updated_parts)}</div>' if updated_parts else ""
    video_section = ""
    if video_source:
        poster = profile_video_poster(profile)
        video_title = profile.get("video_title") or f"{profile['name']}资料视频"
        video_description = profile.get("video_description") or f"{profile['name']}相关视频资料。"
        video_section = f'''<section class="video-section"><div class="wrap"><div class="section-head"><div><span class="kicker">PROFILE VIDEO</span><h2>{esc(video_title)}</h2></div><p>{esc(video_description)}</p></div><div class="video-frame"><video controls preload="metadata" poster="{prefix}{esc(poster)}"><source src="{prefix}{esc(video_source)}" type="video/mp4"></video></div></div></section>'''
    related_footer = f'<div class="related-return"><a href="{site_href(prefix, profile["city_slug"])}">查看{esc(profile["city"])}全部资料 <span aria-hidden="true">→</span></a><a href="{site_href(prefix)}">返回顶奢首页 <span aria-hidden="true">→</span></a></div>'
    related_section = random_profile_section(
        f'profile-related-{profile["path"]}',
        related_pool,
        prefix,
        6,
        "YOU MAY ALSO LIKE",
        "随机资料推荐",
        "每次打开页面都会从不同城市随机展示更多资料入口。",
        extra_class="profile-random",
        footer_links=related_footer,
    )
    review_label = "内容已完成" if profile.get("content_review") == "已完成" else "资料整理中"
    body = f"""
<div class="wrap breadcrumbs detail-crumb"><a href="{site_href(prefix)}">首页</a><span>/</span><a href="{site_href(prefix, profile['city_slug'])}">{profile['city']}资源库</a><span>/</span><span>{profile['name']}</span></div>
<section class="detail wrap">
  <div class="gallery" data-gallery><figure class="gallery-main">{media_placeholder(prefix, profile, 1, 'main-photo', eager=True)}<figcaption>{esc(media_caption(profile, 1))}</figcaption></figure><div class="thumb-row">{thumbs}</div></div>
  <article class="detail-copy"><span class="kicker">{profile['city']} · CURATED PROFILE</span><h1>{profile['name']}</h1><p class="lead">{profile['summary']}</p><div class="facts"><div><span>城市</span><b>{profile['city']}</b></div><div><span>风格</span><b>{profile['tag']}</b></div><div><span>媒体</span><b>{profile_media_label(profile)}</b></div><div><span>状态</span><b>{review_label}</b></div></div>{date_meta}<p>{profile['intro']}</p><a class="back-city-link" href="{site_href(prefix, profile['city_slug'])}">返回{profile['city']}资源库查看全部资料 <span aria-hidden="true">→</span></a><button class="consult detail-consult" data-chat-open type="button"><span class="button-logo" aria-hidden="true"><img src="{prefix}assets/brand-logo.svg" alt=""></span><span class="button-copy"><b>立即咨询</b><small>PRIVATE CONCIERGE</small></span><span class="button-arrow" aria-hidden="true">↗</span></button></article>
</section>
{video_section}
<section class="content-section"><div class="wrap narrow"><span class="kicker">PROFILE NOTE</span><h2>{profile['name']}独立介绍</h2>{body_paragraphs}<p>继续浏览<a href="{site_href(prefix, profile['city_slug'])}">{profile['city']}精选资料与城市资源库</a>，或查看下方相关推荐。</p></div></section>
{related_section}"""
    page_schema = {"@type": "WebPage", "name": profile["name"], "description": profile["seo_description"], "url": f"{DOMAIN}/{profile['path']}"}
    if image_urls:
        page_schema["primaryImageOfPage"] = {"@type": "ImageObject", "url": image_urls[0]}
    if profile.get("first_published"):
        page_schema["datePublished"] = profile["first_published"]
    if profile.get("last_updated"):
        page_schema["dateModified"] = profile["last_updated"]
    graph = [page_schema, {"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "首页", "item": HOME_URL}, {"@type": "ListItem", "position": 2, "name": f"{profile['city']}资源库", "item": f"{DOMAIN}/{profile['city_slug']}/"}, {"@type": "ListItem", "position": 3, "name": profile["name"], "item": f"{DOMAIN}/{profile['path']}"}]}]
    if video_source:
        poster_url = f"{DOMAIN}/{profile_video_poster(profile)}"
        video_schema = {
            "@type": "VideoObject",
            "name": profile.get("video_title") or f"{profile['name']}资料视频",
            "description": profile.get("video_description") or f"{profile['name']}相关视频资料。",
            "thumbnailUrl": poster_url,
            "contentUrl": f"{DOMAIN}/{video_source}",
        }
        if profile.get("video_upload_date"):
            video_schema["uploadDate"] = profile["video_upload_date"]
        if profile.get("video_duration"):
            video_schema["duration"] = profile["video_duration"]
        graph.append(video_schema)
    schema = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False)
    return page(profile["seo_title"], profile["seo_description"], f"{DOMAIN}/{profile['path']}", 2, body, f'<script type="application/ld+json">{schema}</script>', indexable=is_indexable(profile))


def fixed_body(kind: str) -> tuple[str, str, str, str]:
    data = {
        "about": ("关于我们", "关于顶奢", "了解顶奢五城资料库的内容结构、更新方式与浏览路径。"),
        "contact": ("联系我们", "联系顶奢", "通过顶奢专属在线客服咨询城市资料、页面内容与网站使用问题。"),
        "privacy": ("隐私政策", "隐私政策", "了解顶奢网站可能处理的信息、使用目的、第三方服务与访问者选择。"),
        "terms": ("服务条款", "服务条款", "了解访问和使用顶奢网站时适用的内容说明与使用规则。"),
    }
    title, h1, description = data[kind]
    if kind == "contact":
        body = f'''<section class="legal-hero contact-hero"><div class="wrap narrow"><span class="kicker">CONTACT · DINGSHE</span><h1>{h1}</h1><p>{description}</p></div></section><section class="contact-page"><div class="wrap contact-layout"><div class="contact-intro"><span class="kicker">PRIVATE CONCIERGE</span><h2>专属沟通入口</h2><p>需要了解城市资料、页面内容或其他信息时，可直接打开在线客服。客服入口已接入顶奢专属客服，并会在当前页面打开沟通窗口。</p><div class="contact-points"><span>上海</span><span>广州</span><span>深圳</span><span>北京</span><span>杭州</span></div><div class="contact-details"><a href="mailto:{CONTACT_EMAIL}"><span>OFFICIAL EMAIL · 官方邮箱</span><b>{CONTACT_EMAIL}</b></a><div><span>OFFICE ADDRESS · 地址</span><address>{CONTACT_ADDRESS}</address></div></div><p class="contact-legal">开始咨询前，你也可以查看我们的<a href="../privacy/">隐私政策</a>与<a href="../terms/">服务条款</a>。</p></div><div class="contact-card"><img src="../assets/brand-logo.svg" alt="顶奢 DS 专属服务标识" width="92" height="92"><span class="contact-card-en">DINGSHE PRIVATE SERVICE</span><h2>在线客服</h2><p>点击下方按钮，在当前页面打开专属客服窗口。</p><button class="consult detail-consult contact-consult" data-chat-open type="button"><span class="button-logo" aria-hidden="true"><img src="../assets/brand-logo.svg" alt=""></span><span class="button-copy"><b>开始咨询</b><small>PRIVATE CONCIERGE</small></span><span class="button-arrow" aria-hidden="true">↗</span></button></div></div></section>'''
        return title, h1, description, body
    if kind == "about":
        city_links = "".join(
            f'<a href="../{city["slug"]}/"><b>{city["name"]}资源库</b><small>{city["line"]}</small></a>'
            for city in CITIES
        )
        body = f'''<section class="legal-hero"><div class="wrap narrow"><span class="kicker">ABOUT · DINGSHE</span><h1>{h1}</h1><p>{description}</p></div></section>
<section class="policy-page about-page"><div class="wrap policy-layout"><aside class="policy-index"><span>ABOUT US</span><a href="#mission">网站定位</a><a href="#cities">五城入口</a><a href="#standards">内容标准</a></aside><div class="policy-content">
<section id="mission" class="policy-card policy-lead"><span class="kicker">OUR PURPOSE</span><h2>让每套资料拥有清晰、可持续的页面</h2><p>顶奢是一个按城市组织的资料展示站，首批覆盖上海、广州、深圳、北京和杭州。我们以“首页—城市资源库—独立详情页”的结构整理内容，让访问者能够快速定位城市，也让每套资料拥有稳定网址、独立图片说明和持续更新空间。</p><p>城市页负责介绍本地内容与提供完整入口；详情页承载三张图片、一个视频、资料说明和相关推荐。后续增加资料时，现有页面路径不会被打乱。</p></section>
<section id="cities" class="policy-card"><span class="kicker">CITY DIRECTORY</span><h2>从五座城市开始浏览</h2><div class="about-city-links">{city_links}</div></section>
<section id="standards" class="policy-card"><span class="kicker">CONTENT PRINCIPLES</span><h2>我们的内容标准</h2><div class="policy-points"><article><b>独立呈现</b><p>为每套资料提供独立标题、介绍、媒体说明与详情网址。</p></article><article><b>图文一致</b><p>图片替代文字、主图说明和附近正文围绕同一页面主题编写。</p></article><article><b>清晰互联</b><p>通过城市回链、相关推荐和有意义的锚文本连接重要页面。</p></article></div><p class="policy-next">如需了解具体页面，可前往<a href="../contact/">联系我们</a>。</p></section>
</div></div></section>'''
        return title, h1, description, body
    if kind == "privacy":
        body = f'''<section class="legal-hero"><div class="wrap narrow"><span class="kicker">PRIVACY · DINGSHE</span><h1>{h1}</h1><p>{description}</p><small class="policy-date">更新日期：2026 年 9 月 22 日</small></div></section>
<section class="policy-page"><div class="wrap policy-layout"><aside class="policy-index"><span>PRIVACY</span><a href="#collect">信息范围</a><a href="#use">使用目的</a><a href="#cookies">Cookie 与分析</a><a href="#services">第三方服务</a><a href="#choices">你的选择</a></aside><div class="policy-content">
<section id="collect" class="policy-card"><h2>1. 我们可能处理的信息</h2><p>访问网站时，服务器及分析工具可能记录浏览器类型、设备类型、访问页面、来源页面、访问时间和近似地区等技术信息。你主动使用在线客服时，我们还会处理你在对话中自愿提供的内容。</p><p>请不要在咨询中提交与问题无关的敏感个人信息。</p></section>
<section id="use" class="policy-card"><h2>2. 信息的使用目的</h2><p>相关信息用于运行和保护网站、理解页面使用情况、改进城市资料与导航体验，以及回复你主动发起的咨询。我们不会把在线沟通内容用于与上述目的无关的公开展示。</p></section>
<section id="cookies" class="policy-card"><h2>3. Cookie 与访问分析</h2><p>网站可能使用 Cookie 或类似技术维持基础功能并统计访问情况，包括 Google Analytics 4。你可以通过浏览器设置限制或清除 Cookie；这样做可能影响部分功能或统计的准确性。</p></section>
<section id="services" class="policy-card"><h2>4. 第三方服务</h2><p>网站接入在线客服、访问分析及搜索发现服务。相应服务加载时，服务提供方可能按照其自身规则处理必要的技术信息。我们会根据实际使用情况调整这些接入，并尽量只保留网站运营所需的服务。</p></section>
<section class="policy-card"><h2>5. 保存与安全</h2><p>我们会在实现运营、回复咨询、安全审计或履行必要义务所需的期限内保存相关信息，并采取合理措施减少未经授权的访问、泄露或滥用风险。互联网传输无法保证绝对安全。</p></section>
<section id="choices" class="policy-card"><h2>6. 你的选择与联系我们</h2><p>你可以不提交在线咨询，也可以通过浏览器管理 Cookie。若对本政策或已提交的信息有疑问，请通过<a href="../contact/">联系我们页面</a>发起咨询，或发送邮件至 <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a>。</p><p>本政策可能随网站功能或服务接入变化而更新；重大调整会在本页体现，并更新页面日期。</p></section>
</div></div></section>'''
        return title, h1, description, body
    body = f'''<section class="legal-hero"><div class="wrap narrow"><span class="kicker">TERMS · DINGSHE</span><h1>{h1}</h1><p>{description}</p><small class="policy-date">更新日期：2026 年 9 月 22 日</small></div></section>
<section class="policy-page"><div class="wrap policy-layout"><aside class="policy-index"><span>TERMS</span><a href="#purpose">网站用途</a><a href="#conduct">使用规则</a><a href="#content">内容与媒体</a><a href="#third-party">第三方服务</a><a href="#changes">更新与联系</a></aside><div class="policy-content">
<section id="purpose" class="policy-card"><h2>1. 网站用途</h2><p>顶奢用于展示按城市整理的资料、图片、视频位置及相关介绍。页面信息用于浏览和沟通参考；如需确认具体内容，请通过官方在线客服进一步了解。</p></section>
<section id="conduct" class="policy-card"><h2>2. 合理使用</h2><p>访问者不得利用网站从事违法活动、破坏网站安全、干扰正常服务、批量抓取受限制内容，或冒用他人身份发起沟通。我们可以对明显影响网站安全或正常运行的访问采取限制措施。</p></section>
<section id="content" class="policy-card"><h2>3. 页面内容与媒体</h2><p>网站的版式、文字、品牌标识及依法享有权利的媒体内容受相应法律保护。除非取得授权，不应擅自复制、重新发布或将内容用于误导性用途。若你认为某项内容涉及权利问题，请通过联系我们页面提供具体网址与说明。</p></section>
<section id="third-party" class="policy-card"><h2>4. 第三方功能与链接</h2><p>在线客服、访问分析或外部链接可能由第三方提供，其可用性和数据处理规则由相应服务方负责。我们会维护站内入口，但不能保证所有第三方服务始终不中断。</p></section>
<section class="policy-card"><h2>5. 信息准确性与服务变更</h2><p>我们会持续维护页面，但展示内容可能随资料更新而变化。网站按当前可用状态提供，不对临时中断、第三方故障或访问者基于过期页面信息作出的决定作不适当保证。</p></section>
<section id="changes" class="policy-card"><h2>6. 条款更新与联系</h2><p>本条款可能随网站结构、服务方式或适用要求调整而更新。继续使用网站前，可再次查看本页。若有疑问，请前往<a href="../contact/">联系我们</a>；有关信息处理的说明请查看<a href="../privacy/">隐私政策</a>。</p></section>
</div></div></section>'''
    return title, h1, description, body


def editable_fixed_body(kind: str) -> tuple[str, str, str]:
    data = FIXED_PAGES[kind]
    if kind == "contact":
        city_points = "".join(f"<span>{esc(city['name'])}</span>" for city in CITIES)
        body = f'''<section class="legal-hero contact-hero"><div class="wrap narrow"><span class="kicker">{esc(data['hero_kicker'])}</span><h1>{esc(data['hero_title'])}</h1><p>{esc(data['hero_description'])}</p></div></section><section class="contact-page"><div class="wrap contact-layout"><div class="contact-intro"><span class="kicker">{esc(data['intro_kicker'])}</span><h2>{esc(data['intro_title'])}</h2><p>{esc(data['intro_text'])}</p><div class="contact-points">{city_points}</div><div class="contact-details"><a href="mailto:{esc(CONTACT_EMAIL)}"><span>{esc(data['email_label'])}</span><b>{esc(CONTACT_EMAIL)}</b></a><div><span>{esc(data['address_label'])}</span><address>{esc(CONTACT_ADDRESS)}</address></div></div><p class="contact-legal">{esc(data['legal_text'])}</p></div><div class="contact-card"><img src="../assets/brand-logo.svg" alt="{esc(BRAND)} DS 专属服务标识" width="92" height="92"><span class="contact-card-en">{esc(data['card_kicker'])}</span><h2>{esc(data['card_title'])}</h2><p>{esc(data['card_text'])}</p><button class="consult detail-consult contact-consult" data-chat-open type="button"><span class="button-logo" aria-hidden="true"><img src="../assets/brand-logo.svg" alt=""></span><span class="button-copy"><b>{esc(data['button_title'])}</b><small>{esc(data['button_subtitle'])}</small></span><span class="button-arrow" aria-hidden="true">↗</span></button></div></div></section>'''
        return data["seo_title"], data["seo_description"], body

    if kind == "about":
        city_links = "".join(
            f'<a href="{site_href("../", city["slug"])}"><b>{esc(city["name"])}资源库</b><small>{esc(city["line"])}</small></a>'
            for city in CITIES
        )
        body = f'''<section class="legal-hero"><div class="wrap narrow"><span class="kicker">{esc(data['hero_kicker'])}</span><h1>{esc(data['hero_title'])}</h1><p>{esc(data['hero_description'])}</p></div></section>
<section class="policy-page about-page"><div class="wrap policy-layout"><aside class="policy-index"><span>{esc(data['sidebar_title'])}</span><a href="#mission">{esc(data['sidebar_1'])}</a><a href="#cities">{esc(data['sidebar_2'])}</a><a href="#standards">{esc(data['sidebar_3'])}</a></aside><div class="policy-content">
<section id="mission" class="policy-card policy-lead"><span class="kicker">{esc(data['section_1_kicker'])}</span><h2>{esc(data['section_1_title'])}</h2><p>{esc(data['section_1_body_1'])}</p><p>{esc(data['section_1_body_2'])}</p></section>
<section id="cities" class="policy-card"><span class="kicker">{esc(data['section_2_kicker'])}</span><h2>{esc(data['section_2_title'])}</h2><div class="about-city-links">{city_links}</div></section>
<section id="standards" class="policy-card"><span class="kicker">{esc(data['section_3_kicker'])}</span><h2>{esc(data['section_3_title'])}</h2><div class="policy-points"><article><b>{esc(data['point_1_title'])}</b><p>{esc(data['point_1_text'])}</p></article><article><b>{esc(data['point_2_title'])}</b><p>{esc(data['point_2_text'])}</p></article><article><b>{esc(data['point_3_title'])}</b><p>{esc(data['point_3_text'])}</p></article></div><p class="policy-next">{esc(data['closing_text'])}</p></section>
</div></div></section>'''
        return data["seo_title"], data["seo_description"], body

    anchor_ids = {
        "privacy": ["collect", "use", "cookies", "services", "security", "choices"],
        "terms": ["purpose", "conduct", "content", "third-party", "accuracy", "changes"],
    }[kind]
    sidebar_links = "".join(
        f'<a href="#{anchor}">{esc(data[f"sidebar_{index}"])}</a>'
        for index, anchor in enumerate(anchor_ids, start=1)
    )
    sections = []
    for index, anchor in enumerate(anchor_ids, start=1):
        paragraphs = "".join(
            f"<p>{esc(data.get(f'section_{index}_body_{body_index}', ''))}</p>"
            for body_index in (1, 2)
            if str(data.get(f"section_{index}_body_{body_index}", "")).strip()
        )
        sections.append(f'<section id="{anchor}" class="policy-card"><h2>{esc(data[f"section_{index}_title"])}</h2>{paragraphs}</section>')
    body = f'''<section class="legal-hero"><div class="wrap narrow"><span class="kicker">{esc(data['hero_kicker'])}</span><h1>{esc(data['hero_title'])}</h1><p>{esc(data['hero_description'])}</p><small class="policy-date">{esc(data['updated_date'])}</small></div></section>
<section class="policy-page"><div class="wrap policy-layout"><aside class="policy-index"><span>{esc(data['sidebar_title'])}</span>{sidebar_links}</aside><div class="policy-content">{"".join(sections)}</div></div></section>'''
    return data["seo_title"], data["seo_description"], body


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def load_json(path: Path, default: object) -> object:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def prior_page_state() -> dict[str, dict]:
    state = load_json(SEO_STATE_PATH, {})
    if isinstance(state, dict) and isinstance(state.get("pages"), dict):
        return state["pages"]
    previous: dict[str, dict] = {}
    old_sitemap = DIST / "sitemap.xml"
    if old_sitemap.exists():
        xml = old_sitemap.read_text(encoding="utf-8")
        for block in re.findall(r"<url>(.*?)</url>", xml, flags=re.S):
            loc = re.search(r"<loc>(.*?)</loc>", block, flags=re.S)
            lastmod = re.search(r"<lastmod>(.*?)</lastmod>", block, flags=re.S)
            if loc:
                previous[html.unescape(loc.group(1).strip())] = {
                    "hash": "",
                    "lastmod": lastmod.group(1).strip() if lastmod else date.today().isoformat(),
                    "indexable": True,
                }
    return previous


def file_digest(hasher: object, source: Path) -> None:
    if not source.exists() or not source.is_file():
        return
    hasher.update(str(source.relative_to(ROOT)).encode("utf-8"))
    with source.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)


def page_digest(content: str, assets: list[Path]) -> str:
    hasher = hashlib.sha256(content.encode("utf-8"))
    for asset in sorted(assets, key=lambda path: str(path)):
        file_digest(hasher, asset)
    return hasher.hexdigest()


def profile_assets(profile: dict, *, first_only: bool = False) -> list[Path]:
    assets: list[Path] = []
    slots = (1,) if first_only else (1, 2, 3)
    for slot in slots:
        source = existing_profile_image_source(profile, slot)
        if source:
            assets.append(ROOT / source)
    if not first_only and profile_video_source(profile):
        assets.append(ROOT / profile["media_dir"] / "profile.mp4")
    return assets


def optimize_image(source: Path, destination: Path, width: int, quality: int = 82) -> None:
    from PIL import Image, ImageOps

    destination.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as original:
        image = ImageOps.exif_transpose(original)
        if image.width > width:
            height = max(1, round(image.height * width / image.width))
            image = image.resize((width, height), Image.Resampling.LANCZOS)
        if image.mode not in ("RGB", "RGBA"):
            image = image.convert("RGBA" if "transparency" in image.info else "RGB")
        image.save(destination, "WEBP", quality=quality, method=6)


def prepare_responsive_images() -> None:
    hero = ROOT / "assets" / "hero-city.png"
    for width in (640, 1200, 1680):
        optimize_image(hero, DIST / "assets" / f"hero-city-{width}.webp", width, 82)
    for profile in PROFILES:
        for slot in range(1, 4):
            source_path = existing_profile_image_source(profile, slot)
            if not source_path:
                continue
            source = ROOT / source_path
            for width in (480, 800):
                optimize_image(source, DIST / profile["media_dir"] / f"{slot:02d}-{width}.webp", width, 82)


def build() -> None:
    previous_state = prior_page_state()
    if DIST.exists():
        shutil.rmtree(DIST)
    (DIST / "assets").mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / "assets" / "hero-city.png", DIST / "assets" / "hero-city.png")
    for name in ["style.css", "site.js", "favicon.svg", "brand-logo.svg", "profile-placeholder-1.svg", "profile-placeholder-2.svg", "profile-placeholder-3.svg", "video-poster.svg"]:
        shutil.copy2(ROOT / "assets" / name, DIST / "assets" / name)
    if MEDIA_SOURCE.exists():
        shutil.copytree(MEDIA_SOURCE, DIST / "photos", dirs_exist_ok=True)
    else:
        (DIST / "photos").mkdir(parents=True, exist_ok=True)
    prepare_responsive_images()
    if VERIFICATION_SOURCE.exists():
        for verification_file in VERIFICATION_SOURCE.iterdir():
            if verification_file.is_file() and verification_file.name != "README.txt":
                shutil.copy2(verification_file, DIST / verification_file.name)
    pages: dict[str, dict] = {}

    def add_page(url: str, output: Path, content: str, *, indexable: bool, assets: list[Path] | None = None) -> None:
        pages[url] = {
            "path": output,
            "content": content,
            "indexable": indexable,
            "assets": assets or [],
        }

    home_featured_assets = [asset for profile in INDEXABLE_PROFILES if profile.get("home_featured") == "是" for asset in profile_assets(profile, first_only=True)]
    add_page(HOME_URL, DIST / "index.html", build_home(), indexable=True, assets=[ROOT / "assets" / "hero-city.png", *home_featured_assets])
    for city in CITIES:
        city_profiles = [profile for profile in PROFILES if profile["city_slug"] == city["slug"]]
        add_page(
            f"{DOMAIN}/{city['slug']}/",
            DIST / city["slug"] / "index.html",
            build_city(city),
            indexable=is_indexable(city),
            assets=[asset for profile in city_profiles for asset in profile_assets(profile, first_only=True)],
        )
    for profile in PROFILES:
        add_page(
            f"{DOMAIN}/{profile['path']}",
            DIST / profile["path"] / "index.html",
            build_profile(profile),
            indexable=is_indexable(profile),
            assets=profile_assets(profile),
        )
    for kind in ["about", "contact", "privacy", "terms"]:
        title, description, body = editable_fixed_body(kind)
        url = f"{DOMAIN}/{kind}/"
        add_page(url, DIST / kind / "index.html", page(title, description, url, 1, body), indexable=True)

    today = date.today().isoformat()
    new_state: dict[str, dict] = {}
    changed_urls: set[str] = set()
    for url, record in pages.items():
        digest = page_digest(record["content"], record["assets"])
        previous = previous_state.get(url, {})
        changed = previous.get("hash") != digest
        lastmod = today if changed else previous.get("lastmod", today)
        indexable = bool(record["indexable"])
        if indexable and (changed or not previous.get("indexable", False)):
            changed_urls.add(url)
        if previous.get("indexable", False) and not indexable:
            changed_urls.add(url)
        new_state[url] = {"hash": digest, "lastmod": lastmod, "indexable": indexable}
        write(record["path"], record["content"])

    for url, previous in previous_state.items():
        if url not in pages and previous.get("indexable", False):
            changed_urls.add(url)

    pending_data = load_json(INDEXNOW_PENDING_PATH, {})
    if isinstance(pending_data, dict):
        changed_urls.update(url for url in pending_data.get("urls", []) if isinstance(url, str))
    write(SEO_STATE_PATH, json.dumps({"generated_at": today, "pages": new_state}, ensure_ascii=False, indent=2) + "\n")
    write(INDEXNOW_PENDING_PATH, json.dumps({"generated_at": today, "urls": sorted(changed_urls)}, ensure_ascii=False, indent=2) + "\n")

    sitemap_urls = [url for url, record in pages.items() if record["indexable"]]
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(
        f"  <url><loc>{xml_escape(url)}</loc><lastmod>{xml_escape(new_state[url]['lastmod'])}</lastmod></url>"
        for url in sitemap_urls
    ) + "\n</urlset>\n"
    write(DIST / "sitemap.xml", sitemap)
    image_pages: list[tuple[str, list[tuple[str, str, str]]]] = [
        (HOME_URL, [(f"{DOMAIN}/assets/hero-city-1680.webp", HOME_CONTENT["hero_image_alt"], HOME_CONTENT["hero_image_title"])])
    ]
    for profile in INDEXABLE_PROFILES:
        images = [(url, caption, f"{profile['name']}{MEDIA_LABELS[slot]}") for slot, url, _, caption in available_profile_images(profile)]
        if images:
            image_pages.append((f"{DOMAIN}/{profile['path']}", images))
    image_entries = []
    for page_url, images in image_pages:
        image_nodes = "".join(
            f"<image:image><image:loc>{xml_escape(url)}</image:loc><image:caption>{xml_escape(caption)}</image:caption><image:title>{xml_escape(title)}</image:title></image:image>"
            for url, caption, title in images
        )
        image_entries.append(f"  <url><loc>{xml_escape(page_url)}</loc>{image_nodes}</url>")
    image_sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n' + "\n".join(image_entries) + "\n</urlset>\n"
    write(DIST / "image-sitemap.xml", image_sitemap)
    write(DIST / "robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {DOMAIN}/sitemap.xml\nSitemap: {DOMAIN}/image-sitemap.xml\n")
    write(DIST / "CNAME", "hqq2.com\n")
    write(DIST / "photos" / "README.txt", "媒体文件命名说明\n\n请将文件放入项目根目录 photos 下的对应目录，例如 photos/shanghai-model-001。\n照片命名：01.jpg、02.jpg、03.jpg（也支持 jpeg、png、webp、avif）。\n视频命名：profile.mp4（可选）。有视频时请在工作表填写标题、描述、上传日期和时长。\n重新构建后，真实图片会生成响应式 WebP，并在资料允许收录后进入图片站点地图，无需手改 HTML。\n")
    write(ROOT / "profiles.json", json.dumps(ALL_PROFILES, ensure_ascii=False, indent=2) + "\n")
    not_found = FIXED_PAGES["not_found"]
    not_found_body = f'<section class="legal-hero"><div class="wrap narrow"><span class="kicker">{esc(not_found["hero_kicker"])}</span><h1>{esc(not_found["hero_title"])}</h1><p>{esc(not_found["hero_description"])}</p><p><a class="text-link" href="index.html">{esc(not_found["button_label"])} →</a></p></div></section>'
    write(DIST / "404.html", page(not_found["seo_title"], not_found["seo_description"], f"{DOMAIN}/404.html", 0, not_found_body, indexable=False))


if __name__ == "__main__":
    build()
