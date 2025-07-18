# GitHub Actions CI/CD Workflows

This document describes the CI/CD workflows implemented for the Weather Dashboard project.

## 🚀 Available Workflows

### 1. Main CI/CD Pipeline (`ci-cd.yml`)

**Triggers:**

- Push to `main` or `develop` branches
- Pull requests to `main` branch  
- Manual dispatch with environment selection

**Jobs:**

- **Lint**: Code formatting, import sorting, linting, type checking
- **Test**: Cross-platform testing (Ubuntu, Windows, macOS) with Python 3.9-3.12
- **Security**: Bandit security scanning and Safety dependency checks
- **Integration Test**: GUI and full application testing
- **Build**: PyInstaller executable creation for all platforms
- **Documentation**: API documentation generation
- **Deploy**: Staging (develop branch) and Production (main branch) deployment
- **Notify**: Results notification

**Usage:**

```bash
# Trigger manually with environment selection
gh workflow run ci-cd.yml --ref main

# Trigger with specific environment
gh workflow run ci-cd.yml --ref main -f test_environment=production
```

### 2. Quick Test (`quick-test.yml`)

**Triggers:**

- Manual dispatch only

**Jobs:**

- **Quick Test**: Fast validation with configurable test types

**Test Types:**

- `basic`: Import and basic functionality tests
- `full`: Complete pytest suite
- `integration`: GUI and integration testing

**Usage:**

```bash
# Basic test
gh workflow run quick-test.yml --ref main -f test_type=basic

# Full test suite
gh workflow run quick-test.yml --ref main -f test_type=full

# Integration tests
gh workflow run quick-test.yml --ref main -f test_type=integration
```

### 3. PR Validation (`pr-validation.yml`)

**Triggers:**

- Pull requests to `main` or `develop` branches
- PR events: opened, synchronize, reopened

**Jobs:**

- **Validate PR**: Comprehensive validation including:
  - Code formatting check (Black)
  - Linting (Flake8)
  - Unit tests (Pytest)
  - Application startup test
  - Automated PR comment with results

**Permissions:**

The workflow requires the following GitHub permissions:

- `contents: read` - Read repository contents
- `issues: write` - Create/update PR comments
- `pull-requests: write` - Interact with pull requests

**Features:**

- ✅ Automatic code quality validation
- ✅ Comprehensive test execution
- ✅ Application startup verification
- ✅ Smart PR commenting (updates existing bot comments)
- ✅ Error handling and graceful degradation

**Comment Format:**

```markdown
## 🤖 PR Validation Results

**Status**: ✅ Passed / ❌ Failed

### Checks Performed:
- ✅ Code formatting (Black)
- ✅ Linting (Flake8)
- ✅ Unit tests (Pytest)
- ✅ Application startup test

🎉 All checks passed! This PR is ready for review.
```

### 4. Python App CI (`python-app.yml`)

**Note:** This is a legacy workflow that may be deprecated in favor of the main CI/CD pipeline.

## ⚙️ Configuration & Troubleshooting

### GitHub Permissions

If you encounter permission errors like:

```text
RequestError [HttpError]: Resource not accessible by integration
```

This typically means the workflow lacks proper permissions. Ensure workflows include:

```yaml
permissions:
  contents: read
  issues: write
  pull-requests: write
```

### Repository Settings

For workflows to function properly, verify these repository settings:

1. **Actions Permissions**: Go to Settings → Actions → General
   - Allow GitHub Actions to create and approve pull requests
   - Allow GitHub Actions to submit approving reviews

2. **Token Permissions**: Ensure `GITHUB_TOKEN` has sufficient permissions
   - Read access to metadata
   - Write access to issues and pull requests

## 📋 Prerequisites

### GitHub CLI Installation

**Windows:**

```powershell
winget install GitHub.cli
```

**macOS:**

```bash
brew install gh
```

**Linux:**

```bash
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh
```

### Authentication

```bash
# Login to GitHub
gh auth login

# Verify authentication
gh auth status
```

## 🔧 Workflow Configuration

### Environment Variables

Workflows use these environment variables:

- `OPENWEATHER_API_KEY`: OpenWeatherMap API key (set in repository secrets)
- `WEATHER_DEFAULT_CITY`: Default city for testing
- `WEATHER_CACHE_DURATION`: Cache duration in seconds
- `WEATHER_LOG_LEVEL`: Logging level

### Repository Secrets

Set these secrets in your GitHub repository:

1. Go to Settings > Secrets and variables > Actions
2. Add repository secrets:
   - `OPENWEATHER_API_KEY`: Your OpenWeatherMap API key

### Branch Protection

Recommended branch protection rules for `main`:

- Require pull request reviews
- Require status checks (PR Validation workflow)
- Require up-to-date branches
- Restrict pushes to main branch

## 📊 Monitoring and Debugging

### Workflow Status

```bash
# View recent runs
gh run list

# View specific run details
gh run view [RUN_ID]

# Download run logs
gh run download [RUN_ID]

# Re-run failed jobs
gh run rerun [RUN_ID] --failed
```

### Common Issues

#### 1. Import Errors

- Ensure all dependencies are in `requirements.txt`
- Check Python path configuration

#### 2. GUI Testing Failures

- Virtual display (xvfb) is configured for Linux
- Windows and macOS have native GUI support

#### 3. API Key Issues

- Verify repository secrets are set correctly
- Check environment variable names

#### 4. Build Failures

- PyInstaller may need specific configurations
- Check platform-specific build requirements

## 🎯 Best Practices

### Workflow Design

- Keep jobs focused and independent
- Use matrix strategies for cross-platform testing
- Implement proper caching for dependencies
- Use artifacts for build outputs

### Security

- Never commit API keys or secrets
- Use repository secrets for sensitive data
- Implement security scanning (Bandit, Safety)
- Validate inputs in workflow_dispatch events

### Performance

- Cache pip dependencies
- Use specific Python versions
- Parallel job execution where possible
- Conditional job execution based on changes

### Maintenance

- Keep workflow dependencies updated
- Monitor workflow execution times
- Review and update security policies
- Document workflow changes

## 📈 Metrics and Reporting

The workflows provide:

- **Code Coverage**: Via Codecov integration
- **Security Reports**: Bandit and Safety scan results
- **Build Artifacts**: Executable files for all platforms
- **Documentation**: Generated API docs
- **Test Results**: Detailed pytest reports

Access these through the GitHub Actions interface or download as artifacts.
