# Git 提交消息使用示例

## 示例场景

### 场景 1：简单的功能添加
**用户请求：**
```
帮我看看暂存区的改动，生成个提交消息
```

**技能执行：**
1. 执行 `git status --short` → 发现新增 `src/utils/validator.js`
2. 执行 `git diff --cached` → 添加了验证函数
3. 执行 `git log -5 --pretty=format:%s` → 最近提交多为 `feat:` 前缀
4. 输出：`feat: 添加工具类验证函数`

### 场景 2：Bug 修复
**用户请求：**
```
读取暂存区，建议提交消息
```

**技能执行：**
1. 执行 `git status --short` → 发现修改 `src/api/user.js`
2. 执行 `git diff --cached` → 修复了 null 值处理
3. 执行 `git log -5 --pretty=format:%s` → 最近提交多为 `fix:` 前缀
4. 输出：`fix: 修复用户接口空值处理`

### 场景 3：多文件改动
**用户请求：**
```
总结暂存区的变更并生成提交消息
```

**技能执行：**
1. 执行 `git status --short` → 发现修改 `README.md`、`package.json`、`src/index.js`
2. 执行 `git diff --cached --stat` → README 新增说明，package.json 更新版本，index.js 新增初始化逻辑
3. 执行 `git log -5 --pretty=format:%s` → 发现使用 `doc:` 和 `feat:` 风格
4. 输出：`feat: 添加初始化模块并更新文档`

**补充建议：** "建议将文档和代码改动分开提交"

### 场景 4：暂存区为空
**用户请求：**
```
看看暂存区有什么改动
```

**技能执行：**
1. 执行 `git status --short` → 无暂存内容
2. 输出：`暂存区为空，是否需要暂存文件或查看未暂存的改动？`

### 场景 5：有未暂存改动
**用户请求：**
```
生成提交消息
```

**技能执行：**
1. 执行 `git status --short` → 有暂存内容 + 有未暂存内容
2. 执行 `git diff --cached` → 读取暂存区变更
3. 执行 `git log -5 --pretty=format:%s` → 匹配风格
4. 输出：`refactor: 优化错误处理逻辑` + `（注意：未暂存的改动不会包含在本次提交中）`
