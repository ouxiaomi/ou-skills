# 通用项目 Harness 配置

## 适用场景

当无法检测到特定项目类型时，使用通用配置：
- 没有 `package.json`、`pyproject.toml`、`go.mod` 等文件
- 静态网站项目
- 文档项目
- 配置文件项目

## init.sh 模板

通用项目的 init.sh 包含：

1. **基本工具检查**
   ```bash
   command -v git &> /dev/null && echo "✅ git 已安装"
   command -v make &> /dev/null && echo "✅ make 已安装"
   ```

2. **环境摘要**
   ```bash
   echo "项目: {project_name}"
   echo "类型: generic"
   ```

3. **Makefile 支持（可选）**
   ```bash
   if [ -f "Makefile" ]; then
       make help
   fi
   ```

## 建议的目录结构

```
project/
├── CLAUDE.md           # 项目文档
├── feature_list.json   # 功能列表
├── claude-progress.txt # 进度日志
├── init.sh            # 初始化脚本
├── .claude/
│   └── prompts/       # 代理提示词
└── src/               # 源代码（如果有）
```

## 特殊项目类型

### 文档项目
- 可能使用 Markdown、AsciiDoc 等
- 可能有 `mkdocs.yml` 或 `conf.py`

### 配置项目
- 可能包含 YAML、JSON、TOML 配置
- 可能有 schema 验证

### 静态网站
- 可能有 `index.html`
- 可能有构建脚本

## Harness 与通用项目

### 最小化配置

对于简单项目，Harness 可以简化：

```bash
#!/bin/bash
echo "=== Generic Project Setup ==="
echo "Project: $(pwd | xargs basename)"
echo ""
echo "Checking basic tools..."
command -v git >/dev/null 2>&1 && echo "✅ git"
command -v make >/dev/null 2>&1 && echo "✅ make"
echo ""
echo "Project ready for development."
```

### 扩展配置

对于更复杂的通用项目：

```bash
#!/bin/bash

# 1. 检查项目类型特定的工具
# 2. 运行项目特定的验证
# 3. 报告项目状态

# 检查文档工具
if [ -f "mkdocs.yml" ]; then
    echo "📚 MkDocs project detected"
fi

# 检查构建文件
if [ -f "Makefile" ]; then
    echo "🔨 Makefile detected"
    make help 2>/dev/null || true
fi

# 检查测试
if [ -f "tox.ini" ]; then
    echo "🧪 tox detected"
fi

echo ""
echo "Environment check complete."
```

## Feature List 建议

通用项目的 feature_list.json 应该关注：

- 项目结构搭建
- 文档完善
- 配置管理
- 部署流程
- 测试覆盖

如果项目有特定需求，可以在 `feature_list.json` 中添加自定义字段。