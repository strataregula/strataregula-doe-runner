# Metrics Output Format

This document describes the complete specification for the `metrics.csv` output format produced by DOE Runner.

## Overview

The metrics CSV file contains the standardized results of experiment execution. Each row represents the outcome of one test case with performance metrics, execution details, and status information.

## File Format Requirements

### Basic Requirements
- **Encoding**: UTF-8
- **Format**: CSV with comma separators  
- **Line Endings**: LF (Unix-style, enforced)
- **Headers**: First row contains column headers
- **Deterministic**: Same input always produces same output format

### Column Ordering
Columns appear in a **fixed, deterministic order** to ensure reproducible outputs:

1. **Core Result Columns** (always first)
2. **Performance Metrics** (standard order)
3. **Parameter Columns** (`param_*` in alphabetical order)
4. **Extension Columns** (`ext_*`, `tag_*`, `note_*` in alphabetical order)

## Required Columns (Always Present)

### Core Execution Results

#### `case_id`
- **Type**: String
- **Description**: Unique case identifier (copied from input)
- **Example**: `test-01`, `perf-load-heavy-001`

#### `status`
- **Type**: String (enum)
- **Description**: Execution outcome
- **Valid Values**:
  - `OK`: Successful execution
  - `FAIL`: Command execution failed
  - `TIMEOUT`: Execution exceeded timeout limit
- **Examples**:
  ```csv
  case_id,status
  test-01,OK
  test-02,FAIL  
  test-03,TIMEOUT
  ```

#### `run_seconds`
- **Type**: Float (6 decimal places)
- **Description**: Actual execution time in seconds
- **Range**: 0.0 to timeout_s value
- **Examples**:
  ```csv
  case_id,run_seconds
  test-01,0.123456
  test-02,1.234567
  test-03,60.000000
  ```

### Performance Metrics

#### `p95`
- **Type**: Float (6 decimal places) or empty
- **Description**: 95th percentile latency in seconds
- **Source**: Parsed from command output or backend-generated
- **Examples**:
  ```csv
  case_id,p95
  test-01,0.050000
  test-02,0.120000
  test-03,         # Empty if not available
  ```

#### `p99`
- **Type**: Float (6 decimal places) or empty
- **Description**: 99th percentile latency in seconds
- **Examples**:
  ```csv
  case_id,p99
  test-01,0.080000
  test-02,0.180000
  test-03,         # Empty if not available
  ```

#### `throughput_rps`
- **Type**: Float (2 decimal places) or empty
- **Description**: Throughput in requests per second
- **Examples**:
  ```csv
  case_id,throughput_rps
  test-01,1000.00
  test-02,850.50
  test-03,        # Empty if not available  
  ```

#### `errors`
- **Type**: Integer
- **Description**: Number of errors encountered during execution
- **Default**: 0 for successful executions
- **Examples**:
  ```csv
  case_id,errors
  test-01,0
  test-02,3
  test-03,1
  ```

### Timestamp Columns

#### `ts_start`
- **Type**: ISO 8601 timestamp (JST timezone)
- **Description**: Execution start time
- **Format**: `YYYY-MM-DDTHH:MM:SS+09:00`
- **Examples**:
  ```csv
  case_id,ts_start
  test-01,2025-08-25T10:30:00+09:00
  test-02,2025-08-25T10:30:15+09:00
  ```

#### `ts_end`
- **Type**: ISO 8601 timestamp (JST timezone)
- **Description**: Execution end time
- **Examples**:
  ```csv
  case_id,ts_end
  test-01,2025-08-25T10:30:01+09:00
  test-02,2025-08-25T10:30:45+09:00
  ```

## Optional Performance Columns

### Extended Latency Metrics

#### `p50`, `p90`, `p95`, `p99`, `p999`
- **Type**: Float (6 decimal places)
- **Description**: Various percentile latencies in seconds
- **Source**: Parsed from detailed command output

#### `latency_avg`, `latency_min`, `latency_max`
- **Type**: Float (6 decimal places)
- **Description**: Average, minimum, and maximum latency
- **Units**: Seconds

### Throughput Metrics

#### `throughput_avg`, `throughput_peak`
- **Type**: Float (2 decimal places)
- **Description**: Average and peak throughput measurements
- **Units**: Requests per second

