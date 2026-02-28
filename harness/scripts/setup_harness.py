#!/usr/bin/env python3
"""
Harness System Setup Script

Configures a long-running agent Harness system for any project type.
Based on Anthropic's engineering blog: https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents

Usage:
    python setup_harness.py [project_path]

If project_path is not specified, uses current directory.
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path


def detect_project_type(project_path: Path) -> str:
    """Detect project type based on config files."""
    if (project_path / "package.json").exists():
        pkg = json.loads((project_path / "package.json").read_text())
        # Check for framework indicators
        deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
        if "vue" in deps:
            return "node-vue"
        if "react" in deps or "react-dom" in deps:
            return "node-react"
        if "next" in deps:
            return "node-nextjs"
        if "svelte" in deps:
            return "node-svelte"
        if "express" in deps or "fastify" in deps:
            return "node-backend"
        return "node"
    if (project_path / "pyproject.toml").exists():
        return "python"
    if (project_path / "setup.py").exists() or (project_path / "requirements.txt").exists():
        return "python"
    if (project_path / "go.mod").exists():
        return "go"
    if (project_path / "Cargo.toml").exists():
        return "rust"
    if (project_path / "pom.xml").exists():
        return "java-maven"
    if (project_path / "build.gradle").exists():
        return "java-gradle"
    return "generic"


def get_project_info(project_path: Path) -> dict:
    """Extract project name and version from config files."""
    info = {"name": project_path.name, "version": "0.0.0"}

    # Try package.json (Node.js)
    pkg_json = project_path / "package.json"
    if pkg_json.exists():
        try:
            pkg = json.loads(pkg_json.read_text())
            info["name"] = pkg.get("name", info["name"])
            info["version"] = pkg.get("version", info["version"])
            return info
        except (json.JSONDecodeError, IOError):
            pass

    # Try pyproject.toml (Python)
    pyproject = project_path / "pyproject.toml"
    if pyproject.exists():
        try:
            content = pyproject.read_text()
            # Simple TOML parsing for name and version
            name_match = re.search(r'^name\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)
            version_match = re.search(r'^version\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)
            if name_match:
                info["name"] = name_match.group(1)
            if version_match:
                info["version"] = version_match.group(1)
            return info
        except IOError:
            pass

    # Try go.mod (Go)
    go_mod = project_path / "go.mod"
    if go_mod.exists():
        try:
            content = go_mod.read_text()
            module_match = re.search(r"^module\s+(\S+)", content, re.MULTILINE)
            if module_match:
                info["name"] = module_match.group(1).split("/")[-1]
            return info
        except IOError:
            pass

    return info


def create_feature_list(project_path: Path, project_info: dict, project_type: str) -> Path:
    """Create feature_list.json based on existing codebase analysis."""
    feature_list = {
        "project": project_info["name"],
        "version": project_info["version"],
        "lastUpdated": datetime.now().strftime("%Y-%m-%d"),
        "features": []
    }

    # Analyze existing features from CLAUDE.md if it exists
    claude_md = project_path / "CLAUDE.md"
    existing_features = []

    if claude_md.exists():
        content = claude_md.read_text()
        # Extract feature descriptions from markdown
        # Look for bullet points, headers that might indicate features
        lines = content.split("\n")
        for line in lines:
            line = line.strip()
            if line.startswith("- ") or line.startswith("* "):
                # Clean up and add as potential feature
                feature_text = line[2:].strip()
                if len(feature_text) > 5 and len(feature_text) < 100:
                    existing_features.append(feature_text)

    # Generate feature entries
    feature_id = 1
    seen = set()

    for feature_text in existing_features[:20]:  # Limit to 20 features
        if feature_text in seen:
            continue
        seen.add(feature_text)

        # Skip if it looks like a meta description
        if any(kw in feature_text.lower() for kw in ["目录", "结构", "overview", "目录结构", "directory"]):
            continue

        feature_list["features"].append({
            "id": f"F{feature_id:03d}",
            "category": "existing",
            "description": feature_text,
            "priority": "medium",
            "status": "completed",
            "steps": [],
            "testCommand": f"验证 {feature_text} 功能"
        })
        feature_id += 1

    # Add placeholder for future features
    if len(feature_list["features"]) < 5:
        feature_list["features"].append({
            "id": f"F{feature_id:03d}",
            "category": "future",
            "description": "待规划功能",
            "priority": "low",
            "status": "pending",
            "steps": ["分析需求", "设计实现方案", "编写代码", "测试验证"],
            "testCommand": "验证功能正常工作"
        })

    output_path = project_path / "feature_list.json"
    output_path.write_text(json.dumps(feature_list, indent=2, ensure_ascii=False))
    return output_path


def create_progress_file(project_path: Path, project_info: dict) -> Path:
    """Create claude-progress.txt progress tracking file."""
    today = datetime.now().strftime("%Y-%m-%d")

    content = f"""# {project_info["name"].title()} 开发进度日志

