# Code Maat MCP Server Examples

This document provides practical examples of using the Code Maat MCP server for various software analysis scenarios.

> **Note**: This server uses FastMCP and is designed to work with Claude Desktop. All examples assume the server is properly configured in your Claude Desktop MCP settings.

## Quick Start Workflow

### 1. Basic Repository Analysis

```python
# Check if Code Maat is properly configured
check_code_maat_status()

# Generate a git log for the last 6 months
generate_git_log(
    repo_path="/path/to/your/repository",
    format_type="git2",
    after_date="2024-01-01"
)

# Get repository overview
run_summary_analysis(
    log_file="logfile.log",
    vcs="git2"
)
```

### 2. Finding Hotspots and Problem Areas

```python
# Find modules with many developers (potential communication issues)
run_authors_analysis(
    log_file="logfile.log",
    vcs="git2",
    min_revs=10,
    rows=20
)

# Find frequently changing code (potential instability)
run_churn_analysis(
    log_file="logfile.log",
    vcs="git2",
    churn_type="entity-churn",
    rows=15
)

# Check which code is stable vs frequently changing
run_age_analysis(
    log_file="logfile.log",
    vcs="git2",
    rows=25
)
```

## Advanced Analysis Scenarios

### Refactoring Planning

```python
# Find logically coupled modules (candidates for refactoring)
run_coupling_analysis(
    log_file="logfile.log",
    vcs="git2",
    min_coupling=70,  # High coupling threshold
    max_changeset_size=15,  # Focus on smaller changes
    min_revs=5
)

# Understand developer ownership patterns
run_entity_effort_analysis(
    log_file="logfile.log",
    vcs="git2",
    min_revs=3
)
```

### Team Organization Analysis

```python
# Analyze communication patterns between developers
run_communication_analysis(
    log_file="logfile.log",
    vcs="git2",
    min_shared_revs=8
)

# See individual developer contributions
run_churn_analysis(
    log_file="logfile.log",
    vcs="git2",
    churn_type="author-churn"
)
```

### Technical Debt Assessment

```python
# Find modules that change together but shouldn't
run_coupling_analysis(
    log_file="logfile.log",
    vcs="git2",
    min_coupling=50,
    max_coupling=90  # Exclude obvious high coupling
)

# Identify modules with distributed ownership (potential knowledge silos)
run_authors_analysis(
    log_file="logfile.log",
    vcs="git2",
    min_revs=5
)
```

## Working with Different VCS Systems

### Git Repositories

```python
# Generate git2 format log (recommended)
generate_git_log(
    repo_path="/path/to/git/repo",
    format_type="git2",
    after_date="2023-01-01",
    exclude_paths=["vendor/", "node_modules/", "dist/"]
)

# Alternative: legacy git format
generate_git_log(
    repo_path="/path/to/git/repo",
    format_type="git",
    after_date="2023-01-01"
)
```

### Subversion

```bash
# Generate SVN log (done outside MCP server)
svn log -v --xml > svn_logfile.log -r {20240101}:HEAD
```

```python
# Analyze SVN log
run_summary_analysis(
    log_file="svn_logfile.log",
    vcs="svn"
)
```

## Real-World Use Cases

### Case 1: Microservices Decomposition

When breaking down a monolith into microservices:

```python
# 1. Find tightly coupled modules
run_coupling_analysis(
    log_file="monolith.log",
    vcs="git2",
    min_coupling=80,
    max_changeset_size=10
)

# 2. Identify stable vs changing areas
run_age_analysis(
    log_file="monolith.log", 
    vcs="git2"
)

# 3. Understand team boundaries
run_communication_analysis(
    log_file="monolith.log",
    vcs="git2",
    min_shared_revs=10
)
```

### Case 2: Code Review Process Optimization

Optimize your code review process:

```python
# Find files that multiple developers work on
run_authors_analysis(
    log_file="recent.log",
    vcs="git2",
    min_revs=3,
    rows=30
)

# Identify knowledge concentration risks
run_entity_effort_analysis(
    log_file="recent.log",
    vcs="git2"
)
```

### Case 3: Legacy System Assessment

Assess a legacy system for modernization:

