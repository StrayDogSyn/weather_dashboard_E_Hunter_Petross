# Branch Protection & Collaboration Guidelines

## 🔒 Protected Branches

### Main Branch (`main`)

The `main` branch contains production-ready code and is protected with the following rules:

- ❌ **No direct pushes** - All changes must come via Pull Request
- ✅ **Require pull request reviews** - At least 1 approval required
- ✅ **Require status checks** - All CI/CD checks must pass
- ✅ **Require branches to be up to date** - Feature branch must be current
- ✅ **Include administrators** - Rules apply to all users

## 🚀 Development Workflow

### Current Active Branches

- **`main`** - Protected production branch
- **`feature/week13-enhancements`** - Week 13 development work

### Pull Request Template

When creating a Pull Request, please include:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Code refactoring

## Testing
- [ ] Tests added/updated
- [ ] All tests passing
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes
```

## 📋 Code Review Guidelines

### For Reviewers

- Review code for functionality, security, and maintainability
- Check that tests adequately cover new functionality
- Verify documentation is updated appropriately
- Ensure code follows project conventions

### For Contributors

- Keep pull requests focused and small when possible
- Write clear commit messages
- Include tests for new functionality
- Update documentation as needed
- Respond to review feedback promptly

## 🛡️ Repository Settings

### Branch Protection Rules

To maintain code quality and prevent main branch corruption:

1. Navigate to **Settings > Branches** in GitHub
2. Add protection rule for `main` branch:
   - Require pull request reviews before merging
   - Require status checks to pass before merging
   - Require branches to be up to date before merging
   - Include administrators in restrictions

### Status Checks

Future CI/CD integration will include:

- Code quality checks (Black, Flake8)
- Type checking (MyPy)
- Test suite execution
- Security scanning

---

**Last Updated**: July 11, 2025  
**For Questions**: Contact repository owner or create an issue
