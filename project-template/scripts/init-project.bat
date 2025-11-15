@echo off
REM 新專案初始化腳本 (Windows 版本)
REM Version: 4.0
REM Usage: init-project.bat

setlocal enabledelayedexpansion

echo ================================================================
echo 🚀 新專案初始化開始 (Project Initialization)
echo ================================================================
echo.

REM Step 1: 創建標準目錄結構
echo 📁 Step 1/7: 創建目錄結構...
mkdir src\backend 2>nul
mkdir src\frontend 2>nul
mkdir src\shared 2>nul
mkdir tests\unit 2>nul
mkdir tests\integration 2>nul
mkdir tests\e2e 2>nul
mkdir docs\research 2>nul
mkdir docs\product 2>nul
mkdir docs\design 2>nul
mkdir docs\analytics 2>nul
mkdir docs\technical 2>nul
mkdir data\handoffs 2>nul
mkdir data\stage_archives 2>nul
mkdir data\reviews 2>nul
mkdir data\vectors 2>nul
mkdir features 2>nul
mkdir scripts\ci 2>nul
mkdir scripts\deployment 2>nul

echo    ✅ 目錄結構創建完成
echo.

REM Step 2: 生成基礎文件
echo 📄 Step 2/7: 生成基礎文件...

REM README.md
if not exist README.md (
    (
        echo # Project Name
        echo.
        echo **Version**: 0.1.0
        echo **Status**: 🚧 In Development
        echo.
        echo ## 📋 Description
        echo.
        echo [Brief description of your project]
        echo.
        echo ## 🚀 Quick Start
        echo.
        echo ```bash
        echo # Install dependencies
        echo pip install -r requirements/base.txt
        echo.
        echo # Run tests
        echo pytest tests/ -v
        echo.
        echo # Start development server
        echo python src/main.py
        echo ```
        echo.
        echo ## 📚 Documentation
        echo.
        echo - [Architecture](docs/technical/ARCHITECTURE.md^)
        echo - [API Reference](docs/technical/API.md^)
        echo - [Development Guide](.claude/CLAUDE.md^)
        echo.
        echo ## 🔧 Development Workflow
        echo.
        echo This project follows TDD + Multi-Agent workflow.
        echo.
        echo See [CLAUDE.md](.claude/CLAUDE.md^) for full workflow details.
    ) > README.md
    echo    ✅ README.md 創建完成
) else (
    echo    ⏭️  README.md 已存在,跳過
)

