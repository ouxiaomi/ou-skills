#!/usr/bin/env python3
"""
技能Hash检查工具
用于检测重复的技能
"""

import os
import json
import hashlib
from pathlib import Path
from collections import defaultdict
from datetime import datetime

def compute_file_hash(filepath):
    """计算文件的SHA-256 hash"""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()

def scan_skills(repo_root):
    """扫描所有技能"""
    skills = {}
    categories_path = Path(repo_root) / "categories"

    if not categories_path.exists():
        print(f"❌ 分类目录不存在: {categories_path}")
        return skills

    for skill_md in categories_path.rglob("SKILL.md"):
        skill_path = str(skill_md.relative_to(repo_root))
        skill_dir = str(skill_md.parent.relative_to(repo_root))

        skill_hash = compute_file_hash(skill_md)

        skills[skill_path] = {
            "path": skill_path,
            "dir": skill_dir,
            "hash": skill_hash,
            "size": skill_md.stat().st_size,
            "modified": datetime.fromtimestamp(skill_md.stat().st_mtime).isoformat()
        }

    return skills

def check_duplicates(skills):
    """检查重复技能"""
    hash_map = defaultdict(list)

    for path, info in skills.items():
        hash_map[info["hash"]].append(info)

    # 找出有重复的hash
    duplicates = {h: v for h, v in hash_map.items() if len(v) > 1}
    return duplicates

def save_hash_index(repo_root, skills):
    """保存hash索引"""
    hash_file = Path(repo_root) / ".skills-hash.json"

    index = {
        "version": "1.0",
        "lastUpdated": datetime.now().isoformat(),
        "totalSkills": len(skills),
        "skills": {path: {
            "hash": info["hash"],
            "size": info["size"],
            "modified": info["modified"]
        } for path, info in skills.items()}
    }

    with open(hash_file, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)

    return hash_file

def main():
    import sys
    repo_root = Path(__file__).parent.parent

    print("🔍 扫描技能并计算hash...\n")

    skills = scan_skills(repo_root)

    if not skills:
        print("⚠️  没有找到任何技能")
        return

    print(f"✅ 找到 {len(skills)} 个技能:\n")

    for path, info in sorted(skills.items()):
        print(f"  📄 {path}")
        print(f"     Hash: {info['hash'][:16]}...")
        print(f"     大小: {info['size']} bytes\n")

    # 检查重复
    duplicates = check_duplicates(skills)

    if duplicates:
        print("⚠️  发现重复技能!\n")
        for h, skill_list in duplicates.items():
            print(f"  Hash: {h[:16]}... ({len(skill_list)} 个重复项)")
            for skill in skill_list:
                print(f"    - {skill['path']}")
        print()
    else:
        print("✅ 没有发现重复技能\n")

    # 保存索引
    hash_file = save_hash_index(repo_root, skills)
    print(f"💾 Hash索引已保存: {hash_file}")

    # 返回状态码（有重复返回1）
    sys.exit(1 if duplicates else 0)

if __name__ == "__main__":
    main()
