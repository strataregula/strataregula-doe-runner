# CLI Reference

Complete command-line interface reference for DOE Runner.

## Installation and Setup

### Command Availability
After installing `strataregula-doe-runner`, the following command becomes available:

```bash
srd          # Main DOE Runner CLI
```

### Version Check
```bash
srd --version
# Output: DOE Runner 0.1.0
```

### Help
```bash
srd --help
# Shows main help and available commands

srd COMMAND --help
# Shows help for specific command
```

## Main Commands

### `srd run`

Execute experiment cases from CSV file.

#### Synopsis
```bash
srd run [OPTIONS] --cases CASES_FILE [--out METRICS_FILE]
```

#### Required Arguments

##### `--cases CASES_FILE`
- **Description**: Path to input cases CSV file
- **Type**: File path (must exist and be readable)
- **Examples**:
  ```bash
  srd run --cases test_cases.csv
  srd run --cases /path/to/experiments/load_test.csv
  srd run --cases "./cases/performance_suite.csv"
  ```

#### Optional Arguments

##### `--out METRICS_FILE`
- **Description**: Path to output metrics CSV file
- **Type**: File path (will be created/overwritten)
- **Default**: `metrics.csv` in current directory
- **Examples**:
  ```bash
  srd run --cases cases.csv --out results.csv
  srd run --cases cases.csv --out /tmp/experiment_results.csv
  ```

##### `--max-workers INTEGER`
- **Description**: Number of parallel worker threads
- **Type**: Integer (1-16)
- **Default**: 1 (sequential execution)
- **Examples**:
  ```bash
  srd run --cases cases.csv --max-workers 4
  srd run --cases cases.csv --max-workers 8  # For heavy parallelization
  ```

##### `--force`
- **Description**: Force re-execution, ignoring cache
- **Type**: Flag (no value)
- **Default**: False (use cache when available)
- **Examples**:
  ```bash
  srd run --cases cases.csv --force
  srd run --cases cases.csv --out fresh_results.csv --force
  ```

##### `--dry-run`
- **Description**: Validate cases without executing them
- **Type**: Flag (no value)
- **Default**: False (execute cases)
- **Examples**:
  ```bash
  srd run --cases cases.csv --dry-run
  srd run --cases suspicious_cases.csv --dry-run --verbose
  ```

##### `--verbose`
- **Description**: Enable verbose output and logging
- **Type**: Flag (no value)
- **Default**: False (minimal output)
- **Examples**:
  ```bash
  srd run --cases cases.csv --verbose
  srd run --cases cases.csv --max-workers 4 --verbose
  ```

##### `--timeout INTEGER`
- **Description**: Global timeout override (seconds)
- **Type**: Integer (overrides individual case timeouts)
- **Default**: Use individual case timeout_s values
- **Examples**:
  ```bash
  srd run --cases cases.csv --timeout 300  # 5 minute max per case
  srd run --cases cases.csv --timeout 60   # Quick timeout for testing
  ```

##### `--backend-filter STRING`
- **Description**: Execute only cases with specified backend
- **Type**: String (shell, dummy, simroute)
- **Default**: Execute all backends
- **Examples**:
  ```bash
  srd run --cases cases.csv --backend-filter shell
  srd run --cases cases.csv --backend-filter dummy --dry-run
  ```

##### `--case-filter STRING`
- **Description**: Execute only cases matching pattern (regex)
- **Type**: Regular expression string
- **Default**: Execute all cases
- **Examples**:
  ```bash
  srd run --cases cases.csv --case-filter "test-.*"
  srd run --cases cases.csv --case-filter "perf-load-.*"
  srd run --cases cases.csv --case-filter "smoke-.*|critical-.*"
  ```

##### `--resource-group STRING`
- **Description**: Execute only cases from specified resource group
- **Type**: String
- **Default**: Execute all resource groups
- **Examples**:
  ```bash
  srd run --cases cases.csv --resource-group light
  srd run --cases cases.csv --resource-group heavy --max-workers 2
  ```

#### Complete Examples