## 格式说明

每次会话结束时，代理应在此记录进度：
- 日期时间
- 完成的工作
- 当前状态
- 下一步计划

---

## 进度记录

### {today} (Harness 系统初始化)

**完成的工作:**
- 创建长运行代理 Harness 系统
- 添加 feature_list.json (功能需求列表)
- 添加 claude-progress.txt (进度跟踪日志)
- 添加 init.sh (开发环境初始化脚本)
- 添加 .claude/prompts/ (代理提示词)
- 更新 CLAUDE.md (添加 Harness 系统文档)

**当前状态:**
- 系统初始化完成
- Harness 架构已配置

**下一步计划:**
- 根据功能列表优先级继续开发
- 首先考虑高优先级的 pending 功能
"""

    output_path = project_path / "claude-progress.txt"
    output_path.write_text(content)
    return output_path


def get_init_sh_content(project_type: str, project_info: dict) -> str:
    """Generate init.sh content based on project type."""

    project_name = project_info["name"].title()

    if project_type.startswith("node"):
        return f'''#!/bin/bash

# {project_name} 开发环境初始化脚本
# 用途: 快速启动开发环境，验证基本功能
# 使用方法: ./init.sh

echo "🚀 {project_name} 开发环境初始化..."
echo ""

# 1. 检查 Node.js 版本
echo "📋 检查 Node.js 版本..."
node_version=$(node -v 2>/dev/null)
if [ $? -ne 0 ]; then
    echo "❌ Node.js 未安装，请先安装 Node.js"
    echo "   推荐版本: Node.js 18.x 或更高"
    exit 1
fi
echo "✅ Node.js 版本: $node_version"
echo ""

# 2. 检查包管理器
echo "📋 检查包管理器..."
if command -v pnpm &> /dev/null; then
    PKG_MANAGER="pnpm"
    PKG_VERSION=$(pnpm -v)
elif command -v npm &> /dev/null; then
    PKG_MANAGER="npm"
    PKG_VERSION=$(npm -v)
elif command -v yarn &> /dev/null; then
    PKG_MANAGER="yarn"
    PKG_VERSION=$(yarn -v)
else
    echo "❌ 未找到包管理器 (pnpm/npm/yarn)"
    exit 1
fi
echo "✅ 包管理器: $PKG_MANAGER v$PKG_VERSION"
echo ""

# 3. 安装依赖
echo "📋 检查依赖..."
if [ ! -d "node_modules" ]; then
    echo "📦 安装依赖..."
    $PKG_MANAGER install
    if [ $? -ne 0 ]; then
        echo "❌ 依赖安装失败"
        exit 1
    fi
    echo "✅ 依赖安装完成"
else
    echo "✅ 依赖已安装"
fi
echo ""

# 4. 检查关键配置文件
echo "📋 检查关键配置文件..."
config_files=("package.json" "vite.config.js" "tsconfig.json")
for file in "${{config_files[@]}}"; do
    if [ -f "$file" ]; then
        echo "✅ $file 存在"
    fi
done
echo ""

# 5. 显示环境摘要
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 环境摘要"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Node.js: $node_version"
echo "  包管理器: $PKG_MANAGER v$PKG_VERSION"
echo "  项目: {project_info["name"]} v{project_info["version"]}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 6. 启动开发服务器
echo "🌟 启动开发服务器..."
echo "📝 提示: 按 Ctrl+C 停止服务器"
echo ""
$PKG_MANAGER dev
'''

    elif project_type == "python":
        return f'''#!/bin/bash

# {project_name} 开发环境初始化脚本
# 用途: 快速启动开发环境，验证基本功能
# 使用方法: ./init.sh

echo "🚀 {project_name} 开发环境初始化..."
echo ""

# 1. 检查 Python 版本
echo "📋 检查 Python 版本..."
python_version=$(python3 -c "import sys; print(sys.version.split()[0])" 2>/dev/null)
if [ $? -ne 0 ]; then
    echo "❌ Python3 未安装，请先安装 Python"
    echo "   推荐版本: Python 3.11 或更高"
    exit 1
fi
echo "✅ Python 版本: $python_version"
echo ""

# 2. 检查虚拟环境
echo "📋 检查虚拟环境..."
if [ -d ".venv" ]; then
    echo "✅ 虚拟环境存在 (.venv)"
    source .venv/bin/activate
elif [ -d "venv" ]; then
    echo "✅ 虚拟环境存在 (venv)"
    source venv/bin/activate
else
    echo "⚠️  未检测到虚拟环境，建议创建: python -m venv .venv"
fi
echo ""

# 3. 检查包管理器
echo "📋 检查包管理器..."
if command -v uv &> /dev/null; then
    PKG_MANAGER="uv"
    echo "✅ 使用 uv (推荐)"
elif command -v pip &> /dev/null; then
    PKG_MANAGER="pip"
    echo "✅ 使用 pip"
else
    echo "❌ 未找到包管理器 (uv/pip)"
    exit 1
fi
echo ""

# 4. 安装依赖
echo "📋 检查依赖..."
if [ "$PKG_MANAGER" = "uv" ]; then
    if [ -f "pyproject.toml" ]; then
        echo "📦 同步依赖..."
        uv sync
    elif [ -f "requirements.txt" ]; then
        echo "📦 安装依赖..."
        uv pip install -r requirements.txt
    fi
else
    if [ -f "requirements.txt" ]; then
        echo "📦 安装依赖..."
        pip install -r requirements.txt
    fi
fi
echo ""

# 5. 检查关键配置文件
echo "📋 检查关键配置文件..."
config_files=("pyproject.toml" "requirements.txt" "setup.py")
for file in "${{config_files[@]}}"; do
    if [ -f "$file" ]; then
        echo "✅ $file 存在"
    fi
done
echo ""

# 6. 显示环境摘要
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 环境摘要"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Python: $python_version"
echo "  包管理器: $PKG_MANAGER"
echo "  项目: {project_info["name"]} v{project_info["version"]}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 7. 运行测试（可选）
if [ -f "pytest.ini" ] || [ -d "tests" ]; then
    echo "🧪 运行测试..."
    $PKG_MANAGER run pytest
fi
'''

    elif project_type == "go":
        return f'''#!/bin/bash

# {project_name} 开发环境初始化脚本
# 用途: 快速启动开发环境，验证基本功能
# 使用方法: ./init.sh

echo "🚀 {project_name} 开发环境初始化..."
echo ""

# 1. 检查 Go 版本
echo "📋 检查 Go 版本..."
go_version=$(go version 2>/dev/null | awk '{{print $3}}')
if [ $? -ne 0 ]; then
    echo "❌ Go 未安装，请先安装 Go"
    echo "   推荐版本: Go 1.21 或更高"
    exit 1
fi
echo "✅ Go 版本: $go_version"
echo ""

# 2. 检查 go.mod
echo "📋 检查 Go 模块..."
if [ -f "go.mod" ]; then
    echo "✅ go.mod 存在"
else
    echo "❌ go.mod 不存在"
    echo "   运行: go mod init {project_info["name"]}"
    exit 1
fi
echo ""

# 3. 下载依赖
echo "📋 检查依赖..."
go mod download
echo "✅ 依赖已同步"
echo ""

# 4. 编译检查
echo "📋 编译检查..."
go build ./...
if [ $? -ne 0 ]; then
    echo "❌ 编译失败"
    exit 1
fi
echo "✅ 编译成功"
echo ""

# 5. 显示环境摘要
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 环境摘要"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Go: $go_version"
echo "  项目: {project_info["name"]}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 6. 运行测试
if [ -d "$(go env GOPATH)/pkg" ]; then
    echo "🧪 运行测试..."
    go test ./...
fi
'''

    else:  # Generic
        return f'''#!/bin/bash

# {project_name} 开发环境初始化脚本
# 用途: 快速启动开发环境，验证基本功能
# 使用方法: ./init.sh

echo "🚀 {project_name} 开发环境初始化..."
echo ""

# 1. 检查基本工具
echo "📋 检查基本工具..."
command -v git &> /dev/null && echo "✅ git 已安装" || echo "⚠️  git 未安装"
command -v make &> /dev/null && echo "✅ make 已安装" || echo "⚠️  make 未安装"
echo ""

# 2. 显示环境摘要
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 环境摘要"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  项目: {project_info["name"]} v{project_info["version"]}"
echo "  类型: {project_type}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 3. 检查是否有 Makefile
if [ -f "Makefile" ]; then
    echo "📋 发现 Makefile，可用命令:"
    make help 2>/dev/null || grep "^[a-zA-Z]" Makefile | head -10
fi
'''


def create_init_sh(project_path: Path, project_type: str, project_info: dict) -> Path:
    """Create init.sh script based on project type."""
    content = get_init_sh_content(project_type, project_info)
    output_path = project_path / "init.sh"
    output_path.write_text(content)
    os.chmod(output_path, 0o755)
    return output_path


def create_prompts_directory(project_path: Path, project_info: dict) -> Path:
    """Create .claude/prompts/ directory with agent prompts."""
    prompts_dir = project_path / ".claude" / "prompts"
    prompts_dir.mkdir(parents=True, exist_ok=True)

    # Base directory for harness prompts
    base_dir = Path(__file__).parent.parent / "prompts"

    # Copy all prompt files, substituting project name
    prompt_files = ["initializer.md", "coding-agent.md", "checkpoint.md"]
    for prompt_file in prompt_files:
        source = base_dir / prompt_file
        if source.exists():
            content = source.read_text()
            # Replace placeholder with actual project name
            content = content.replace("Project Name", project_info["name"].title())
            (prompts_dir / prompt_file).write_text(content)

    return prompts_dir


def get_claude_md_addition(project_type: str, project_info: dict) -> str:
    """Generate CLAUDE.md addition content."""
    return f'''

## 长运行代理 Harness

本项目采用 Anthropic 推荐的长运行代理 Harness 架构，支持 AI 代理在多个上下文窗口中持续有效工作。

参考：https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents

### 关键文件

1. **feature_list.json** - 功能需求列表
   - 记录所有功能需求及其状态（completed/pending/failed）
   - 代理只允许修改 `status` 字段，不得删除或修改功能描述
   - 使用 JSON 格式避免被意外修改

2. **claude-progress.txt** - 进度跟踪日志
   - 记录每次会话完成的工作
   - 当前状态和下一步计划
   - 帮助代理快速了解项目进展

3. **init.sh** - 开发环境初始化脚本
   - 检查环境依赖
   - 安装/同步依赖
   - 验证项目配置

### 代理工作流程

每次新会话开始时，代理应执行以下步骤：

1. **定位工作目录**
   ```bash
   pwd  # 确认当前工作目录
   ```

2. **了解项目进度**
   - 读取 `claude-progress.txt` 了解最近工作
   - 运行 `git log --oneline -10` 查看最近提交

3. **选择下一个任务**
   - 读取 `feature_list.json`
   - 选择优先级最高的 pending 功能开始工作

4. **验证环境状态**
   ```bash
   ./init.sh  # 验证开发环境
   ```

5. **完成工作后**
   - 提交 Git（描述性提交信息）
   - 更新 `claude-progress.txt`
   - 更新 `feature_list.json` 中的功能状态

### 测试要求

代理在标记功能为 "completed" 之前，必须：
1. 运行相关测试（如果存在）
2. 手动验证功能端到端工作正常
3. 确保代码符合项目规范
'''


def update_claude_md(project_path: Path, project_type: str, project_info: dict) -> bool:
    """Update CLAUDE.md with Harness documentation."""
    claude_md = project_path / "CLAUDE.md"

    if not claude_md.exists():
        return False

    content = claude_md.read_text()

    # Check if Harness section already exists
    if "长运行代理 Harness" in content or "Long-Running Agent Harness" in content:
        return False

    addition = get_claude_md_addition(project_type, project_info)
    new_content = content.rstrip() + "\n" + addition
    claude_md.write_text(new_content)
    return True


def main():
    # Determine project path
    if len(sys.argv) > 1:
        project_path = Path(sys.argv[1]).resolve()
    else:
        project_path = Path.cwd()

    if not project_path.exists():
        print(f"❌ 项目路径不存在: {project_path}")
        sys.exit(1)

    print(f"🚀 配置 Harness 系统于: {project_path}")
    print("")

    # Detect project type
    project_type = detect_project_type(project_path)
    print(f"📋 检测到项目类型: {project_type}")

    # Get project info
    project_info = get_project_info(project_path)
    print(f"📋 项目: {project_info['name']} v{project_info['version']}")
    print("")

    # Create files
    print("📦 创建 Harness 文件...")

    # 1. feature_list.json
    feature_list_path = create_feature_list(project_path, project_info, project_type)
    print(f"   ✅ {feature_list_path.name}")

    # 2. claude-progress.txt
    progress_path = create_progress_file(project_path, project_info)
    print(f"   ✅ {progress_path.name}")

    # 3. init.sh
    init_sh_path = create_init_sh(project_path, project_type, project_info)
    print(f"   ✅ {init_sh_path.name}")

    # 4. .claude/prompts/
    prompts_dir = create_prompts_directory(project_path, project_info)
    print(f"   ✅ .claude/prompts/")

    # 5. Update CLAUDE.md
    claude_md = project_path / "CLAUDE.md"
    if claude_md.exists():
        if update_claude_md(project_path, project_type, project_info):
            print(f"   ✅ CLAUDE.md (已更新)")
        else:
            print(f"   ⚠️  CLAUDE.md (Harness 章节已存在)")
    else:
        print(f"   ⚠️  CLAUDE.md (不存在，跳过)")

    print("")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("✅ Harness 系统配置完成！")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("")
    print("下一步:")
    print("   1. 检查并完善 feature_list.json 中的功能列表")
    print("   2. 运行 ./init.sh 验证开发环境")
    print("   3. 开始使用 Harness 系统进行开发")


if __name__ == "__main__":
    main()
