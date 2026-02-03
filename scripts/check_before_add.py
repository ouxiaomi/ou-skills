#!/usr/bin/env python3
"""
新增技能前的Hash检查
在添加新技能前检查是否已存在相同的技能
"""

import os
import json
import hashlib
import sys
from pathlib import Path

def compute_file_hash(filepath):
    """计算文件的SHA-256 hash"""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()

def check_duplicate_skill(skill_path, repo_root):
    """检查技能是否重复"""
    hash_file = Path(repo_root) / ".skills-hash.json"

    if not hash_file.exists():
        print("⚠️  Hash索引文件不存在，无法检查重复")
        print("   运行 scripts/check_skill_hash.py 生成索引")
        return False

    with open(hash_file, "r", encoding="utf-8") as f:
        index = json.load(f)

    # 计算新技能的hash
    new_skill_path = Path(skill_path)
    if not new_skill_path.exists():
        print(f"❌ 技能文件不存在: {skill_path}")
        return False

    new_hash = compute_file_hash(skill_path)

    # 检查是否存在相同hash
    for path, info in index.get("skills", {}).items():
        if info["hash"] == new_hash:
            print(f"⚠️  发现重复技能!")
            print(f"   新技能: {skill_path}")
            print(f"   已存在: {path}")
            print(f"   Hash: {new_hash}")
            return True

    return False

def main():
    if len(sys.argv) < 2:
        print("用法: python3 scripts/check_before_add.py <SKILL.md路径>")
        print("示例: python3 scripts/check_before_add.py categories/code-analysis/my-skill/SKILL.md")
        sys.exit(1)

    skill_path = sys.argv[1]
    repo_root = Path(__file__).parent.parent

    print(f"🔍 检查技能: {skill_path}\n")

    is_duplicate = check_duplicate_skill(skill_path, repo_root)

    if is_duplicate:
        print("\n❌ 检测到重复技能，请确认是否继续")
        sys.exit(1)
    else:
        print("\n✅ 没有检测到重复，可以安全添加")
        sys.exit(0)

if __name__ == "__main__":
    main()
