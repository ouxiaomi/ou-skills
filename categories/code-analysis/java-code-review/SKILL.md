---
name: java-code-review
description: 仅审查当前分支相对基线(master/main)的 Java 代码改动，但结合完整文件上下文给出结构化建议与改进方案，生成 Markdown 报告并可打包输出。
allowed_tools:
  - Read
  - Grep
  - Glob
  - RunCommand
entry: scripts/java_code_review.py
outputs:
  - reviews/java/java_code_review.md
---
# 目标

在工作区内对 Java 文件进行差异化代码审查：只聚焦改动的 diff，但结合文件整体情况输出可读、可执行的建议，最终产出 `reviews/java/java_code_review.md`。

# 使用说明

1. 工作目录需为 Git 仓库，并存在基线分支 `master` 或 `main`。
2. 运行入口脚本：
   - Python: `python3 .claude/skills/java-diff-review/scripts/java_code_review.py`
3. 报告生成位置：`reviews/java/java_code_review.md`。

# 审查范围与原则

- 只审查 Java 文件的差异（当前分支 vs 基线分支），但建议基于完整文件上下文。
- 输出包括：结构组织、可读性、可维护性、反设计模式/坏味道识别、性能与安全提示、具体修改建议。
- 建议以最小影响面优先，遵循优雅代码风格。

# 审查清单（参考）
1. 代码组织与命名：包结构、类/方法命名、单一职责。
2. 错误处理：异常类型、异常传播与日志、资源释放。
3. 可读性与复杂度：方法长度、嵌套深度、条件分支复杂度。
4. API 设计：参数数量、返回契约、空值处理与 Optional 使用。
5. 日志与监控：`System.out` 替换为日志框架；敏感信息不落盘。
6. 性能与资源：集合选择、流处理、I/O、数据库/网络调用。
7. 安全与稳健：输入校验、SQL/命令注入、线程安全、不可变性。
8. 测试与覆盖率：新增逻辑的单元与边界测试。
9. 编码风格：确保优雅且代码容易维护。
10. 代码行数：God class（文件超过 800 行）。
11. 代码行数：Long method（方法超过 80 行）。
12. Feature envy & data clumps（参数间重复组合）。

# 运行策略
- 自动探测基线分支（优先 `master`，否则 `main`）。
- 仅当 diff 存在 Java 文件时生成逐文件审查段落；否则输出结构化空报告与指引。
- 对每个改动文件：
  - 概览：新增/删除行数与变更块。
  - 重点问题：坏味道列表（例如广义异常捕获、`System.out.println`、长参数列表、魔法数、空值判定等）。
  - 建议与示例：给出修改方向与简要示例。

# 集成建议
- 在 Claude Code 或 Codex 中启用 Agent Skills 后，工作区将自动发现此 Skill
- 如需只允许本 Skill 运行特定工具，可在运行时限制为 `Read/Grep/Glob/RunCommand`