#### `requests_total`, `requests_successful`, `requests_failed`
- **Type**: Integer
- **Description**: Request count breakdown

### Resource Usage Metrics

#### `cpu_util`
- **Type**: Float (2 decimal places)
- **Description**: CPU utilization percentage (0.0-100.0)
- **Source**: Parsed from system monitoring or command output

#### `mem_peak_mb`
- **Type**: Float (2 decimal places)
- **Description**: Peak memory usage in megabytes
- **Source**: Process monitoring or command output

#### `disk_io_mb`
- **Type**: Float (2 decimal places)
- **Description**: Total disk I/O in megabytes

#### `network_io_mb`
- **Type**: Float (2 decimal places)
- **Description**: Total network I/O in megabytes

### Queue and Concurrency Metrics

#### `queue_depth_p95`
- **Type**: Float (2 decimal places)
- **Description**: 95th percentile queue depth

#### `connections_active`
- **Type**: Integer
- **Description**: Number of active connections during test

#### `threads_active`
- **Type**: Integer
- **Description**: Number of active threads during execution

## Parameter Columns (`param_*`)

### Format
- **Naming**: `param_{parameter_name}`
- **Source**: Copied from input cases.csv
- **Purpose**: Track input parameters alongside results

### Examples
```csv
case_id,param_load,param_users,param_duration,p95,throughput_rps
test-01,light,100,30,0.05,1000.00
test-02,medium,200,60,0.10,800.00
test-03,heavy,400,120,0.20,500.00
```

## Extension Columns

### `ext_*` Columns
- **Purpose**: Backend-specific extensions
- **Naming**: `ext_{extension_name}`
- **Examples**:
  ```csv
  case_id,ext_backend_version,ext_simulation_step_count
  test-01,shell-1.0,
  test-02,simroute-2.1,15000
  ```

### `tag_*` Columns  
- **Purpose**: Tag-based metadata
- **Naming**: `tag_{tag_name}`
- **Values**: Boolean (1 for present, empty for absent)
- **Examples**:
  ```csv
  case_id,tag_smoke,tag_critical,tag_performance
  test-01,1,1,
  test-02,,,1
  ```

### `note_*` Columns
- **Purpose**: Free-form annotations
- **Naming**: `note_{note_type}`
- **Examples**:
  ```csv
  case_id,note_comment,note_issue_ref
  test-01,"Baseline measurement","TICKET-123"
  test-02,"Performance regression",
  ```

## Backend-Specific Columns

### Shell Backend

#### Standard Parsing
The shell backend parses these formats from command stdout/stderr:

**Key-Value Format**:
```bash
p95=0.050 p99=0.080 throughput_rps=1000 errors=0
```

**JSON Format**:
```json
{
  "p95": 0.050,
  "p99": 0.080,
  "throughput_rps": 1000,
  "errors": 0,
  "cpu_util": 25.5,
  "mem_peak_mb": 128.0
}
```

#### Custom Metrics
Any numeric key from command output becomes a column:
```bash
# Command output
custom_metric=42.5 response_size_kb=1.2

# Results in columns
custom_metric,response_size_kb
42.50,1.20
```

### Dummy Backend

#### Generated Metrics
- `p95`: Random value 0.01-0.10 seconds
- `p99`: p95 * 1.6 seconds  
- `throughput_rps`: Random value 500-2000 RPS
- `errors`: 0 (dummy never fails)

### Simroute Backend

#### Simulation Metrics
- Standard performance metrics (p95, p99, throughput_rps)
- `ext_simulation_step_count`: Number of simulation steps
- `ext_vehicles_processed`: Number of vehicles simulated
- `ext_scenario_type`: Simulation scenario used

## Complete Example Output

