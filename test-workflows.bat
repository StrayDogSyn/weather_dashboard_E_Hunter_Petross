@echo off
REM GitHub Actions Workflow Tester for Weather Dashboard
REM Requires GitHub CLI to be installed and authenticated

echo.
echo 🌤️ Weather Dashboard - GitHub Actions Workflow Tester
echo =========================================================
echo.

REM Check if GitHub CLI is available
gh --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ GitHub CLI not found. Please install it first:
    echo    winget install GitHub.cli
    echo.
    pause
    exit /b 1
)

REM Check authentication
gh auth status >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Not authenticated with GitHub. Please run:
    echo    gh auth login
    echo.
    pause
    exit /b 1
)

echo ✅ GitHub CLI is installed and authenticated
echo.

REM Show menu
:menu
echo Available commands:
echo.
echo [1] List all workflows
echo [2] Run quick test (basic)
echo [3] Run quick test (full)
echo [4] Run CI/CD pipeline
echo [5] Watch recent workflow runs
echo [6] Exit
echo.
set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" goto list_workflows
if "%choice%"=="2" goto quick_test_basic
if "%choice%"=="3" goto quick_test_full
if "%choice%"=="4" goto run_cicd
if "%choice%"=="5" goto watch_runs
if "%choice%"=="6" goto exit
goto menu

:list_workflows
echo.
echo 📋 Available workflows:
gh workflow list
echo.
pause
goto menu

:quick_test_basic
echo.
echo 🚀 Running quick test (basic validation)...
gh workflow run quick-test.yml --ref main -f test_type=basic
if %errorlevel%==0 (
    echo ✅ Workflow triggered successfully!
    echo Run option [5] to watch progress
) else (
    echo ❌ Failed to trigger workflow
)
echo.
pause
goto menu

:quick_test_full
echo.
echo 🚀 Running quick test (full test suite)...
gh workflow run quick-test.yml --ref main -f test_type=full
if %errorlevel%==0 (
    echo ✅ Workflow triggered successfully!
    echo Run option [5] to watch progress
) else (
    echo ❌ Failed to trigger workflow
)
echo.
pause
goto menu

:run_cicd
echo.
echo 🚀 Running CI/CD pipeline...
gh workflow run ci-cd.yml --ref main
if %errorlevel%==0 (
    echo ✅ Workflow triggered successfully!
    echo Run option [5] to watch progress
) else (
    echo ❌ Failed to trigger workflow
)
echo.
pause
goto menu

:watch_runs
echo.
echo 👀 Recent workflow runs:
gh run list --limit 10
echo.
echo To watch a specific run: gh run watch [RUN_ID]
echo.
pause
goto menu

:exit
echo.
echo 👋 Goodbye!
exit /b 0
