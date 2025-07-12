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

- Pull request opened, synchronized, or reopened

**Jobs:**

- **Validate PR**: Code formatting, linting, testing, startup validation
- **Comment**: Automated PR comment with results

**Features:**

- Automatic code quality checks
- Test execution validation
- Application startup verification
- PR status comments with results

## 🛠️ Workflow Testing

### Using the Python Test Script

The `workflow_test.py` script provides an easy interface for triggering workflows:

```bash
# List available workflows
python workflow_test.py list

# Run specific workflow
python workflow_test.py quick-test

# Run on specific branch
python workflow_test.py ci-cd develop

# Test all workflows
python workflow_test.py test-all

# Watch workflow progress
python workflow_test.py watch
```

### Direct GitHub CLI Commands

```bash
# List workflows
gh workflow list

# Run CI/CD pipeline
gh workflow run ci-cd.yml --ref main

# Run quick test with basic type
gh workflow run quick-test.yml --ref main -f test_type=basic

# Watch running workflows
gh run list

# Watch specific workflow run
gh run watch [RUN_ID]

# View workflow logs
gh run view [RUN_ID] --log
```

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
