# Node.js 项目 Harness 配置

## 项目类型检测

Node.js 项目通过以下文件检测：
- `package.json` - 存在即为 Node.js 项目
- 进一步检测框架：
  - `vue` 依赖 → Vue 项目
  - `react`/`react-dom` 依赖 → React 项目
  - `next` 依赖 → Next.js 项目
  - `svelte` 依赖 → Svelte 项目
  - `express`/`fastify` 依赖 → 后端项目

## init.sh 模板

Node.js 项目的 init.sh 包含：

1. **Node.js 版本检查**
   ```bash
   node -v
   # 推荐版本: Node.js 18.x 或更高
   ```

2. **包管理器检测**
   - 优先级: pnpm > npm > yarn
   - 自动选择可用的包管理器

3. **依赖安装**
   ```bash
   if [ ! -d "node_modules" ]; then
       $PKG_MANAGER install
   fi
   ```

4. **配置文件检查**
   - `package.json` (必需)
   - `vite.config.js` (Vite 项目)
   - `tsconfig.json` (TypeScript 项目)

5. **开发服务器启动**
   ```bash
   $PKG_MANAGER dev
   ```

## 常见框架特定配置

### Vue 项目
```bash
# 检测
if grep -q '"vue"' package.json; then
    echo "Vue project detected"
fi

# 开发命令通常
pnpm dev
# 或
pnpm serve
```

### React 项目
```bash
# Create React App
pnpm start

# Vite
pnpm dev
```

### Next.js 项目
```bash
# App Router
pnpm dev

# Pages Router
pnpm dev
```

### 后端项目 (Express/Fastify)
```bash
# 可能需要 concurrently 同时运行服务和客户端
concurrently "pnpm server" "pnpm client"

# 或使用 nodemon 调试
nodemon src/index.js
```

## TypeScript 支持

```bash
# 检查 TypeScript 配置
if [ -f "tsconfig.json" ]; then
    echo "✅ TypeScript"
    
    # 类型检查
    pnpm exec tsc --noEmit
fi

# 或
pnpm typecheck
```

## 测试配置

```bash
# Jest
pnpm test

# Vitest
pnpm test

# Playwright
pnpm playwright test
```

## 常用命令速查

| 命令 | 说明 |
|------|------|
| `pnpm install` | 安装依赖 |
| `pnpm dev` | 启动开发服务器 |
| `pnpm build` | 生产构建 |
| `pnpm preview` | 预览生产构建 |
| `pnpm test` | 运行测试 |
| `pnpm lint` | 代码检查 |
| `pnpm typecheck` | TypeScript 类型检查 |

## Docker 支持

```dockerfile
# 多阶段构建示例
FROM node:18-alpine AS builder

WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN corepack enable pnpm && pnpm install --frozen-lockfile

COPY . .
RUN pnpm build

FROM node:18-alpine AS runner
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/package.json .
CMD ["node", "dist/index.js"]
```

## 框架特定开发命令

### Next.js
```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  }
}
```

### Vite (React/Vue)
```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  }
}
```

### Express
```json
{
  "scripts": {
    "dev": "nodemon src/index.js",
    "start": "node src/index.js"
  }
}
```

## Harness 最佳实践

### 环境验证

```bash
# 检查 Node.js 版本
NODE_MAJOR=$(node -v | cut -d. -f1 | tr -d 'v')
if [ "$NODE_MAJOR" -lt 18 ]; then
    echo "❌ 需要 Node.js 18 或更高版本"
    exit 1
fi
```

### 包管理器偏好

```bash
# 推荐 pnpm（严格版本管理 + 节省空间）
if command -v pnpm &> /dev/null; then
    PKG_MANAGER="pnpm"
elif command -v npm &> /dev/null; then
    PKG_MANAGER="npm"
else
    echo "❌ 需要安装包管理器"
    exit 1
fi
```

### 构建验证

```bash
# 开发前先验证构建
pnpm build

# 如果构建成功，继续
if [ $? -eq 0 ]; then
    echo "✅ 构建验证通过"
fi
```