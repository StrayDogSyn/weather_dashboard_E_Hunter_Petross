# Weather Dashboard - GitHub CLI Setup and Workflow Testing
# PowerShell script for Windows users

param(
    [Parameter(Position=0)]
    [string]$Action = "help",
    
    [Parameter(Position=1)]
    [string]$WorkflowName = "",
    
    [Parameter(Position=2)]
    [string]$Branch = "main"
)

function Write-Header {
    Write-Host "🌤️ Weather Dashboard - GitHub CLI & Workflow Manager" -ForegroundColor Cyan
    Write-Host "=" * 60 -ForegroundColor Gray
}

function Test-GitHubCLI {
    try {
        $version = gh --version 2>$null
        if ($version) {
            Write-Host "✅ GitHub CLI is installed: $($version[0])" -ForegroundColor Green
            return $true
        }
    }
    catch {
        Write-Host "❌ GitHub CLI not found" -ForegroundColor Red
        return $false
    }
    return $false
}

function Install-GitHubCLI {
    Write-Host "🚀 Installing GitHub CLI..." -ForegroundColor Yellow
    
    # Try winget first
    try {
        Write-Host "Attempting installation via winget..." -ForegroundColor Gray
        winget install GitHub.cli
        Write-Host "✅ GitHub CLI installed successfully!" -ForegroundColor Green
        Write-Host "⚠️ Please restart your terminal and run 'gh auth login'" -ForegroundColor Yellow
    }
    catch {
        Write-Host "❌ winget installation failed. Trying alternative methods..." -ForegroundColor Red
        
        # Try chocolatey
        if (Get-Command choco -ErrorAction SilentlyContinue) {
            Write-Host "Attempting installation via Chocolatey..." -ForegroundColor Gray
            choco install gh
        }
        else {
            Write-Host "Manual installation required:" -ForegroundColor Yellow
            Write-Host "1. Visit: https://cli.github.com/" -ForegroundColor White
            Write-Host "2. Download and run the Windows installer" -ForegroundColor White
            Write-Host "3. Restart your terminal" -ForegroundColor White
            Write-Host "4. Run: gh auth login" -ForegroundColor White
        }
    }
}

function Test-Authentication {
    try {
        $authStatus = gh auth status 2>&1
        if ($authStatus -match "Logged in") {
            Write-Host "✅ Authenticated with GitHub" -ForegroundColor Green
            return $true
        }
        else {
            Write-Host "❌ Not authenticated with GitHub" -ForegroundColor Red
            Write-Host "Run: gh auth login" -ForegroundColor Yellow
            return $false
        }
    }
    catch {
        Write-Host "❌ Authentication check failed" -ForegroundColor Red
        return $false
    }
}

function Show-Workflows {
    Write-Host "📋 Available Workflows:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  • ci-cd          - Main CI/CD pipeline (comprehensive testing)" -ForegroundColor White
    Write-Host "  • quick-test     - Quick validation tests (basic, full, integration)" -ForegroundColor White  
    Write-Host "  • pr-validation  - PR validation (triggers automatically)" -ForegroundColor White
    Write-Host ""
    Write-Host "Usage Examples:" -ForegroundColor Yellow
    Write-Host "  .\workflow-manager.ps1 run quick-test" -ForegroundColor Gray
    Write-Host "  .\workflow-manager.ps1 run ci-cd main" -ForegroundColor Gray
    Write-Host "  .\workflow-manager.ps1 watch" -ForegroundColor Gray
}