REM .gitignore
if not exist .gitignore (
    (
        echo # Python
        echo __pycache__/
        echo *.py[cod]
        echo *$py.class
        echo *.so
        echo .Python
        echo env/
        echo venv/
        echo ENV/
        echo build/
        echo dist/
        echo *.egg-info/
        echo.
        echo # Testing
        echo .pytest_cache/
        echo .coverage
        echo htmlcov/
        echo.
        echo # IDEs
        echo .vscode/
        echo .idea/
        echo *.swp
        echo.
        echo # OS
        echo .DS_Store
        echo Thumbs.db
        echo.
        echo # Environment
        echo .env
        echo .env.local
        echo.
        echo # Data
        echo data/vectors/
        echo data/handoffs/*.json
        echo data/reviews/
        echo.
        echo # Logs
        echo *.log
        echo logs/
    ) > .gitignore
    echo    ✅ .gitignore 創建完成
) else (
    echo    ⏭️  .gitignore 已存在,跳過
)

REM pytest.ini
if not exist pytest.ini (
    (
        echo [pytest]
        echo testpaths = tests
        echo python_files = test_*.py
        echo python_classes = Test*
        echo python_functions = test_*
        echo addopts =
        echo     -v
        echo     --strict-markers
        echo     --tb=short
        echo     --cov=src
        echo     --cov-report=html
        echo     --cov-report=term-missing
        echo markers =
        echo     unit: Unit tests
        echo     integration: Integration tests
        echo     e2e: End-to-end tests
    ) > pytest.ini
    echo    ✅ pytest.ini 創建完成
) else (
    echo    ⏭️  pytest.ini 已存在,跳過
)

REM requirements/base.txt
mkdir requirements 2>nul
if not exist requirements\base.txt (
    (
        echo # Core dependencies
        echo pytest^>=7.4.0
        echo pytest-cov^>=4.1.0
        echo pytest-asyncio^>=0.21.0
        echo.
        echo # Code quality
        echo black^>=23.0.0
        echo ruff^>=0.0.280
        echo mypy^>=1.4.0
        echo.
        echo # Optional: EvoMem integration
        echo # chromadb^>=0.4.0
        echo # sentence-transformers^>=2.2.0
    ) > requirements\base.txt
    echo    ✅ requirements/base.txt 創建完成
) else (
    echo    ⏭️  requirements/base.txt 已存在,跳過
)

echo.

REM Step 3: 初始化 Git
echo 🔧 Step 3/7: 初始化 Git...
if not exist .git (
    git init
    git add .
    git commit -m "chore: 初始化專案結構"
    echo    ✅ Git 初始化完成
) else (
    echo    ⏭️  Git 已初始化,跳過
)

echo.

REM Step 4: 安裝 Git Hooks
echo 🪝 Step 4/7: 安裝 Git Hooks...
if exist .claude\scripts\pre-commit (
    mkdir .git\hooks 2>nul
    copy .claude\scripts\pre-commit .git\hooks\pre-commit >nul
    echo    ✅ Pre-commit hook 安裝完成
) else (
    echo    ⚠️  Pre-commit hook 文件不存在,跳過
)

echo.

REM Step 5: 安裝 Python 依賴
echo 📦 Step 5/7: 安裝 Python 依賴...
if exist requirements\base.txt (
    echo    正在安裝依賴...
    pip install -q -r requirements\base.txt
    echo    ✅ 依賴安裝完成
) else (
    echo    ⚠️  requirements/base.txt 不存在,跳過
)

echo.

REM Step 6: 設置 EvoMem
echo 🧠 Step 6/7: 設置 EvoMem (可選^)...
set /p enable_evomem="   是否啟用 EvoMem 記憶系統? (y/N): "

if /i "%enable_evomem%"=="y" (
    echo    正在設置 EvoMem...
    pip install -q chromadb sentence-transformers
    mkdir data\vectors\semantic_memory 2>nul
    echo    ✅ EvoMem 依賴安裝完成
) else (
    echo    ⏭️  跳過 EvoMem 設置
)

echo.

REM Step 7: 生成首個 Checkpoint
echo 📊 Step 7/7: 生成首個 Checkpoint...

for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c%%a%%b)
for /f "tokens=1-2 delims=/:" %%a in ('time /t') do (set mytime=%%a%%b)
set TIMESTAMP=%mydate%_%mytime%

set CHECKPOINT_FILE=data\stage_archives\CHECKPOINT_INIT_%TIMESTAMP%.md

(
    echo # Checkpoint: Project Initialization
    echo.
    echo **Stage**: Project Init
    echo **Timestamp**: %date% %time%
    echo **Status**: ✅ Completed
    echo.
    echo ---
    echo.
    echo ## 📋 Summary
    echo.
    echo 專案已成功初始化,具備完整的開發環境與工作流程支援。
    echo.
    echo ### 已完成
    echo.
    echo - ✅ 標準目錄結構
    echo - ✅ 基礎文件
    echo - ✅ Git 版本控制初始化
    echo - ✅ Pre-commit hooks 安裝
    echo - ✅ Python 依賴安裝
    echo.
    echo ---
    echo.
    echo ## 🎯 Next Steps
    echo.
    echo 1. 閱讀 .claude/CLAUDE.md 了解工作流程
    echo 2. 開始 SBE Workshop 或直接進入 TDD
    echo 3. 召喚相應 Agent 開始開發
    echo.
    echo **🚀 Ready to start development!**
) > "%CHECKPOINT_FILE%"

echo    ✅ Checkpoint 創建完成: %CHECKPOINT_FILE%
echo.

REM Final Summary
echo ================================================================
echo ✅ 專案初始化完成!
echo ================================================================
echo.
echo 📚 下一步:
echo    1. 閱讀 .claude\CLAUDE.md 了解工作流程
echo    2. 開始 SBE Workshop 或直接進入 TDD
echo    3. 召喚相應 Agent 開始開發
echo.
echo 🎯 召喚 Agent 範例:
echo    - 需求工作坊: @.claude\agents\xiaozhi-quality.md
echo    - 開始開發: @.claude\agents\xiaocheng-developer.md
echo    - 記憶查詢: @.claude\agents\xiaoji-memory-keeper.md
echo.
echo 🚀 Happy coding!

pause
