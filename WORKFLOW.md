# 技能仓库管理流程

## 新增技能流程

1. **检查重复** ⚠️
   ```bash
   python3 scripts/check_before_add.py <新技能路径>/SKILL.md
   ```
   如果提示重复，确认是否继续

2. **确定分类**
   - 在 `categories/` 下选择或创建对应分类目录
   - 常见分类：code-analysis, development, productivity, communication

3. **创建技能文件夹**
   - 使用短横线命名，如 `my-awesome-skill`
   - 完整路径示例：`categories/code-analysis/my-awesome-skill/`

4. **创建必需文件**
   - **SKILL.md** (必需) - 技能说明和使用指南
   - **reference.md** (可选) - 参考文档
   - **examples.md** (可选) - 使用示例
   - **scripts/** (可选) - 辅助脚本
   - **templates/** (可选) - 模板文件

5. **更新索引**
   - 更新 `SKILLS-INDEX.md` 添加技能信息
   - 运行 `python3 scripts/check_skill_hash.py` 更新hash索引

## 重复检测机制

### Hash索引系统
- 每个技能的 `SKILL.md` 都会计算 SHA-256 hash
- hash值存储在 `.skills-hash.json` 中
- 新增技能前自动检查hash，避免重复

### 常用命令

**扫描所有技能并更新hash索引：**
```bash
python3 scripts/check_skill_hash.py
```

**检查新技能是否重复：**
```bash
python3 scripts/check_before_add.py categories/xxx/my-skill/SKILL.md
```

**查看当前hash索引：**
```bash
cat .skills-hash.json
```

## 更新流程

每次修改后按顺序执行：

```bash
cd ~/.openclaw/workspace/ou-skills

# 1. 添加所有变更
git add .

# 2. 提交（描述清楚变更内容）
git commit -m "feat: 添加新技能 xxx

- 分类: code-analysis
- 功能: xxx描述
- hash: xxx（可选）"

# 3. 推送到远程
git push origin main
```

## 目录结构

```
categories/
├── code-analysis/      # 代码分析
├── development/        # 开发工具
├── productivity/       # 生产力
├── communication/      # 通信
└── ... (按需添加新分类)

scripts/
├── check_skill_hash.py     # 扫描所有技能并更新hash索引
├── check_before_add.py     # 新增技能前检查重复
└── check-skill-hash.sh     # Bash版本（备选）

.skills-hash.json        # Hash索引文件（自动生成）
SKILLS-INDEX.md          # 技能目录索引
WORKFLOW.md             # 本文档（工作流程）
```

## 规则总结

✅ **新增技能前**：必须运行 `check_before_add.py` 检查重复
✅ **提交前**：运行 `check_skill_hash.py` 更新hash索引
✅ **命名规范**：使用短横线（kebab-case）命名文件夹
✅ **文档完整**：每个技能至少要有 SKILL.md

**维护者**: 君小秘
**仓库**: https://github.com/ouxiaomi/ou-skills
