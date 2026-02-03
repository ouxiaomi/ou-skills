# Deploy Service - GitHub 项目一键部署技能

一键部署 GitHub 项目到 Docker 的 Claude Code 技能。

## 功能

当你说 **"帮我部署 https://github.com/xxx/xxx"** 时，自动完成：

1. 克隆项目并分析部署需求
2. 收集配置信息（环境变量、端口等）
3. 自动分配可用端口
4. 部署 Docker 服务
5. 集成到 Homepage（可选）

## 安装

将 `deploy-service` 文件夹解压到 `~/.claude/skills/` 目录：

```bash
# 创建 skills 目录（如果不存在）
mkdir -p ~/.claude/skills

# 解压技能包
unzip deploy-service.zip -d ~/.claude/skills/

# 验证安装
ls ~/.claude/skills/deploy-service/
# 应该看到: SKILL.md  README.md
```

## 使用方式

```
帮我部署 https://github.com/xxx/xxx
部署 https://github.com/xxx/xxx
安装 https://github.com/xxx/xxx
```

## 执行流程

```
用户请求部署 GitHub 项目
        ↓
克隆到临时目录分析
        ↓
自动分配可用端口
        ↓
询问配置
├── 服务名称
├── 环境变量
├── 项目部署路径
├── 宿主机 IP
└── Homepage 集成（可选）
        ↓
展示配置预览
        ↓
用户确认？ ──No──→ 调整配置
        ↓ Yes
部署到 Docker
        ↓
Homepage 集成（如果选择）
        ↓
验证部署
        ↓
生成部署报告
```

## 特性

- **自动端口分配**：从 9000 开始递增，自动检查冲突
- **智能配置收集**：分析 README、docker-compose.yml、.env.example
- **Homepage 集成可选**：不强制依赖 Homepage
- **安全部署**：不会删除已有文件，必须用户确认才部署
- **镜像加速提示**：拉取失败时提供国内镜像配置方法

## 要求

- Docker 和 docker-compose
- Git
- Claude Code CLI

## 版本历史

### v2.1.0 (2025-12-08)
- Homepage 集成改为可选
- 移除硬编码路径，改为动态询问
- 增加镜像加速器配置提示
- 增加目录存在检查，防止误删

### v2.0.0 (2025-12-07)
- 重构：专注 GitHub 项目部署
- 移除：局域网服务发现功能

### v1.0.0 (2025-11-11)
- 初始版本

## 许可

MIT
