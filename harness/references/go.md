# Go 项目 Harness 配置

## 项目类型检测

Go 项目通过以下文件检测：
- `go.mod` - Go 模块定义文件

## init.sh 模板

Go 项目的 init.sh 包含：

1. **Go 版本检查**
   ```bash
   go_version=$(go version 2>/dev/null | awk '{print $3}')
   # 推荐版本: Go 1.21 或更高
   ```

2. **go.mod 检查**
   ```bash
   if [ -f "go.mod" ]; then
       echo "✅ go.mod 存在"
   else
       echo "❌ go.mod 不存在"
       go mod init <module-name>
   fi
   ```

3. **依赖下载**
   ```bash
   go mod download
   ```

4. **编译检查**
   ```bash
   go build ./...
   ```

5. **测试运行**
   ```bash
   go test ./...
   ```

## 常见项目结构

### 标准布局
```
project/
├── cmd/
│   └── myapp/
│       └── main.go
├── internal/
│   ├── handler/
│   ├── service/
│   └── repository/
├── pkg/
│   └── utils/
├── api/
├── go.mod
└── go.sum
```

### 简单布局
```
project/
├── main.go
├── handler.go
├── service.go
├── go.mod
└── go.sum
```

## go.mod 示例

```go
module github.com/user/myapp

go 1.22

require (
    github.com/gin-gonic/gin v1.9.1
    github.com/spf13/cobra v1.8.0
)
```

## 常用命令

```bash
# 初始化模块
go mod init github.com/user/myapp

# 下载依赖
go mod download

# 整理依赖
go mod tidy

# 运行
go run ./cmd/myapp

# 构建
go build -o bin/myapp ./cmd/myapp

# 测试
go test ./...

# 测试覆盖率
go test -cover ./...
```
