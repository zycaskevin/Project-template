#!/bin/bash

# 新專案初始化腳本 (Project Initialization Script)
# Version: 4.0
# Usage: ./init-project.sh

set -e  # Exit on error

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 新專案初始化開始 (Project Initialization)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Step 1: 創建標準目錄結構
echo "📁 Step 1/7: 創建目錄結構..."
mkdir -p src/{backend,frontend,shared}
mkdir -p tests/{unit,integration,e2e}
mkdir -p docs/{research,product,design,analytics,technical}
mkdir -p data/{handoffs,stage_archives,reviews,vectors}
mkdir -p features
mkdir -p scripts/{ci,deployment}

echo "   ✅ 目錄結構創建完成"
echo ""

# Step 2: 生成基礎文件
echo "📄 Step 2/7: 生成基礎文件..."

# README.md
if [ ! -f README.md ]; then
    cat > README.md << 'EOF'
# Project Name

**Version**: 0.1.0
**Status**: 🚧 In Development

## 📋 Description

[Brief description of your project]

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements/base.txt

# Run tests
pytest tests/ -v

# Start development server
python src/main.py
```

## 📚 Documentation

- [Architecture](docs/technical/ARCHITECTURE.md)
- [API Reference](docs/technical/API.md)
- [Development Guide](.claude/CLAUDE.md)

## 🔧 Development Workflow

This project follows TDD + Multi-Agent workflow:

1. **SBE Workshop** - Define requirements in `features/*.feature`
2. **TDD Red** - Write failing tests
3. **TDD Green** - Minimal implementation
4. **TDD Refactor** - Improve code quality

See [CLAUDE.md](.claude/CLAUDE.md) for full workflow details.

## 📊 Quality Metrics

- Code Coverage: ![Coverage](https://img.shields.io/badge/coverage-0%25-red)
- Code Quality: ![Quality](https://img.shields.io/badge/quality-A-green)
- Build Status: ![Build](https://img.shields.io/badge/build-passing-green)

EOF
    echo "   ✅ README.md 創建完成"
else
    echo "   ⏭️  README.md 已存在,跳過"
fi

# .gitignore
if [ ! -f .gitignore ]; then
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Environment
.env
.env.local

# Data
data/vectors/
data/handoffs/*.json
data/reviews/

# Logs
*.log
logs/

EOF
    echo "   ✅ .gitignore 創建完成"
else
    echo "   ⏭️  .gitignore 已存在,跳過"
fi

# pytest.ini
if [ ! -f pytest.ini ]; then
    cat > pytest.ini << 'EOF'
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --strict-markers
    --tb=short
    --cov=src
    --cov-report=html
    --cov-report=term-missing
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow-running tests

EOF
    echo "   ✅ pytest.ini 創建完成"
else
    echo "   ⏭️  pytest.ini 已存在,跳過"
fi

# requirements/base.txt
mkdir -p requirements
if [ ! -f requirements/base.txt ]; then
    cat > requirements/base.txt << 'EOF'
# Core dependencies
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-asyncio>=0.21.0

# Code quality
black>=23.0.0
ruff>=0.0.280
mypy>=1.4.0

# Optional: EvoMem integration
# chromadb>=0.4.0
# sentence-transformers>=2.2.0

EOF
    echo "   ✅ requirements/base.txt 創建完成"
else
    echo "   ⏭️  requirements/base.txt 已存在,跳過"
fi

echo ""

# Step 3: 初始化 Git
echo "🔧 Step 3/7: 初始化 Git..."
if [ ! -d .git ]; then
    git init
    git add .
    git commit -m "chore: 初始化專案結構

🎯 自動生成:
- 標準目錄結構 (src/, tests/, docs/, data/)
- 基礎文件 (README, .gitignore, pytest.ini)
- requirements/base.txt

🤖 Generated with Claude Code Project Template v4.0"
    echo "   ✅ Git 初始化完成"
else
    echo "   ⏭️  Git 已初始化,跳過"
fi

echo ""

# Step 4: 安裝 Git Hooks
echo "🪝 Step 4/7: 安裝 Git Hooks..."
if [ -f .claude/scripts/pre-commit ]; then
    mkdir -p .git/hooks
    cp .claude/scripts/pre-commit .git/hooks/pre-commit
    chmod +x .git/hooks/pre-commit
    echo "   ✅ Pre-commit hook 安裝完成"
else
    echo "   ⚠️  Pre-commit hook 文件不存在,跳過"
fi

echo ""

# Step 5: 安裝 Python 依賴
echo "📦 Step 5/7: 安裝 Python 依賴..."
if [ -f requirements/base.txt ]; then
    echo "   正在安裝依賴..."
    pip install -r requirements/base.txt -q
    echo "   ✅ 依賴安裝完成"
else
    echo "   ⚠️  requirements/base.txt 不存在,跳過"
fi

echo ""

# Step 6: 設置 EvoMem (Optional)
echo "🧠 Step 6/7: 設置 EvoMem (可選)..."
read -p "   是否啟用 EvoMem 記憶系統? (y/N): " enable_evomem

if [[ "$enable_evomem" =~ ^[Yy]$ ]]; then
    echo "   正在設置 EvoMem..."

    # 安裝 EvoMem 依賴
    pip install chromadb sentence-transformers -q

    # 創建 EvoMem 目錄
    mkdir -p data/vectors/semantic_memory

    # 初始化 EvoMem (需要 Python 代碼)
    python3 << 'PYTHON_EOF'
try:
    from chromadb import Client
    from chromadb.config import Settings

    client = Client(Settings(
        chroma_db_impl="duckdb+parquet",
        persist_directory="data/vectors/semantic_memory"
    ))

    # 創建默認 collection
    collection = client.get_or_create_collection(
        name="project_memory",
        metadata={"description": "Project knowledge base"}
    )

    print("   ✅ EvoMem 初始化完成")

except ImportError:
    print("   ⚠️  EvoMem 依賴未安裝,請手動執行: pip install chromadb sentence-transformers")
except Exception as e:
    print(f"   ⚠️  EvoMem 初始化失敗: {e}")
PYTHON_EOF

else
    echo "   ⏭️  跳過 EvoMem 設置"
fi

echo ""

# Step 7: 生成首個 Checkpoint
echo "📊 Step 7/7: 生成首個 Checkpoint..."

CHECKPOINT_FILE="data/stage_archives/CHECKPOINT_INIT_$(date +%Y%m%d_%H%M%S).md"

cat > "$CHECKPOINT_FILE" << 'EOF'
# Checkpoint: Project Initialization

**Stage**: Project Init
**Timestamp**: $(date -Iseconds)
**Status**: ✅ Completed

---

## 📋 Summary

專案已成功初始化,具備完整的開發環境與工作流程支援。

### 已完成

- ✅ 標準目錄結構 (src/, tests/, docs/, data/)
- ✅ 基礎文件 (README, .gitignore, pytest.ini)
- ✅ Git 版本控制初始化
- ✅ Pre-commit hooks 安裝
- ✅ Python 依賴安裝
- ✅ EvoMem 記憶系統 (可選)

---

## 🎯 Next Steps

### Stage 1: Pre-Business (前商業階段)

如果需要完整的商業分析:

1. **產業研究** - 召喚 小研 (xiaoyan-research.md)
2. **市場策略** - 召喚 小市 (xiaoshi-market.md)
3. **產品規劃** - 召喚 小品 (xiaopin-product.md)
4. **UX/UI 設計** - 召喚 小界 (xiaojie-ux.md)

### Stage 2: SBE Workshop (需求工作坊)

如果直接開始開發:

1. **需求定義** - 召喚 小質 (xiaozhi-quality.md)
2. **編寫 .feature 文件** - 使用 Gherkin 語法
3. **範例**: `features/calculator.feature`

### Stage 3: TDD Cycle (測試驅動開發)

1. **🔴 Red** - 寫失敗測試 (小質)
2. **🟢 Green** - 最小實作 (小程)
3. **🔵 Refactor** - 優化代碼 (小程)

---

## 📊 Token Statistics

- Checkpoint tokens: ~800
- Compression rate: N/A (initial state)

---

## 🔗 References

- [CLAUDE.md](.claude/CLAUDE.md) - 完整工作流程
- [Agents](. claude/agents/) - 所有可用 Agent
- [Templates](.claude/templates/) - 文檔模板

---

**🚀 Ready to start development!**
EOF

echo "   ✅ Checkpoint 創建完成: $CHECKPOINT_FILE"
echo ""

# Final Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 專案初始化完成!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📁 目錄結構:"
tree -L 2 -I '__pycache__|*.pyc|.git' || ls -la
echo ""
echo "📚 下一步:"
echo "   1. 閱讀 .claude/CLAUDE.md 了解工作流程"
echo "   2. 開始 SBE Workshop 或直接進入 TDD"
echo "   3. 召喚相應 Agent 開始開發"
echo ""
echo "🎯 召喚 Agent 範例:"
echo "   - 需求工作坊: @.claude/agents/xiaozhi-quality.md"
echo "   - 開始開發: @.claude/agents/xiaocheng-developer.md"
echo "   - 記憶查詢: @.claude/agents/xiaoji-memory-keeper.md"
echo ""
echo "🚀 Happy coding!"
