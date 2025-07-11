# Git Workflow & Branching Strategy

## 🔒 Branch Protection

### Main Branch Protection

The `main` branch is **protected** and should never receive direct commits. All changes must go through the feature branch workflow and pull request process.

### Current Branch Structure

- **`main`** - Production-ready code, protected branch
- **`feature/week13-enhancements`** - Current development branch
- **`feature/*`** - Feature development branches (create as needed)

## 🚀 Development Workflow

### 1. Starting New Work

```bash
# Always start from main
git checkout main
git pull origin main

# Create a new feature branch
git checkout -b feature/descriptive-name
```

### 2. During Development

```bash
# Regular commits on feature branch
git add .
git commit -m "feat: add new functionality"

# Push to remote feature branch
git push -u origin feature/descriptive-name
```

### 3. Finishing Work

```bash
# Create Pull Request on GitHub
# Review and merge through GitHub interface

# After merge, clean up
git checkout main
git pull origin main
git branch -d feature/descriptive-name
```

## 📋 Branch Naming Conventions

### Feature Branches

- `feature/week13-enhancements` - Week 13 submission enhancements
- `feature/ui-improvements` - User interface improvements
- `feature/api-enhancements` - API integration improvements
- `feature/database-optimization` - Database performance work

### Bug Fix Branches

- `bugfix/weather-api-timeout` - Fix API timeout issues
- `bugfix/database-connection` - Fix database connectivity

### Documentation Branches

- `docs/api-documentation` - API documentation updates
- `docs/user-guide` - User guide improvements

## 🛡️ Protection Rules

### Main Branch Rules

1. **No Direct Pushes** - All changes via Pull Request
2. **Require Reviews** - At least one approval required
3. **Status Checks** - All CI/CD checks must pass
4. **Up-to-date Branch** - Feature branch must be current with main

### Pull Request Requirements

- **Descriptive Title** - Clear summary of changes
- **Detailed Description** - What, why, and how of changes
- **Link Issues** - Reference related issues if applicable
- **Test Coverage** - Include tests for new functionality

## 🔄 Collaboration Workflow

### For Team Members

1. **Clone Repository**:

   ```bash
   git clone https://github.com/StrayDogSyn/weather_dashboard_E_Hunter_Petross.git
   cd weather_dashboard_E_Hunter_Petross
   ```

2. **Set Up Development Environment**:

   ```bash
   # Install dependencies
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   
   # Set up environment
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Create Feature Branch**:

   ```bash
   git checkout -b feature/your-feature
   ```

4. **Make Changes and Test**:

   ```bash
   # Make your changes
   python -m pytest tests/
   black src/ tests/
   flake8 src/ tests/
   ```

5. **Submit Pull Request**:
   - Push branch to GitHub
   - Create Pull Request
   - Request review
   - Address feedback
   - Merge when approved

### For External Contributors

1. **Fork Repository** on GitHub
2. **Clone Your Fork**:

   ```bash
   git clone https://github.com/YOUR_USERNAME/weather_dashboard_E_Hunter_Petross.git
   ```

3. **Add Upstream Remote**:

   ```bash
   git remote add upstream https://github.com/StrayDogSyn/weather_dashboard_E_Hunter_Petross.git
   ```

4. **Keep Fork Updated**:

   ```bash
   git fetch upstream
   git checkout main
   git merge upstream/main
   git push origin main
   ```

## 🚨 Emergency Procedures

### Hotfix for Critical Issues

For critical production issues that need immediate attention:

1. **Create Hotfix Branch from Main**:

   ```bash
   git checkout main
   git pull origin main
   git checkout -b hotfix/critical-issue-name
   ```

2. **Make Minimal Fix**:

   ```bash
   # Make only the necessary changes
   git add .
   git commit -m "hotfix: critical issue description"
   git push -u origin hotfix/critical-issue-name
   ```

3. **Fast-Track Pull Request**:
   - Create PR with "HOTFIX" label
   - Get immediate review
   - Merge ASAP
   - Delete hotfix branch

### Rollback Procedures

If a merge causes issues:

1. **Identify Problem Commit**:

   ```bash
   git log --oneline
   ```

2. **Create Revert**:

   ```bash
   git revert <commit-hash>
   git push origin main
   ```

## 📊 Branch Status

### Current Active Branches

- ✅ `main` - Stable, production-ready
- 🚧 `feature/week13-enhancements` - Week 13 development work

### Branch Policies

- **Automatic Deletion** - Feature branches deleted after merge
- **Stale Branch Cleanup** - Inactive branches removed monthly
- **Main Protection** - Enforced via GitHub branch protection rules

## 🔧 Tools & Integration

### GitHub Integration

- **Branch Protection Rules** - Configured in repository settings
- **Status Checks** - CI/CD pipeline integration
- **Code Review** - Required reviewers and approvals

### Local Git Configuration

Recommended git configuration for this project:

```bash
# Set up commit signing (optional but recommended)
git config user.signingkey YOUR_GPG_KEY
git config commit.gpgsign true

# Set up helpful aliases
git config alias.co checkout
git config alias.br branch
git config alias.ci commit
git config alias.st status
```

---

**Last Updated**: July 11, 2025  
**Current Branch**: `feature/week13-enhancements`  
**Next Review**: When merging to main
