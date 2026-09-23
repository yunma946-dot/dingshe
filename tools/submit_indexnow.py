from __future__ import annotations

import argparse
import json
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PENDING_PATH = ROOT / "indexnow_pending.json"
DOMAIN = "hqq2.com"
KEY = "73fe7e61a18cb1678580f5a26ccab2a4"
KEY_LOCATION = f"https://{DOMAIN}/{KEY}.txt"
ENDPOINT = "https://api.indexnow.org/indexnow"


def sitemap_urls() -> list[str]:
    sitemap = ROOT / "dist" / "sitemap.xml"
    tree = ET.parse(sitemap)
    namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    return [node.text for node in tree.findall("s:url/s:loc", namespace) if node.text]


def pending_urls() -> list[str]:
    if not PENDING_PATH.exists():
        return []
    data = json.loads(PENDING_PATH.read_text(encoding="utf-8"))
    urls = data.get("urls", []) if isinstance(data, dict) else []
    return sorted({url for url in urls if isinstance(url, str) and url.startswith(f"https://{DOMAIN}/")})


def main() -> None:
    parser = argparse.ArgumentParser(description="提交顶奢网站 URL 到 IndexNow")
    parser.add_argument("--dry-run", action="store_true", help="只检查提交内容，不发送请求")
    parser.add_argument("--all", action="store_true", help="提交站点地图中的全部可收录网址")
    args = parser.parse_args()
    urls = sitemap_urls() if args.all else pending_urls()
    if not urls:
        print("没有需要提交的新增、修改或删除网址。")
        return
    payload = {
        "host": DOMAIN,
        "key": KEY,
        "keyLocation": KEY_LOCATION,
        "urlList": urls,
    }
    if args.dry_run:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    request = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        print(f"IndexNow submission status: {response.status}")
    if not args.all:
        PENDING_PATH.write_text(
            json.dumps({"generated_at": "submitted", "urls": []}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"已提交并清空待通知列表：{len(urls)} 个网址")


if __name__ == "__main__":
    main()