### Sample metrics.csv
```csv
case_id,status,run_seconds,p95,p99,throughput_rps,errors,ts_start,ts_end,cpu_util,mem_peak_mb,param_load,param_users,ext_backend_version,tag_smoke,tag_performance,note_comment
smoke-01,OK,0.089000,0.010000,0.020000,2000.00,0,2025-08-25T10:30:00+09:00,2025-08-25T10:30:01+09:00,5.50,64.00,light,50,dummy-1.0,1,,"Baseline smoke test"
unit-01,OK,15.234000,,,,,0,2025-08-25T10:30:01+09:00,2025-08-25T10:30:16+09:00,25.00,128.00,,,shell-1.0,,,"Unit test suite"
load-light,OK,32.567000,0.050000,0.080000,1000.00,0,2025-08-25T10:30:16+09:00,2025-08-25T10:30:49+09:00,45.25,256.00,medium,100,shell-1.0,,1,"Light load test"
load-heavy,OK,125.890000,0.200000,0.400000,500.00,3,2025-08-25T10:30:49+09:00,2025-08-25T10:32:55+09:00,78.50,512.00,heavy,400,shell-1.0,,1,"Heavy load with some errors"
sim-urban,OK,180.123000,0.150000,0.250000,750.00,0,2025-08-25T10:32:55+09:00,2025-08-25T10:35:55+09:00,60.00,1024.00,simulation,,simroute-2.1,,,
timeout-case,TIMEOUT,60.000000,,,,,0,2025-08-25T10:35:55+09:00,2025-08-25T10:36:55+09:00,,,heavy,1000,shell-1.0,,,
failed-case,FAIL,5.678000,,,,,1,2025-08-25T10:36:55+09:00,2025-08-25T10:37:01+09:00,10.00,32.00,light,10,shell-1.0,,,"Command returned exit code 1"
```

## Data Formatting Rules

### Numeric Formatting
- **Floats**: Consistent decimal places (6 for latency, 2 for others)
- **Integers**: No decimal places
- **Empty Values**: Empty string (not NULL, "N/A", etc.)
- **Rounding**: Standard mathematical rounding

### String Formatting
- **Quotes**: Only when necessary (contains comma, quotes, newlines)
- **Encoding**: UTF-8 throughout
- **Newlines**: LF only (no CRLF)

### Timestamp Formatting
- **Format**: ISO 8601 with JST timezone (+09:00)
- **Precision**: Second-level precision
- **Consistency**: All timestamps in same timezone

### Boolean Values
- **True**: "1" or "true" (depending on context)
- **False**: Empty string (not "0" or "false")

## Deterministic Output Guarantees

### Column Ordering
1. Required columns in fixed order
2. Performance metrics in alphabetical order
3. Parameter columns (`param_*`) in alphabetical order
4. Extension columns (`ext_*`, `tag_*`, `note_*`) in alphabetical order

### Row Ordering
- Same order as input cases.csv
- Maintains case_id sequence from input

### Value Consistency
- Same precision and formatting across runs
- Consistent empty value representation
- Stable numeric rounding

## Validation and Quality Assurance

### Format Validation
```python
# Example validation rules
def validate_metrics_csv(filepath):
    required_columns = [
        'case_id', 'status', 'run_seconds', 'p95', 'p99', 
        'throughput_rps', 'errors', 'ts_start', 'ts_end'
    ]
    
    # Check required columns exist
    # Validate data types
    # Verify timestamp format
    # Check numeric ranges
```

### Quality Checks
- All case_ids from input present in output
- Status values are valid enum values
- Timestamps are in JST timezone
- Numeric values within reasonable ranges
- No missing required data

## Usage Patterns

### 1. Performance Analysis
```python
import pandas as pd

# Load metrics
df = pd.read_csv('metrics.csv')

# Analyze performance
successful = df[df['status'] == 'OK']
print(f"P95 avg: {successful['p95'].mean():.3f}s")
print(f"Throughput avg: {successful['throughput_rps'].mean():.0f} RPS")

# Check threshold violations
violations = successful[successful['p95'] > successful.get('threshold_p95', float('inf'))]
print(f"Threshold violations: {len(violations)}")
```

### 2. Trend Analysis
```python
# Compare multiple runs
import matplotlib.pyplot as plt

# Plot performance trends
plt.plot(df['case_id'], df['p95'], label='P95 Latency')
plt.plot(df['case_id'], df['p99'], label='P99 Latency')
plt.legend()
plt.xticks(rotation=45)
plt.ylabel('Latency (seconds)')
plt.title('Performance Trends')
plt.show()
```