```bash
# Basic execution
srd run --cases my_cases.csv

# Production-ready execution with parallelization
srd run --cases production_cases.csv --out prod_results.csv --max-workers 8 --verbose

# Quick validation run
srd run --cases new_cases.csv --dry-run --verbose

# Re-run with fresh results
srd run --cases cases.csv --force --out fresh_metrics.csv

# Execute only shell backend cases
srd run --cases mixed_cases.csv --backend-filter shell --max-workers 4

# Execute only performance tests
srd run --cases all_cases.csv --case-filter "perf-.*" --resource-group heavy

# Quick timeout for testing
srd run --cases slow_cases.csv --timeout 30 --verbose
```

### `srd validate`

Validate cases CSV file format without execution.

#### Synopsis
```bash
srd validate [OPTIONS] CASES_FILE
```

#### Arguments

##### `CASES_FILE`
- **Description**: Path to cases CSV file to validate
- **Type**: File path (must exist and be readable)
- **Required**: Yes

#### Optional Arguments

##### `--verbose`
- **Description**: Show detailed validation results
- **Type**: Flag
- **Examples**:
  ```bash
  srd validate cases.csv --verbose
  ```

##### `--strict`
- **Description**: Enable strict validation (additional checks)
- **Type**: Flag
- **Examples**:
  ```bash
  srd validate cases.csv --strict
  ```

#### Examples
```bash
# Basic validation
srd validate test_cases.csv

# Detailed validation output
srd validate cases.csv --verbose

# Strict validation with all checks
srd validate production_cases.csv --strict --verbose
```

### `srd cache`

Manage execution result cache.

#### Subcommands

##### `srd cache status CASES_FILE`
Show cache status for cases file.

```bash
srd cache status cases.csv
# Output: Cache hits: 15/20 cases (75.0%)
```

##### `srd cache clear CASES_FILE`
Clear cached results for cases file.

```bash
srd cache clear cases.csv
# Output: Cleared cache for 15 cases
```

##### `srd cache clear-all`
Clear entire cache.

```bash
srd cache clear-all
# Output: Cleared entire cache (1,234 entries)
```

#### Examples
```bash
# Check cache status
srd cache status my_cases.csv

# Clear specific cache
srd cache clear my_cases.csv

# Nuclear option - clear everything
srd cache clear-all
```

### `srd info`

Show system and plugin information.

#### Synopsis
```bash
srd info [OPTIONS]
```

#### Optional Arguments

##### `--adapters`
- **Description**: Show available execution adapters/backends
- **Type**: Flag

##### `--system`
- **Description**: Show system information
- **Type**: Flag

##### `--plugin`
- **Description**: Show plugin integration status
- **Type**: Flag

#### Examples
```bash
# Basic info
srd info

# Show available backends
srd info --adapters

# Complete system info
srd info --system --adapters --plugin
```

## Global Options

These options work with all commands:

### `--version`
Show version information.
```bash
srd --version
```

### `--help`
Show help information.
```bash
srd --help
srd run --help
srd validate --help
```

### `--config FILE`
Use custom configuration file (future feature).
```bash
srd --config my_config.yaml run --cases cases.csv
```

## Environment Variables

### `RUN_LOG_DIR`
- **Description**: Directory for execution run logs
- **Default**: `docs/run` (relative to working directory)
- **Examples**:
  ```bash
  export RUN_LOG_DIR="/var/log/doe-runner"
  export RUN_LOG_DIR="./logs"
  ```

### `RUN_LOG_WRITE_COMPAT`
- **Description**: Enable compatibility mode for run logs
- **Default**: `0` (disabled)
- **Values**: `0` (disabled), `1` (enabled)
- **Examples**:
  ```bash
  export RUN_LOG_WRITE_COMPAT=1
  ```

### `DOE_MAX_WORKERS`
- **Description**: Default number of worker threads
- **Default**: `1`
- **Examples**:
  ```bash
  export DOE_MAX_WORKERS=4
  ```

### `DOE_CACHE_DIR`
- **Description**: Custom cache directory
- **Default**: `~/.doe-runner/cache`
- **Examples**:
  ```bash
  export DOE_CACHE_DIR="/tmp/doe-cache"
  ```