function Run-Workflow {
    param($WorkflowName, $Branch)
    
    if (-not (Test-GitHubCLI)) {
        Write-Host "❌ GitHub CLI required. Run: .\workflow-manager.ps1 install" -ForegroundColor Red
        return
    }
    
    if (-not (Test-Authentication)) {
        return
    }
    
    $workflowFile = switch ($WorkflowName) {
        "ci-cd" { "ci-cd.yml" }
        "quick-test" { "quick-test.yml" }
        "pr-validation" { "pr-validation.yml" }
        default { 
            Write-Host "❌ Unknown workflow: $WorkflowName" -ForegroundColor Red
            Show-Workflows
            return 
        }
    }
    
    Write-Host "🚀 Triggering workflow: $WorkflowName" -ForegroundColor Yellow
    Write-Host "📁 File: $workflowFile" -ForegroundColor Gray
    Write-Host "🌿 Branch: $Branch" -ForegroundColor Gray
    
    try {
        if ($WorkflowName -eq "quick-test") {
            $testType = Read-Host "Enter test type (basic/full/integration) [basic]"
            if ([string]::IsNullOrEmpty($testType)) { $testType = "basic" }
            
            gh workflow run $workflowFile --ref $Branch -f test_type=$testType
        }
        else {
            gh workflow run $workflowFile --ref $Branch
        }
        
        Write-Host "✅ Workflow triggered successfully!" -ForegroundColor Green
        Write-Host "💡 To watch progress: .\workflow-manager.ps1 watch" -ForegroundColor Cyan
    }
    catch {
        Write-Host "❌ Failed to trigger workflow: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Watch-Workflows {
    if (-not (Test-GitHubCLI)) {
        Write-Host "❌ GitHub CLI required. Run: .\workflow-manager.ps1 install" -ForegroundColor Red
        return
    }
    
    Write-Host "👀 Recent workflow runs:" -ForegroundColor Cyan
    try {
        gh run list --limit 10
    }
    catch {
        Write-Host "❌ Failed to fetch workflow runs" -ForegroundColor Red
    }
}

function Test-Local {
    Write-Host "🧪 Testing application locally..." -ForegroundColor Yellow
    
    # Test Python
    try {
        $pythonVersion = python --version 2>&1
        Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Python not found" -ForegroundColor Red
        return
    }
    
    # Test basic imports
    try {
        python -c "from src.models.weather_models import CurrentWeather; print('✅ Basic imports work')"
    }
    catch {
        Write-Host "❌ Import test failed" -ForegroundColor Red
    }
    
    # Test TKinter
    try {
        python -c "import tkinter; print('✅ TKinter available')"
    }
    catch {
        Write-Host "❌ TKinter not available" -ForegroundColor Red
    }
    
    # Test main application
    Write-Host "🎯 Testing main application startup..." -ForegroundColor Yellow
    Write-Host "Note: This will launch the GUI briefly for testing" -ForegroundColor Gray
}

function Show-Help {
    Write-Host "Commands:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  install      - Install GitHub CLI" -ForegroundColor White
    Write-Host "  auth         - Check authentication status" -ForegroundColor White
    Write-Host "  list         - List available workflows" -ForegroundColor White
    Write-Host "  run <name>   - Run a specific workflow" -ForegroundColor White
    Write-Host "  watch        - Watch recent workflow runs" -ForegroundColor White
    Write-Host "  test-local   - Test application locally" -ForegroundColor White
    Write-Host "  help         - Show this help" -ForegroundColor White
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Yellow
    Write-Host "  .\workflow-manager.ps1 install" -ForegroundColor Gray
    Write-Host "  .\workflow-manager.ps1 run quick-test" -ForegroundColor Gray
    Write-Host "  .\workflow-manager.ps1 run ci-cd main" -ForegroundColor Gray
    Write-Host "  .\workflow-manager.ps1 watch" -ForegroundColor Gray
}

# Main execution
Write-Header

switch ($Action.ToLower()) {
    "install" { Install-GitHubCLI }
    "auth" { Test-Authentication }
    "list" { Show-Workflows }
    "run" { 
        if ([string]::IsNullOrEmpty($WorkflowName)) {
            Write-Host "❌ Workflow name required. Available: ci-cd, quick-test" -ForegroundColor Red
            Show-Workflows
        }
        else {
            Run-Workflow $WorkflowName $Branch
        }
    }
    "watch" { Watch-Workflows }
    "test-local" { Test-Local }
    "help" { Show-Help }
    default { 
        Write-Host "❌ Unknown action: $Action" -ForegroundColor Red
        Show-Help 
    }
}
