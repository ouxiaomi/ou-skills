# 安装指南

## 快速安装

```bash
# 方法 1：直接下载并解压
curl -L https://github.com/你的用户名/claude-deploy-service/archive/refs/heads/main.zip -o deploy-service.zip
unzip deploy-service.zip
mv claude-deploy-service-main ~/.claude/skills/deploy-service

# 方法 2：使用 git clone
git clone https://github.com/你的用户名/claude-deploy-service.git ~/.claude/skills/deploy-service
```

## 验证安装

```bash
ls ~/.claude/skills/deploy-service/
# 应该看到: SKILL.md  README.md
```

## 使用

安装完成后，对 Claude Code 说：

```
帮我部署 https://github.com/xxx/xxx
```

就可以开始使用了。

## 要求

- Docker 和 docker-compose
- Git
- Claude Code CLI

## 故障排查

### 技能没有触发

检查技能目录是否正确：
```bash
ls -la ~/.claude/skills/deploy-service/SKILL.md
```

### 权限问题

确保文件有读取权限：
```bash
chmod +r ~/.claude/skills/deploy-service/*
```

## 更新

```bash
cd ~/.claude/skills/deploy-service
git pull
```
