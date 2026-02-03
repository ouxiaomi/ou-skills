---
name: deploy-service
description: 一键部署 GitHub 项目到 Docker 并自动集成到 Homepage (user)
---

# GitHub 项目一键部署

当用户说 **"帮我部署 https://github.com/xxx/xxx"** 时，自动执行完整部署流程：
1. 克隆并分析项目
2. 收集配置信息
3. 一键部署到 Docker
4. 自动集成到 Homepage（可选）

---

## 触发条件

- "部署 https://github.com/xxx/xxx"
- "帮我部署下 https://github.com/xxx/xxx"
- "安装 https://github.com/xxx/xxx"

---
## 禁止行为

- ❌ 未经确认直接部署
- ❌ **未经用户同意删除任何已有文件或目录**
- ❌ **覆盖用户已有的项目目录**

---
## 完整执行流程

### 阶段 1：项目分析

#### 1.1 克隆项目到临时目录

```bash
# 克隆到临时目录分析
cd /tmp
rm -rf temp-deploy-analysis
git clone <GitHub地址> temp-deploy-analysis
cd temp-deploy-analysis
```

#### 1.2 分析项目结构

读取并分析以下文件：

```bash
# 必读文件
cat README.md
cat docker-compose.yml 2>/dev/null || cat docker-compose.yaml 2>/dev/null
cat .env.example 2>/dev/null
cat Dockerfile 2>/dev/null

# 项目结构
ls -la
```

**提取信息：**
- 服务名称、功能描述
- 需要的环境变量（从 .env.example 或 README）
- 端口映射
- 数据持久化需求
- 依赖服务（数据库等）

---

### 阶段 2：端口自动分配

**必须执行端口检查：**

```bash
# 综合检查所有已占用端口
{
  # Docker 容器占用端口
  docker ps --format "{{.Ports}}" | grep -oE "0\.0\.0\.0:[0-9]+" | cut -d':' -f2

  # 系统监听端口
  ss -tlnp 2>/dev/null | grep LISTEN | awk '{print $4}' | grep -oE "[0-9]+$"
} | sort -n | uniq
```

**端口分配规则：**
- 从 9000 开始往上递增分配
- 找出最大端口号，从最大值+1 开始分配
- 需要多个端口时，选择连续的未占用端口

**重要 - 区分宿主机端口和容器内部端口：**
- 宿主机端口：docker-compose.yml 中的映射端口（如 `9003:8000` 中的 `9003`）
- 容器内部端口：应用默认端口（如 `9003:8000` 中的 `8000`）
- .env 中的 PORT/SERVER_PORT 应设置为**容器内部端口**，不是宿主机端口

```yaml
# 正确示例
ports:
  - "9003:8000"  # 宿主机 9003 映射到容器 8000

# .env
SERVER_PORT=8000  # ✅ 容器内监听 8000
```

---

### 阶段 3：使用 AskUserQuestion 收集配置

**必须询问的配置：**

1. **服务名称**（用于目录名、容器名）
2. **服务描述**（1-2 句话）
3. **所有环境变量**（逐一说明用途，不得臆测）
4. **项目部署路径**（默认：`~/docker/<服务名>`）
5. **宿主机 IP**（用于访问服务，如 `192.168.1.100` 或 `localhost`）
6. **Homepage 集成**（可选）：
   - 是否集成到 Homepage？
   - 如果是：Homepage 项目路径、分类、图标域名

**注意：端口号自动分配，无需询问用户**

---

### 阶段 4：配置确认

以清晰格式展示所有配置：

```
📋 部署配置预览

服务名称：xxx
访问地址：http://<宿主机IP>:<端口>
项目目录：<项目路径>
Homepage 集成：是/否

环境变量：
- VAR1: value1
- VAR2: value2

端口映射：
- 宿主机 <端口> → 容器 <内部端口> (Web UI)

请确认配置是否正确？必须回复 "yes"/"确认"/"部署" 才会继续。
```

**⚠️ 必须等待用户明确回复才能继续**

---

### 阶段 5：网络连通性检查

```bash
# 检查 Docker Hub 连通性（5秒超时）
timeout 5 curl -s -o /dev/null -w "%{http_code}" https://registry-1.docker.io/v2/ || echo "网络不可达"
```

**如果检测到网络问题或镜像拉取失败：**

1. 提示用户配置 Docker 镜像加速器
2. 提供配置方法：

```bash
# 编辑 Docker daemon 配置
sudo vim /etc/docker/daemon.json

# 添加镜像加速器配置（示例）：
{
  "registry-mirrors": [
    "https://docker.hpcloud.cloud",
    "https://docker.m.daocloud.io",
    "https://docker.unsee.tech",
    "https://docker.1panel.live",
    "https://mirror.aliyuncs.com",
    "https://dockerproxy.com",
    "https://docker.nju.edu.cn",
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub.rat.dev",
    "https://docker.chenby.cn"
  ]
}

# 重启 Docker 服务
sudo systemctl daemon-reload
sudo systemctl restart docker
```

3. 等待用户配置完成后重试拉取镜像
4. 最多重试 2 次

