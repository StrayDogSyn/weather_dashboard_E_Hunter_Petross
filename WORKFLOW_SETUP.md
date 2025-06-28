# GitHub CLI Installation and Workflow Testing Guide

## 🎯 IMMEDIATE NEXT STEPS

**Current Status:** ✅ GitHub CLI installed, ✅ Authentication working, ✅ Workflows detected!

**Ready to test workflows! Available workflows:**
- Weather Dashboard CI/CD (ID: 171239379)
- PR Validation (ID: 171239380) 
- Python application (ID: 171239268)
- Quick Test (ID: 171239381)

**Run your first workflow test now:**

1. **Quick basic test:**
   ```powershell
   gh workflow run quick-test.yml --ref main -f test_type=basic
   ```

2. **Watch the progress:**
   ```powershell
   gh run list
   gh run watch
   ```

3. **Run full CI/CD pipeline:**
   ```powershell
   gh workflow run ci-cd.yml --ref main
   ```

**OR use the batch script:**
```powershell
.\test-workflows.bat
```

---

## 🚀 Quick Installation Options

### ✅ GitHub CLI Status: INSTALLED
GitHub CLI version 2.74.2 is already installed on your system!

### 🔐 Next Step: Authentication Required
You need to authenticate with GitHub to use workflows:

```powershell
# Login to GitHub (run this command)
gh auth login
```

### Alternative Installation Methods (if needed)
```powershell
# Windows Package Manager (already completed)
winget install GitHub.cli

# Verify installation
gh --version
```

## 🔐 Authentication Setup

After installation, authenticate with GitHub:

```powershell
# Login to GitHub
gh auth login

# Follow the prompts to:
# 1. Choose GitHub.com
# 2. Choose HTTPS or SSH
# 3. Authenticate via web browser or token

# Verify authentication
gh auth status
```

## 🧪 Testing GitHub Actions Workflows

### Manual Workflow Triggers (Web Interface)

If you prefer not to use CLI, you can trigger workflows manually:

1. **Go to your GitHub repository**
2. **Click on "Actions" tab**
3. **Select a workflow from the left sidebar**
4. **Click "Run workflow" button**
5. **Choose branch and parameters**
6. **Click "Run workflow"**

### Available Workflows for Testing

| Workflow | File | Trigger Method |
|----------|------|----------------|
| **CI/CD Pipeline** | `ci-cd.yml` | Push to main/develop, PR, or manual |
| **Quick Test** | `quick-test.yml` | Manual only |
| **PR Validation** | `pr-validation.yml` | Automatic on PR |

### CLI Commands (After Installation)

```powershell
# List all workflows
gh workflow list

# Run quick test
gh workflow run quick-test.yml --ref main -f test_type=basic

# Run CI/CD pipeline
gh workflow run ci-cd.yml --ref main

# Run with specific environment
gh workflow run ci-cd.yml --ref main -f test_environment=staging

# Watch workflow runs
gh run list

# Watch specific run
gh run watch [RUN_ID]

# View logs
gh run view [RUN_ID] --log
```

## 🔧 Alternative Testing Without CLI

### Method 1: Git Push Triggers

Since the CI/CD workflow triggers on push to main/develop:

```powershell
# Make a small change and push
echo "# Test commit" >> README.md
git add README.md
git commit -m "Test CI/CD workflow trigger"
git push origin main
```

### Method 2: Create Pull Request

The PR validation workflow triggers automatically:

```powershell
# Create a new branch
git checkout -b test-workflow

# Make a change
echo "# Test PR" >> README.md
git add README.md
git commit -m "Test PR workflow"
git push origin test-workflow

# Create PR via web interface at GitHub.com
```

### Method 3: Direct API Calls (Advanced)

Using curl or PowerShell to trigger workflows:

```powershell
# Set variables
$owner = "YOUR_GITHUB_USERNAME"
$repo = "weather_dashboard_E_Hunter_Petross"
$token = "YOUR_GITHUB_TOKEN"

# Trigger workflow
$headers = @{
    "Authorization" = "Bearer $token"
    "Accept" = "application/vnd.github.v3+json"
}

$body = @{
    "ref" = "main"
    "inputs" = @{
        "test_type" = "basic"
    }
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://api.github.com/repos/$owner/$repo/actions/workflows/quick-test.yml/dispatches" -Method POST -Headers $headers -Body $body -ContentType "application/json"
```

## 📊 Monitoring Workflow Results

### Via Web Interface
1. Go to repository → Actions tab
2. View recent runs and their status
3. Click on runs to see detailed logs
4. Download artifacts if needed

### Via CLI (After Installation)
```powershell
# List recent runs
gh run list

# View specific run
gh run view [RUN_ID]

# Download artifacts
gh run download [RUN_ID]

# Re-run failed jobs
gh run rerun [RUN_ID] --failed
```

## 🛠️ Troubleshooting

### Common Issues

**1. GitHub CLI not found after installation**
- Restart your terminal/PowerShell
- Check if `gh` is in your PATH: `where gh`

**2. Authentication fails**
- Ensure you have proper GitHub permissions
- Try `gh auth refresh`
- Use personal access token if needed

**3. Workflow doesn't trigger**
- Check branch name matches workflow configuration
- Verify you have write access to repository
- Check workflow file syntax

**4. Permission denied**
- Ensure repository has Actions enabled
- Check if you have admin/write access
- Verify GitHub token permissions

### Manual Verification

Test your setup without workflows:

```powershell
# Test application locally
python main.py

# Run tests locally
python -m pytest tests/ -v

# Check imports
python -c "from src.models.weather_models import CurrentWeather; print('✅ Imports work')"
```

## 📝 Next Steps

1. **Install GitHub CLI** using one of the methods above
2. **Authenticate** with your GitHub account
3. **Test workflows** using CLI commands or web interface
4. **Monitor results** in GitHub Actions tab
5. **Review logs** and artifacts for any issues

## 🆘 Need Help?

If you encounter issues:
1. Check the GitHub Actions documentation
2. Review workflow logs for error details
3. Test locally first to isolate issues
4. Ensure all dependencies are properly configured

The workflows are designed to be robust and provide detailed feedback about any issues encountered during execution.
