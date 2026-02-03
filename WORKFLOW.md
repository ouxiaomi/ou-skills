# 技能仓库管理流程

## 新增技能

1. 确定技能分类，在 `categories/` 下创建/选择对应目录
2. 创建技能文件夹（短横线命名，如 `my-awesome-skill`）
3. 创建 `SKILL.md`（必需）
4. 添加可选文件：`reference.md`、`examples.md`、`scripts/`、`templates/`
5. 更新 `SKILLS-INDEX.md` 添加索引信息

## 更新流程

每次修改后按顺序执行：

```bash
cd ~/.openclaw/workspace/ou-skills
git add .
git commit -m "描述变更内容"
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
```

**维护者**: 君小秘
**仓库**: https://github.com/ouxiaomi/ou-skills