### `DOE_DEBUG`
- **Description**: Enable debug logging
- **Default**: `0` (disabled)
- **Values**: `0` (disabled), `1` (enabled)
- **Examples**:
  ```bash
  export DOE_DEBUG=1
  ```

## Exit Codes

DOE Runner uses specific exit codes to indicate execution outcomes:

### Exit Code 0: Success
- All cases executed successfully
- No threshold violations detected
- All validations passed

### Exit Code 2: Success with Warnings
- Cases executed successfully
- Performance threshold violations detected
- Review required but execution completed

### Exit Code 3: Error
- Configuration errors (invalid cases file, missing columns)
- I/O errors (file not found, permission denied)
- Execution failures (backend errors, system issues)

## Output Formats

### Standard Output

#### Minimal Output (Default)
```bash
$ srd run --cases cases.csv
Executing 5 cases...
✅ Completed: 5 successful, 0 failed, 0 timeout
⚠️  Threshold violations: 1 case
Exit code: 2
```

#### Verbose Output
```bash
$ srd run --cases cases.csv --verbose
DOE Runner v0.1.0
Cases file: cases.csv
Output file: metrics.csv
Max workers: 1
Cache enabled: true

Loading cases...
✅ Loaded 5 valid cases

Executing cases:
[1/5] test-01 (shell): ✅ OK (0.123s) - p95=0.05s
[2/5] test-02 (dummy): ✅ OK (0.089s) - p95=0.08s  
[3/5] test-03 (shell): ✅ OK (1.234s) - p95=0.20s ⚠️ threshold violation
[4/5] test-04 (shell): ✅ OK (0.456s) - p95=0.12s
[5/5] test-05 (dummy): ✅ OK (0.067s) - p95=0.05s

Writing metrics to: metrics.csv
Writing run log to: docs/run/run_20250825_103000.md

📊 Execution Summary:
  Total cases: 5
  Successful: 5 (100.0%)
  Failed: 0 (0.0%)
  Timeout: 0 (0.0%)
  Cache hits: 0 (0.0%)
  Total time: 1.969s

⚠️  Threshold Violations (1):
  - test-03: p95=0.200s > threshold=0.150s

Exit code: 2
```

### Error Output

#### Configuration Error
```bash
$ srd run --cases invalid.csv
❌ Error: Missing required column 'backend' in cases file
Exit code: 3
```

#### File Not Found
```bash
$ srd run --cases missing.csv
❌ Error: Cases file not found: missing.csv
Exit code: 3
```

#### Validation Error
```bash
$ srd validate invalid_cases.csv
❌ Validation failed:
  - Row 2: Invalid backend 'invalid_backend'
  - Row 3: timeout_s must be positive integer
  - Row 5: Duplicate case_id 'test-01'
Exit code: 3
```

## Integration Examples

### Makefile Integration
```makefile
# Makefile
.PHONY: test-smoke test-load test-all

test-smoke:
	srd run --cases smoke_cases.csv --out smoke_results.csv --verbose

test-load:
	srd run --cases load_cases.csv --out load_results.csv --max-workers 4 --verbose

test-all: test-smoke test-load
	@echo "All tests completed"

validate-cases:
	srd validate smoke_cases.csv --strict
	srd validate load_cases.csv --strict

clean-cache:
	srd cache clear-all
```

### Shell Script Integration
```bash
#!/bin/bash
# run_experiments.sh

set -e

CASES_FILE="$1"
OUTPUT_FILE="$2"
WORKERS="${3:-4}"

if [[ -z "$CASES_FILE" || -z "$OUTPUT_FILE" ]]; then
    echo "Usage: $0 CASES_FILE OUTPUT_FILE [WORKERS]"
    exit 1
fi

echo "🔍 Validating cases file..."
srd validate "$CASES_FILE" --strict --verbose

echo "🚀 Executing experiments..."
srd run --cases "$CASES_FILE" --out "$OUTPUT_FILE" --max-workers "$WORKERS" --verbose

case $? in
    0)
        echo "✅ All experiments passed successfully"
        ;;
    2)
        echo "⚠️  Experiments completed with threshold violations"
        echo "📊 Check results in: $OUTPUT_FILE"
        ;;
    3)
        echo "❌ Experiment execution failed"
        exit 1
        ;;
esac

echo "📈 Results available in: $OUTPUT_FILE"
echo "📋 Run logs available in: docs/run/"
```

