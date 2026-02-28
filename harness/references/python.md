# Python 项目 Harness 配置

## 项目类型检测

Python 项目通过以下文件检测：
- `pyproject.toml` - 现代 Python 项目（推荐）
- `setup.py` - 传统项目
- `requirements.txt` - 依赖列表

## init.sh 模板

Python 项目的 init.sh 包含：

1. **Python 版本检查**
   ```bash
   python_version=$(python3 -c "import sys; print(sys.version.split()[0])")
   # 推荐版本: Python 3.11 或更高
   ```

2. **虚拟环境检查**
   - 检查 `.venv/` 或 `venv/`
   - 自动激活虚拟环境

3. **包管理器检测**
   - 优先使用 `uv` (推荐)
   - 回退到 `pip`

4. **依赖安装**
   ```bash
   # uv 方式
   uv sync  # pyproject.toml
   uv pip install -r requirements.txt

   # pip 方式
   pip install -r requirements.txt
   ```

5. **配置文件检查**
   - `pyproject.toml` (现代项目)
   - `requirements.txt` (传统项目)
   - `setup.py` (传统项目)

6. **测试运行（可选）**
   ```bash
   if [ -f "pytest.ini" ] || [ -d "tests" ]; then
       $PKG_MANAGER run pytest
   fi
   ```

## 常见项目结构

### FastAPI 项目
```
project/
├── app/
│   ├── main.py
│   ├── api/
│   └── core/
├── tests/
├── pyproject.toml
└── .venv/
```

### Django 项目
```
project/
├── manage.py
├── project_name/
├── apps/
├── requirements.txt
└── .venv/
```

### 包项目
```
project/
├── src/
│   └── package_name/
├── tests/
├── pyproject.toml
└── README.md
```

## pyproject.toml 示例

```toml
[project]
name = "my-project"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.109.0",
    "uvicorn>=0.27.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "mypy>=1.8.0",
    "ruff>=0.2.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.mypy]
python_version = "3.11"
strict = true

[tool.ruff]
line-length = 88
select = ["E", "F", "I", "N", "W"]
```

## Harness 最佳实践

### 虚拟环境优先

Harness 脚本应始终使用虚拟环境：

```bash
# 检测并激活虚拟环境
if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
fi
```

### UV 推荐配置

```bash
# 使用 uv 进行依赖管理
if command -v uv &> /dev/null; then
    # 同步依赖
    uv sync
    
    # 运行测试
    uv run pytest
    
    # 启动开发服务器
    uv run uvicorn app.main:app --reload
fi
```

### 测试集成

确保 init.sh 可以运行基本测试验证：

```bash
# 在 init.sh 末尾添加测试检查
if [ -f "pytest.ini" ] || [ -d "tests" ]; then
    echo "🧪 验证测试..."
    uv run pytest --tb=short -q
fi
```