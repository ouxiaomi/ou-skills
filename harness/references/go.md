# Go 项目 Harness 配置

## 项目类型检测

Go 项目通过以下文件检测：
- `go.mod` - Go 模块定义

## init.sh 模板

Go 项目的 init.sh 包含：

1. **Go 版本检查**
   ```bash
   go_version=$(go version 2>/dev/null | awk '{print $3}')
   # 推荐版本: Go 1.21 或更高
   ```

2. **模块检查**
   ```bash
   if [ -f "go.mod" ]; then
       echo "✅ go.mod 存在"
   fi
   ```

3. **依赖同步**
   ```bash
   go mod download
   go mod tidy
   ```

4. **编译验证**
   ```bash
   go build ./...
   ```

5. **测试运行**
   ```bash
   go test -v ./...
   ```

## 常见项目结构

### 标准 Go 项目
```
project/
├── cmd/
│   └── yourapp/
│       └── main.go
├── internal/
│   ├── handler/
│   └── storage/
├── go.mod
└── go.sum
```

### API 服务项目
```
project/
├── cmd/
│   └── server/
│       └── main.go
├── internal/
│   ├── config/
│   ├── handlers/
│   ├── middleware/
│   └── models/
├── go.mod
└── README.md
```

### 模块化项目
```
project/
├── module1/
│   ├── go.mod
│   └── ...
├── module2/
│   ├── go.mod
│   └── ...
├── cmd/
└── go.work (工作区)
```

## go.mod 示例

```go
module github.com/username/project

go 1.21

require (
	github.com/gin-gonic/gin v1.9.1
	github.com/joho/godotenv v1.5.1
)
```

## Go 工作区配置 (go.work)

对于多模块项目：

```go
go 1.21

use (
	./module1
	./module2
	./cmd
)
```

## Harness 最佳实践

### 开发命令

使用实用的开发命令：

```bash
# 热重载开发
# 需要 air: go install github.com/air-verse/air@latest
air -c .air.toml

# 或使用标准方式
go run ./cmd/yourapp
```

### 测试覆盖

```bash
# 运行所有测试
go test -v -coverprofile=coverage.out ./...

# 查看覆盖率报告
go tool cover -html=coverage.out
```

### 代码质量工具

推荐集成 linter：

```bash
# golangci-lint
golangci-lint run

# 或 go fmt
go fmt ./...
go vet ./...
```

### Docker 支持 (可选)

```dockerfile
FROM golang:1.21-alpine AS builder

WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 go build -o /app/main ./cmd/yourapp

FROM alpine:latest
COPY --from=builder /app/main /app/main
CMD ["/app/main"]
```

## 常用命令速查

| 命令 | 说明 |
|------|------|
| `go mod init <name>` | 初始化模块 |
| `go mod tidy` | 整理依赖 |
| `go mod download` | 下载依赖 |
| `go build ./...` | 编译所有包 |
| `go test ./...` | 运行所有测试 |
| `go run ./cmd/...` | 运行应用 |
| `air` | 热重载开发 |