```python
# Get overall health metrics
run_summary_analysis(
    log_file="legacy.log",
    vcs="git2"
)

# Find the most problematic areas
run_churn_analysis(
    log_file="legacy.log",
    vcs="git2", 
    churn_type="entity-churn",
    rows=20
)

# Understand current maintenance patterns
run_authors_analysis(
    log_file="legacy.log",
    vcs="git2"
)
```

## Filtering and Data Preparation

### Time-based Filtering

```python
# Focus on recent development (last 3 months)
generate_git_log(
    repo_path="/path/to/repo",
    after_date="2024-04-01"  # Adjust to 3 months ago
)

# Focus on specific time period
generate_git_log(
    repo_path="/path/to/repo", 
    after_date="2024-01-01"
)
```

### Path-based Filtering

```python
# Exclude common noise directories
generate_git_log(
    repo_path="/path/to/repo",
    exclude_paths=[
        "vendor/",
        "node_modules/", 
        "target/",
        "build/",
        "dist/",
        "__pycache__/",
        "*.min.js",
        "test/fixtures/"
    ]
)
```

### Analysis-specific Filtering

```python
# For coupling analysis - focus on meaningful changes
run_coupling_analysis(
    log_file="logfile.log",
    vcs="git2",
    min_coupling=30,         # Ignore weak coupling
    max_changeset_size=25,   # Ignore massive commits
    min_revs=5              # Ignore rarely changed files
)

# For author analysis - focus on active files
run_authors_analysis(
    log_file="logfile.log",
    vcs="git2",
    min_revs=8,    # Files with significant activity
    rows=25        # Top problematic files
)
```

## Analysis Interpretation

### Understanding Coupling Results

```python
# High coupling (> 70%) might indicate:
# - Shared libraries/utilities (expected)
# - Missing abstractions (potential refactoring)
# - Feature modules that should be combined

# Medium coupling (30-70%) might indicate:
# - Related features (check if intentional)
# - Temporal coupling (changes for same feature)
# - Cross-cutting concerns

run_coupling_analysis(
    log_file="logfile.log",
    vcs="git2", 
    min_coupling=30,
    max_coupling=100
)
```

### Understanding Author Metrics

```python
# High author count per module might indicate:
# - Core/shared components (expected)
# - Lack of ownership (potential issue)
# - Knowledge sharing (good) vs confusion (bad)

# Low author count might indicate:
# - Clear ownership (good)
# - Knowledge silos (potential risk)
# - Specialized components

run_authors_analysis(
    log_file="logfile.log",
    vcs="git2"
)
```

### Understanding Churn Patterns

```python
# High churn might indicate:
# - Active feature development (expected)
# - Instability/bugs (investigate)
# - Lack of clear requirements

# Low churn might indicate:
# - Stable, mature code (good)
# - Neglected code (investigate if critical)
# - Over-engineering (investigate if complex)

run_churn_analysis(
    log_file="logfile.log",
    vcs="git2",
    churn_type="entity-churn"
)
```

## Troubleshooting Common Issues

### Log File Problems

```python
# Always validate your log file first
validate_log_file(
    log_file="logfile.log",
    vcs="git2"
)

# Check the first few lines manually if validation fails
```

### Performance Issues

```python
# For large repositories, use date filtering
generate_git_log(
    repo_path="/large/repo",
    after_date="2024-06-01",  # Recent data only
    exclude_paths=["vendor/", "third_party/"]
)

# Limit result sets for initial exploration
run_coupling_analysis(
    log_file="logfile.log",
    vcs="git2",
    min_coupling=50,    # Higher threshold
    max_changeset_size=15  # Smaller changesets only
)
```

### Memory Issues

```python
# Check current configuration
check_code_maat_status()

# If you see memory errors, increase heap size in mcp_config.json:
# "java_opts": ["-Xmx8g", "-Djava.awt.headless=true", "-Xss1M"]
```

## Best Practices

1. **Start with summary analysis** to understand your data
2. **Use time filtering** to focus on relevant periods
3. **Exclude noise** (vendor directories, generated files)
4. **Validate logs** before running expensive analyses
5. **Combine analyses** for comprehensive insights
6. **Document findings** and track improvements over time