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
