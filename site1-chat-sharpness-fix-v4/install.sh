#!/usr/bin/env bash
set -euo pipefail

CHAT_ROOT="/var/www/chat"
WIDGET_FILE="$CHAT_ROOT/widget.js"
ASSET_DIR="$CHAT_ROOT/assets"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_DIR="/root/site1-chat-sharp-button-backup-$STAMP"

if [[ ! -f "$WIDGET_FILE" ]]; then
  echo "错误：未找到 $WIDGET_FILE"
  exit 1
fi

mkdir -p "$BACKUP_DIR"
cp -a "$WIDGET_FILE" "$BACKUP_DIR/widget.js"
if [[ -f "$ASSET_DIR/site1_widget_brand_button.svg" ]]; then
  cp -a "$ASSET_DIR/site1_widget_brand_button.svg" "$BACKUP_DIR/site1_widget_brand_button.svg"
fi

mkdir -p "$ASSET_DIR"
install -m 0644 "$SCRIPT_DIR/site1_widget_brand_button.svg" "$ASSET_DIR/site1_widget_brand_button.svg"
python3 "$SCRIPT_DIR/patch_widget.py" "$WIDGET_FILE"

if command -v node >/dev/null 2>&1; then
  node --check "$WIDGET_FILE"
fi

echo
echo "前台1客服按钮清晰度修复成功（v4）。"
echo "低清PNG按钮已改为SVG矢量按钮，CSS位置已纠正；前台2、前台3不变。"
echo "备份目录：$BACKUP_DIR"
echo "网站客服代码缓存版本应为：v=20260926c"