---

### 阶段 6：部署执行

#### 6.1 检查目标目录

**⚠️ 严禁删除用户已有的文件或文件夹！**

```bash
# 检查目标目录是否已存在
if [ -d <项目路径> ]; then
  echo "⚠️ 目录 <项目路径> 已存在"
  ls -la <项目路径>
fi
```

**如果目录已存在：**
1. 询问用户如何处理：
   - 选项 A：使用新目录名（如 `<服务名>-2`）
   - 选项 B：用户手动清理后继续
   - 选项 C：取消部署
2. **绝对禁止**在未经用户同意的情况下删除或覆盖已有目录

#### 6.2 创建项目目录

```bash
# 创建项目目录（仅在目录不存在时）
mkdir -p <项目路径>
cd <项目路径>

# 克隆项目
git clone <GitHub地址> .

# 创建数据目录（如需要）
mkdir -p data
```

#### 6.3 配置文件处理

使用 Edit 工具修改 docker-compose.yml：

1. **更新端口映射**为分配的端口

2. **添加 healthcheck**：

```yaml
healthcheck:
  test: ["CMD", "nc", "-z", "127.0.0.1", "<容器内端口>"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 10s
```

**Healthcheck 注意事项：**
- 使用 `127.0.0.1` 而非 `localhost`
- 端口号使用**容器内部端口**
- 如果容器内有 wget：`["CMD-SHELL", "wget --spider -q http://127.0.0.1:<端口>"]`
- 复杂应用 `start_period` 可设置为 30-60s

3. **如果用户选择集成 Homepage**，添加 labels：

```yaml
labels:
  - homepage.group=<分类名称>
  - homepage.name=<服务名称>
  - homepage.icon=http://<宿主机IP>/icons/<服务名>.png
  - homepage.href=http://<宿主机IP>:<宿主机端口>
  - homepage.description=<服务描述>
```

4. **创建/更新 .env 文件**

```bash
# 根据收集的配置创建 .env
cat > .env << 'EOF'
VAR1=value1
VAR2=value2
TZ=Asia/Shanghai
EOF
```

#### 6.4 启动服务

```bash
cd <项目路径>
docker-compose up -d

# 等待启动
sleep 5

# 检查状态
docker ps | grep <服务名>
docker logs <容器名> --tail 30
```

---

### 阶段 7：Homepage 集成（可选）

**仅当用户选择集成 Homepage 时执行此阶段。**

#### 7.1 下载图标

```bash
curl -L -o <Homepage路径>/config/icons/<服务名>.png "https://icon.ooo/<域名>"

# 验证图标下载成功
ls -lh <Homepage路径>/config/icons/<服务名>.png
```

#### 7.2 重启 Homepage

```bash
cd <Homepage路径>
docker-compose restart

# 等待启动
sleep 3
```

**如果用户跳过 Homepage 集成，直接进入阶段 8。**

---

### 阶段 8：验证部署

**优先使用 Playwright MCP 验证（如果可用）：**

1. 导航到服务地址：`browser_navigate: http://<宿主机IP>:<端口>/`
2. 等待加载：`browser_wait_for: time=3`
3. 截图验证：`browser_take_screenshot: filename=deploy-<服务名>.png`
4. 检查页面：`browser_snapshot`

**如果没有 Playwright MCP，使用 curl/WebFetch 验证：**

```bash
# 验证服务可访问
curl -s -o /dev/null -w "%{http_code}" http://<宿主机IP>:<端口>
```

或使用 WebFetch 工具访问 `http://<宿主机IP>:<端口>` 检查服务是否正常响应

**验证检查点：**
- ✅ 服务 HTTP 状态码为 200
- ✅ 容器状态为 running/healthy

---

### 阶段 9：生成部署报告

```markdown
## 🎉 <服务名> 部署成功

### 📌 访问信息
- **服务地址**：http://<宿主机IP>:<端口>
- **容器名称**：<容器名>
- **项目目录**：<项目路径>

### 📊 容器状态
- 运行状态：✅ Running
- 健康检查：✅ Healthy

### 🔧 常用命令
# 查看日志
docker logs <容器名> -f

# 重启服务
cd <项目路径> && docker-compose restart

# 停止服务
cd <项目路径> && docker-compose down

# 更新服务
cd <项目路径> && git pull && docker-compose pull && docker-compose up -d
```

---

### 阶段 10：清理临时文件

```bash
rm -rf /tmp/temp-deploy-analysis
```

---

## 错误处理

**镜像拉取失败：**
- 提示配置 Docker 镜像加速器
- 提供配置方法
- 最多重试 2 次

**端口冲突：**
- 重新分配端口
- 询问用户确认新端口

**容器启动失败：**
- 查看日志 `docker logs <容器名>`
- 检查环境变量、依赖服务
- 报告错误并提供解决建议

**图标下载失败：**
- 尝试备用域名
- 或询问用户提供图标 URL

---


## 相关文档

- 图标 API：`https://icon.ooo/{domain}`
- Homepage 官方文档：`https://gethomepage.dev`