### Docker Integration
```bash
# Run in Docker container
docker run --rm \
  -v $(pwd)/cases:/app/cases:ro \
  -v $(pwd)/results:/app/results \
  unizontech/strataregula-doe-runner:latest \
  srd run --cases /app/cases/production.csv --out /app/results/metrics.csv --max-workers 4 --verbose
```

### CI/CD Pipeline Integration

#### Jenkins Jenkinsfile
```groovy
pipeline {
    agent any
    
    stages {
        stage('Validate Cases') {
            steps {
                sh 'srd validate performance_cases.csv --strict'
            }
        }
        
        stage('Execute Performance Tests') {
            steps {
                script {
                    def exitCode = sh(
                        returnStatus: true, 
                        script: 'srd run --cases performance_cases.csv --out perf_results.csv --max-workers 4 --verbose'
                    )
                    
                    switch(exitCode) {
                        case 0:
                            echo "✅ Performance tests passed"
                            break
                        case 2:
                            echo "⚠️ Performance threshold violations detected"
                            currentBuild.result = 'UNSTABLE'
                            break
                        case 3:
                            error "❌ Performance test execution failed"
                    }
                }
            }
        }
        
        stage('Archive Results') {
            steps {
                archiveArtifacts artifacts: 'perf_results.csv, docs/run/*.md', fingerprint: true
            }
        }
    }
}
```

#### GitHub Actions
```yaml
name: Performance Tests

on: [push, pull_request]

jobs:
  performance:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Install DOE Runner
      run: pip install strataregula-doe-runner
    
    - name: Validate Test Cases  
      run: srd validate perf_cases.csv --strict --verbose
    
    - name: Run Performance Tests
      id: perf_test
      run: |
        srd run --cases perf_cases.csv --out results.csv --max-workers 4 --verbose
        echo "exit_code=$?" >> $GITHUB_OUTPUT
      continue-on-error: true
    
    - name: Check Results
      run: |
        case "${{ steps.perf_test.outputs.exit_code }}" in
          0) echo "✅ All performance tests passed" ;;
          2) echo "⚠️ Performance threshold violations" ;;
          3) echo "❌ Test execution failed" && exit 1 ;;
        esac
    
    - name: Upload Results
      uses: actions/upload-artifact@v3
      with:
        name: performance-results
        path: |
          results.csv
          docs/run/
```

## Troubleshooting

### Common Command Issues

#### Permission Denied
```bash
$ srd run --cases cases.csv
❌ Error: Permission denied: cases.csv
```
**Solution**: Check file permissions: `chmod 644 cases.csv`

#### Command Not Found
```bash
$ srd --version
bash: srd: command not found
```
**Solution**: Verify installation: `pip list | grep strataregula-doe-runner`

#### Invalid Arguments
```bash
$ srd run --cases cases.csv --max-workers 0
❌ Error: max-workers must be between 1 and 16
```
**Solution**: Use valid argument ranges

#### Memory Issues with Large Case Files
```bash
$ srd run --cases huge_cases.csv --max-workers 16
❌ Error: Out of memory
```
**Solution**: Reduce max-workers or split case file

### Performance Optimization

#### Optimal Worker Count
```bash
# CPU-bound workloads
srd run --cases cases.csv --max-workers $(nproc)

# I/O-bound workloads  
srd run --cases cases.csv --max-workers $(($(nproc) * 2))

# Conservative approach
srd run --cases cases.csv --max-workers 4
```

#### Cache Management
```bash
# Check cache effectiveness
srd cache status cases.csv

# Clear cache if stale
srd cache clear cases.csv

# Fresh run
srd run --cases cases.csv --force
```

### Debug Mode
```bash
# Enable debug logging
export DOE_DEBUG=1
srd run --cases cases.csv --verbose

# Or inline
DOE_DEBUG=1 srd run --cases cases.csv --verbose
```

Next: [Technical Documentation](../technical/architecture.md)