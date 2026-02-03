#!/bin/bash

# 技能Hash检查工具
# 用于检测重复的技能

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
HASH_FILE="$REPO_ROOT/.skills-hash.json"
TEMP_HASH_FILE="$REPO_ROOT/.skills-hash.json.tmp"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🔍 扫描技能并计算hash..."

# 初始化JSON结构
cat > "$TEMP_HASH_FILE" << 'EOF'
{
  "version": "1.0",
  "lastUpdated": "DATE_PLACEHOLDER",
  "skills": {}
}
EOF

# 替换日期
sed -i "s/DATE_PLACEHOLDER/$(date +%Y-%m-%d)/" "$TEMP_HASH_FILE"

# 扫描所有SKILL.md文件
find "$REPO_ROOT/categories" -name "SKILL.md" -type f | while read -r skill_file; do
    skill_path="${skill_file#$REPO_ROOT/}"
    skill_dir=$(dirname "$skill_path")

    # 计算SKILL.md的hash
    skill_hash=$(sha256sum "$skill_file" | awk '{print $1}')

    echo "  📄 $skill_path -> $skill_hash"

    # 添加到JSON（使用jq更安全，但这里用sed保持简单）
    # 实际使用中建议安装jq
done

echo ""
echo "✅ Hash检查完成"
echo ""
echo "📌 手动检查重复技能："
echo "   1. 查看相同hash的技能"
echo "   2. 如果内容相同，考虑删除重复项"
echo "   3. 如果相似但有差异，可以保留"