### 3. Resource Usage Analysis
```python
# Analyze resource usage
resource_cols = ['cpu_util', 'mem_peak_mb']
resource_data = df[resource_cols].dropna()

print("Resource Usage Summary:")
print(resource_data.describe())
```

### 4. Error Analysis
```python
# Analyze failures
failed_cases = df[df['status'] != 'OK']
print(f"Failed cases: {len(failed_cases)}")
print(f"Timeout cases: {len(df[df['status'] == 'TIMEOUT'])}")
print(f"Error cases: {len(df[df['status'] == 'FAIL'])}")

# Error distribution by resource group
if 'param_resource_group' in df.columns:
    error_by_group = failed_cases.groupby('param_resource_group').size()
    print("\nErrors by resource group:")
    print(error_by_group)
```

## Integration with CI/CD

### Jenkins Pipeline Example
```groovy
stage('Execute Performance Tests') {
    steps {
        sh 'srd run --cases perf_cases.csv --out metrics.csv'
        
        script {
            def exitCode = sh(returnStatus: true, script: 'echo $?')
            
            switch(exitCode) {
                case 0:
                    echo "✅ All performance tests passed"
                    break
                case 2:
                    echo "⚠️ Performance thresholds violated"
                    // Continue but mark as unstable
                    currentBuild.result = 'UNSTABLE'
                    break
                case 3:
                    error "❌ Performance test execution failed"
                    break
            }
        }
        
        // Archive results
        archiveArtifacts artifacts: 'metrics.csv', fingerprint: true
        
        // Parse and analyze
        script {
            def metrics = readCSV file: 'metrics.csv'
            def violations = metrics.findAll { row -> 
                row.status == 'OK' && 
                row.p95 as Double > (row.threshold_p95 as Double ?: Double.MAX_VALUE)
            }
            
            if (violations.size() > 0) {
                echo "Threshold violations found:"
                violations.each { row ->
                    echo "  ${row.case_id}: p95=${row.p95}s > threshold=${row.threshold_p95}s"
                }
            }
        }
    }
}
```

### GitHub Actions Example
```yaml
- name: Run Performance Tests
  run: srd run --cases perf_cases.csv --out metrics.csv
  
- name: Upload Results
  uses: actions/upload-artifact@v3
  with:
    name: performance-results
    path: |
      metrics.csv
      docs/run/

- name: Analyze Results
  run: |
    python << EOF
    import csv
    import sys
    
    with open('metrics.csv', 'r') as f:
        reader = csv.DictReader(f)
        total = 0
        failed = 0
        violations = 0
        
        for row in reader:
            total += 1
            if row['status'] != 'OK':
                failed += 1
            elif (row.get('threshold_p95') and 
                  float(row.get('p95', 0)) > float(row['threshold_p95'])):
                violations += 1
        
        print(f"Total cases: {total}")
        print(f"Failed: {failed}")  
        print(f"Threshold violations: {violations}")
        
        if failed > 0:
            sys.exit(1)
        elif violations > 0:
            sys.exit(2)
    EOF
```

## Troubleshooting

### Common Issues

#### Missing Columns
```bash
# Error: Expected column 'p95' not found
```
**Cause**: Backend didn't produce expected metrics
**Solution**: Check command output format, verify parsing rules

#### Invalid Timestamps
```bash
# Error: Invalid timestamp format in ts_start
```
**Cause**: System timezone issues or clock skew
**Solution**: Verify system timezone, check NTP synchronization

#### Inconsistent Formatting
```bash
# Error: Inconsistent numeric precision
```
**Cause**: Different rounding in processing pipeline
**Solution**: Check numeric formatting configuration

#### Empty Results
```bash
# Error: metrics.csv is empty or has no data rows
```
**Cause**: All cases failed or no cases matched filters
**Solution**: Check case validation, review error logs

### Performance Considerations

#### Large Result Sets
- **Rows**: Efficiently handles 10,000+ result rows
- **Columns**: No practical limit on column count
- **Size**: Typical 1MB per 1,000 standard result rows

#### Memory Usage
- Streaming CSV writing for large datasets
- Minimal memory footprint during processing
- Efficient column ordering and formatting

Next: [CLI Reference](cli-reference.md)