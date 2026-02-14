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
   node_version=$(node -v 2>/dev/null)
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
- 检查 `vite.config.js` 或 `vue.config.js`
- 开发命令: `pnpm dev` 或 `pnpm serve`

### React 项目
- Create React App: `pnpm start`
- Vite: `pnpm dev`

### Next.js 项目
- 开发命令: `pnpm dev`
- 检查 `next.config.js`

### 后端项目
- Express: 检查 `src/index.js` 或 `server.js`
- Fastify: 检查 `app.js`
- 可能需要环境变量检查
