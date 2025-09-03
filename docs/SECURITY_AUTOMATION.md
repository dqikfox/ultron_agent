# Security and Dependency Management Automation

This document describes the automated security and dependency management tools implemented for the Ultron Agent project.

## 🛡️ Automated Security Tools

### Dependency Management

**Dependabot** automatically creates pull requests to update dependencies:
- **Schedule**: Weekly updates on Mondays
- **Groups**: Dependencies are grouped by type (AI/ML, web/API, dev tools, security)
- **Review**: All updates require review before merging
- **Configuration**: `.github/dependabot.yml`

### Security Scanning Tools

#### 1. Bandit (Static Security Analysis)
- **What**: Scans Python code for common security issues
- **When**: Pre-commit hooks and CI pipeline
- **Configuration**: `[tool.bandit]` in `pyproject.toml`
- **Run manually**: `bandit -r . -ll`

#### 2. Safety (Dependency Vulnerability Scanning)
- **What**: Checks Python packages for known vulnerabilities
- **When**: Pre-commit hooks and scheduled weekly scans
- **Run manually**: `safety scan` or `safety check`

#### 3. Semgrep (Pattern-Based Security Scanning)
- **What**: Advanced static analysis for security patterns
- **When**: CI pipeline and scheduled audits
- **Requires**: `SEMGREP_APP_TOKEN` secret (optional)

#### 4. detect-secrets (Secret Detection)
- **What**: Prevents committing secrets to version control
- **When**: Pre-commit hooks
- **Configuration**: `.secrets.baseline`

#### 5. OWASP Dependency Check
- **What**: Comprehensive dependency vulnerability scanning
- **When**: CI pipeline for critical changes
- **Format**: Generates HTML, XML, and JSON reports

## 🔄 Workflows

### CI/CD Security Integration

The main CI workflow (`.github/workflows/ci.yml`) now includes:

1. **Security Scan Job**: Runs before other tests
   - Bandit security scan
   - Safety vulnerability check  
   - Semgrep pattern analysis
   - Uploads security reports as artifacts

2. **Dependency Review**: On pull requests
   - Reviews dependency changes
   - Fails on high-severity vulnerabilities

3. **Enhanced Testing**: Includes security-focused tests
   - `pytest-security` for security-specific test patterns

### Scheduled Security Audits

The security audit workflow (`.github/workflows/security-audit.yml`) runs:

- **Weekly**: Every Monday at 9 AM UTC
- **On-demand**: Manual trigger available
- **Dependency changes**: When requirements files are modified

**Features:**
- Comprehensive vulnerability scanning
- SARIF upload to GitHub Security tab
- Automated issue creation for vulnerabilities
- Security report generation

## 🚀 Getting Started

### 1. Install Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run hooks on all files (first time)
pre-commit run --all-files
```

### 2. Manual Security Scans

```bash
# Install security tools
pip install -e ".[dev]"

# Run individual scans
bandit -r . -ll                    # Static security analysis
safety scan                       # Dependency vulnerabilities  
detect-secrets scan .              # Secret detection
```

### 3. View Security Reports

- **GitHub Security Tab**: View Semgrep SARIF results
- **CI Artifacts**: Download detailed security reports
- **Issues**: Auto-created issues for vulnerabilities

## ⚙️ Configuration

### Security Settings in pyproject.toml

```toml
[tool.bandit]
exclude_dirs = ["tests", "docs", "build", "dist", ".venv", "venv"]
skips = ["B101", "B601"]  # Skip assert_used, paramiko_calls

[tool.safety]  
ignore = []  # Add CVE IDs to ignore specific vulnerabilities
full_report = true
```

### Pre-commit Configuration

The `.pre-commit-config.yaml` includes:
- Code formatting (Black, isort)
- Linting (Ruff)
- Security scanning (Bandit, Safety, detect-secrets)
- Type checking (mypy)
- YAML/Markdown linting

### Dependabot Configuration  

The `.github/dependabot.yml` configures:
- Update schedules and limits
- Dependency grouping
- Auto-assignment and labeling
- Ignore rules for major version updates

## 📊 Security Reports

### Report Types

1. **Bandit Reports**: `bandit-report.json`
   - Static security analysis results
   - Severity levels: High, Medium, Low
   - CWE mappings and remediation links

2. **Safety Reports**: `safety-report.json`
   - Known vulnerability database results
   - CVE details and affected versions
   - Remediation recommendations

3. **SARIF Reports**: `semgrep.sarif`
   - Uploaded to GitHub Security tab
   - Integrates with code scanning alerts
   - Pattern-based security findings

### Viewing Results

- **GitHub Security Tab**: Code scanning alerts
- **CI Workflow**: View logs and download artifacts
- **Issues**: Auto-created for high-priority vulnerabilities
- **Pull Requests**: Dependency review comments

## 🔒 Security Best Practices

### For Developers

1. **Always run pre-commit hooks** before committing
2. **Review Dependabot PRs promptly** - security updates are important
3. **Don't ignore security warnings** without investigation  
4. **Use environment variables** for secrets, never hardcode
5. **Test security changes** in isolated environments

### For Maintainers

1. **Monitor security alerts** in GitHub Security tab
2. **Review and triage** auto-created vulnerability issues
3. **Keep security tools updated** via Dependabot
4. **Investigate false positives** and update configuration
5. **Respond to security incidents** per Security Policy

## 🐛 Troubleshooting

### Common Issues

**Pre-commit hooks failing:**
```bash
# Update hooks to latest versions
pre-commit autoupdate

# Clear hook caches
pre-commit clean
```

**Safety scan failing:**
```bash  
# Use new scan command instead of deprecated check
safety scan
```

**False positives:**
- Add to ignore lists in `pyproject.toml`
- Update `.secrets.baseline` for false secret detection
- Use `# nosec` comments for Bandit false positives

### Getting Help

- Check logs in CI workflow runs
- Review security tool documentation
- Open issues for persistent problems
- Follow Security Policy for vulnerability reports

## 🔮 Future Enhancements

Planned security improvements:

1. **CodeQL Integration**: Advanced semantic code analysis
2. **Container Scanning**: Docker image vulnerability scanning  
3. **SBOM Generation**: Software Bill of Materials
4. **Compliance Reporting**: Automated compliance checks
5. **Security Metrics**: Dashboards and trending

---

For questions about security automation, see the [Security Policy](SECURITY.md) or open a discussion.