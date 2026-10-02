#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path


START = "/* HQ_SITE1_SHARP_BUTTON_START */"
END = "/* HQ_SITE1_SHARP_BUTTON_END */"
BLOCK = r'''/* HQ_SITE1_SHARP_BUTTON_START */
        .hq-btn:not(.open){
          background-image:url("${origin}/assets/site1_widget_brand_button.svg?v=20260926d")!important;
          background-repeat:no-repeat!important;
          background-position:center!important;
          background-size:100% 100%!important;
          image-rendering:auto!important;
        }
        .hq-btn.open{
          width:58px!important;
          height:58px!important;
          background-image:none!important;
        }
        /* HQ_SITE1_SHARP_BUTTON_END */'''


def main() -> int:
    if len(sys.argv) != 2:
        print("用法：patch_widget.py /var/www/chat/widget.js")
        return 2

    path = Path(sys.argv[1])
    text = path.read_text(encoding="utf-8")

    # Remove the previous v3 marker first.  In v3 it may have been inserted
    # inside the .hq-btn declaration, which makes the nested rules invalid CSS.
    marker_pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
    cleaned = marker_pattern.sub("", text)

    # Find the site1 button rule by its existing PNG URL, then insert the SVG
    # override only after that rule's closing brace.  This keeps the new rules
    # at the top CSS level instead of nesting them inside .hq-btn { ... }.
    png_needle = "site1_widget_brand_button.png"
    png_pos = cleaned.find(png_needle)
    if png_pos < 0:
        print("错误：未找到前台1低清按钮图片规则，未修改 widget.js。")
        return 1

    rule_start = cleaned.rfind(".hq-btn{", 0, png_pos)
    if rule_start < 0:
        rule_start = cleaned.rfind(".hq-btn {", 0, png_pos)
    rule_end = cleaned.find("}", png_pos)
    if rule_start < 0 or rule_end < 0:
        print("错误：未找到前台1按钮样式的完整大括号，未修改 widget.js。")
        return 1

    updated = cleaned[: rule_end + 1] + "\n        " + BLOCK + cleaned[rule_end + 1 :]

    marker_pos = updated.find(START)
    if (
        marker_pos <= rule_end
        or START not in updated
        or "site1_widget_brand_button.svg?v=20260926d" not in updated
        or updated.count(START) != 1
        or updated.count(END) != 1
    ):
        print("错误：高清按钮补丁校验失败，未保存。")
        return 1

    path.write_text(updated, encoding="utf-8", newline="\n")
    print("widget.js 高清SVG按钮补丁已写入（CSS位置已纠正）。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
