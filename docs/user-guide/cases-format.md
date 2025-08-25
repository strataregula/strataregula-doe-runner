# Cases CSV Format Specification

This document provides the complete specification for the `cases.csv` input format used by DOE Runner.

## Overview

The cases CSV file defines the experiments to be executed. Each row represents one test case with its configuration, execution parameters, and expected outcomes.

## File Format Requirements

### Basic Requirements
- **Encoding**: UTF-8
- **Format**: CSV with comma separators
- **Headers**: First row must contain column headers
- **Line Endings**: LF (Unix-style) preferred, CRLF accepted

### File Structure
```csv
case_id,backend,cmd_template,timeout_s,seed,retries,resource_group,expected_p95,threshold_p95
test-01,shell,"echo 'p95=0.05'",10,42,2,default,0.05,0.06
test-02,dummy,"dummy test",10,123,1,compute,0.08,0.10
```

## Required Columns

### `case_id` (Required)
- **Type**: String
- **Description**: Unique identifier for the test case
- **Rules**: 
  - Must be unique within the file
  - No spaces or special characters recommended
  - Suggested format: `test-01`, `perf-light-001`, `sim-urban-rush`
- **Examples**:
  ```csv
  case_id
  test-basic-01
  performance-load-heavy
  simulation-traffic-peak
  ```

### `backend` (Required)  
- **Type**: String (enum)
- **Description**: Execution backend to use
- **Valid Values**:
  - `shell`: Execute shell commands
  - `dummy`: Testing/simulation backend
  - `simroute`: World-simulation integration (requires extras)
- **Examples**:
  ```csv
  backend
  shell
  dummy
  simroute
  ```

### `cmd_template` (Required)
- **Type**: String
- **Description**: Command template to execute
- **Placeholders**: Can contain `{variable}` placeholders
- **Available Placeholders**:
  - `{seed}`: Replaced with seed value
  - `{case_id}`: Replaced with case ID
  - `{timeout_s}`: Replaced with timeout value
- **Examples**:
  ```csv
  cmd_template
  "echo 'p95=0.05 p99=0.08 throughput_rps=1000'"
  "python benchmark.py --load heavy --seed {seed}"
  "wrk -t4 -c100 -d30s --latency http://localhost:8080/api"
  "python -m simroute_cli --scenario urban --seed {seed} --duration 60"
  ```

### `timeout_s` (Required)
- **Type**: Integer
- **Description**: Maximum execution time in seconds
- **Range**: 1 to 3600 (1 hour)
- **Recommendation**: Set based on expected execution time + buffer
- **Examples**:
  ```csv
  timeout_s
  10          # Quick tests
  60          # Medium benchmarks
  300         # Heavy simulations
  1800        # Long-running tests
  ```

## Optional Columns

### `seed` (Recommended)
- **Type**: Integer
- **Description**: Random seed for reproducible results
- **Default**: Random seed if not specified
- **Range**: Any positive integer
- **Usage**: Critical for deterministic/reproducible experiments
- **Examples**:
  ```csv
  seed
  42          # Classic choice
  12345       # Simple number
  20250825    # Date-based
  ```

### `retries` (Optional)
- **Type**: Integer
- **Description**: Number of retry attempts on failure
- **Default**: 0 (no retries)
- **Range**: 0 to 10
- **Use Case**: Handle transient failures in network tests
- **Examples**:
  ```csv
  retries
  0           # No retries (default)
  2           # Retry twice on failure
  5           # For unreliable environments
  ```

### `resource_group` (Optional)
- **Type**: String
- **Description**: Logical grouping for resource management
- **Default**: "default"
- **Purpose**: Organize cases with similar resource requirements
- **Examples**:
  ```csv
  resource_group
  default     # Default group
  light       # Lightweight tests
  heavy       # Resource-intensive tests
  gpu         # GPU-requiring tests
  network     # Network-dependent tests
  ```

## Metrics Expectation Columns

### `expected_p95` / `expected_p99` (Optional)
- **Type**: Float
- **Description**: Expected performance metric values
- **Units**: Seconds for latency metrics
- **Purpose**: Documentation and comparison baseline
- **Examples**:
  ```csv
  expected_p95,expected_p99
  0.05,0.08           # 50ms p95, 80ms p99
  0.10,0.15           # 100ms p95, 150ms p99
  0.50,1.00           # 500ms p95, 1s p99
  ```

### `threshold_p95` / `threshold_p99` (Optional)
- **Type**: Float  
- **Description**: Performance threshold limits (SLA)
- **Units**: Seconds for latency metrics
- **Purpose**: Automatic pass/fail determination
- **Behavior**: Exit code 2 if exceeded
- **Examples**:
  ```csv
  threshold_p95,threshold_p99
  0.06,0.10           # Fail if p95 > 60ms or p99 > 100ms  
  0.12,0.18           # Relaxed thresholds
  1.00,2.00           # Very relaxed thresholds
  ```

## Extended Columns

### `expected_throughput_rps` / `threshold_throughput_rps` (Optional)
- **Type**: Integer
- **Description**: Throughput expectations and limits
- **Units**: Requests per second
- **Examples**:
  ```csv
  expected_throughput_rps,threshold_throughput_rps
  1000,800            # Expect 1000 RPS, fail below 800
  5000,4000           # High throughput service
  100,50              # Low throughput acceptable
  ```

### `expected_errors` / `threshold_errors` (Optional)
- **Type**: Integer
- **Description**: Error count expectations and limits
- **Default**: threshold_errors = 0 (no errors allowed)
- **Examples**:
  ```csv
  expected_errors,threshold_errors
  0,0                 # No errors expected or allowed
  1,5                 # Some errors expected, fail above 5
  10,20               # Stress test with acceptable error rate
  ```

## Advanced Columns

### `priority` (Optional)
- **Type**: Integer
- **Description**: Execution priority (1-10, 1=highest)
- **Default**: 5 (medium priority)
- **Usage**: Influences execution order in parallel mode
- **Examples**:
  ```csv
  priority
  1                   # Critical test, run first
  5                   # Normal priority
  9                   # Low priority, run last
  ```

### `depends_on` (Optional)
- **Type**: String
- **Description**: Case dependency (case_id of dependency)
- **Behavior**: Wait for dependency completion before starting
- **Format**: Single case_id or comma-separated list
- **Examples**:
  ```csv
  case_id,depends_on
  setup-db,
  test-read,setup-db
  test-write,setup-db
  cleanup,"test-read,test-write"
  ```

### `tags` (Optional)
- **Type**: String
- **Description**: Comma-separated tags for filtering/grouping
- **Usage**: Organize and filter test cases
- **Examples**:
  ```csv
  tags
  smoke,critical
  performance,load-test
  integration,database
  regression,nightly
  ```

### `environment` (Optional)
- **Type**: String
- **Description**: Target execution environment
- **Usage**: Environment-specific configuration
- **Examples**:
  ```csv
  environment
  development
  staging  
  production
  test
  ```

## Backend-Specific Columns

### Shell Backend

#### `working_directory` (Optional)
- **Type**: String
- **Description**: Working directory for command execution
- **Default**: Current directory
- **Examples**:
  ```csv
  working_directory
  /opt/app
  ./tests
  /tmp/benchmark
  ```

#### `environment_vars` (Optional)
- **Type**: String (JSON)
- **Description**: Environment variables for command
- **Format**: JSON object string
- **Examples**:
  ```csv
  environment_vars
  "{\"DEBUG\": \"1\", \"THREADS\": \"4\"}"
  "{\"API_URL\": \"http://localhost:8080\"}"
  ```

### Simroute Backend

#### `scenario` (Optional)
- **Type**: String
- **Description**: Simulation scenario name
- **Examples**:
  ```csv
  scenario
  urban_rush
  highway_traffic  
  rural_roads
  ```

#### `duration` (Optional)
- **Type**: Integer
- **Description**: Simulation duration in seconds
- **Default**: Derived from timeout_s
- **Examples**:
  ```csv
  duration
  60              # 1 minute simulation
  300             # 5 minute simulation
  ```

## Parameter Columns

### Custom Parameters (`param_*`)
- **Type**: Any
- **Description**: Custom parameters passed to command template
- **Naming**: Must start with `param_`
- **Usage**: Available as `{param_name}` in cmd_template
- **Examples**:
  ```csv
  case_id,cmd_template,param_load,param_users
  test-01,"wrk -t{param_load} -c{param_users} http://api",4,100
  test-02,"wrk -t{param_load} -c{param_users} http://api",8,200
  ```

## Complete Example

### Comprehensive Cases File
```csv
case_id,backend,cmd_template,timeout_s,seed,retries,resource_group,expected_p95,threshold_p95,expected_p99,threshold_p99,expected_throughput_rps,threshold_throughput_rps,tags,priority,param_load,param_duration
smoke-01,dummy,"dummy smoke test",10,42,1,light,0.01,0.02,0.02,0.05,2000,1500,"smoke,critical",1,,
unit-test-01,shell,"pytest tests/unit/ -v",30,123,2,light,,,,,,"unit,fast",2,,
integration-01,shell,"pytest tests/integration/ -v",120,456,1,medium,,,,,,"integration,slow",5,,
load-light,shell,"wrk -t{param_load} -c100 -d{param_duration}s --latency http://api/health",60,789,2,heavy,0.05,0.08,0.10,0.15,1000,800,"performance,load",3,4,30
load-heavy,shell,"wrk -t{param_load} -c400 -d{param_duration}s --latency http://api/users",180,101,1,heavy,0.20,0.30,0.40,0.60,500,300,"performance,stress",4,8,120
sim-urban,simroute,"python -m simroute_cli --scenario urban --seed {seed} --duration {param_duration}",300,202,0,compute,0.15,0.20,0.25,0.35,,,,"simulation,traffic",5,,180
cleanup,shell,"docker system prune -f",60,999,0,maintenance,,,,,,"cleanup,maintenance",9,,
```

## Validation Rules

### File-Level Validation
1. **Required columns**: case_id, backend, cmd_template, timeout_s must be present
2. **Unique case_ids**: No duplicate case_id values allowed
3. **Valid backends**: All backend values must be supported
4. **Numeric ranges**: timeout_s, retries, priority within valid ranges
5. **Dependencies**: depends_on references must exist as case_ids

### Row-Level Validation
1. **Non-empty required fields**: case_id, backend, cmd_template cannot be empty
2. **Positive timeouts**: timeout_s must be > 0
3. **Valid thresholds**: threshold values must be positive if specified
4. **Consistent expectations**: expected values should be <= threshold values
5. **Parameter references**: cmd_template placeholders must have corresponding columns

### Data Type Validation
- **Integers**: timeout_s, seed, retries, priority, expected_throughput_rps, threshold_throughput_rps, expected_errors, threshold_errors
- **Floats**: expected_p95, threshold_p95, expected_p99, threshold_p99
- **Strings**: case_id, backend, cmd_template, resource_group, tags, environment, depends_on

## Best Practices

### 1. Naming Conventions
```csv
# Good case_id examples
test-unit-core-01
perf-load-light-api-health  
sim-traffic-urban-rush-hour
regression-database-crud

# Avoid
test1                      # Not descriptive
my test case              # Spaces
test-with-special-chars@  # Special characters
```

### 2. Timeout Setting
```csv
# Rule of thumb: expected_time * 2 + buffer
case_id,cmd_template,expected_duration,timeout_s
quick-test,"echo hello",1,10           # 1s expected, 10s timeout  
benchmark,"benchmark.py",30,75         # 30s expected, 75s timeout
simulation,"simulate.py",120,300       # 2min expected, 5min timeout
```

### 3. Resource Groups
```csv
resource_group,description,typical_cases
light,"CPU: <10%, Memory: <100MB","Unit tests, quick validations"
medium,"CPU: 10-50%, Memory: 100MB-1GB","Integration tests, light benchmarks"  
heavy,"CPU: >50%, Memory: >1GB","Load tests, simulations"
gpu,"Requires GPU","ML inference, graphics rendering"
network,"Network intensive","API tests, data transfers"
```

### 4. Tag Organization
```csv
tags,usage
smoke,"Critical functionality, run first"
unit,"Unit test suite"
integration,"Integration test suite"  
performance,"Performance and load tests"
regression,"Regression test suite"
nightly,"Long-running nightly tests"
critical,"Business-critical functionality"
experimental,"New/experimental features"
```

### 5. Threshold Setting
```csv
# Conservative (strict SLA)
expected_p95,threshold_p95,buffer
0.05,0.06,20%

# Moderate (reasonable buffer)  
expected_p95,threshold_p95,buffer
0.10,0.15,50%

# Relaxed (generous buffer)
expected_p95,threshold_p95,buffer
0.20,0.40,100%
```

## Common Patterns

### 1. Test Suite Pattern
```csv
case_id,backend,cmd_template,timeout_s,tags,priority
setup,shell,"docker-compose up -d",60,"setup",1
smoke-health,shell,"curl -f http://localhost:8080/health",10,"smoke,critical",2  
unit-tests,shell,"pytest tests/unit/ -v --tb=short",120,"unit,fast",3
integration-tests,shell,"pytest tests/integration/ -v",300,"integration",4
performance-tests,shell,"pytest tests/performance/ -v",600,"performance,slow",5
teardown,shell,"docker-compose down",60,"cleanup",9
```

### 2. Load Testing Pattern
```csv
case_id,backend,cmd_template,timeout_s,expected_p95,threshold_p95,param_concurrency,param_duration
load-baseline,shell,"wrk -t4 -c{param_concurrency} -d{param_duration}s --latency http://api/",90,0.05,0.08,50,60
load-2x,shell,"wrk -t4 -c{param_concurrency} -d{param_duration}s --latency http://api/",90,0.10,0.15,100,60
load-4x,shell,"wrk -t8 -c{param_concurrency} -d{param_duration}s --latency http://api/",90,0.20,0.30,200,60
load-8x,shell,"wrk -t8 -c{param_concurrency} -d{param_duration}s --latency http://api/",90,0.40,0.60,400,60
```

### 3. Simulation Pattern
```csv
case_id,backend,cmd_template,timeout_s,seed,scenario,param_vehicles,param_duration
sim-light-traffic,simroute,"simulate --scenario {scenario} --vehicles {param_vehicles} --duration {param_duration} --seed {seed}",180,42,urban,100,120
sim-medium-traffic,simroute,"simulate --scenario {scenario} --vehicles {param_vehicles} --duration {param_duration} --seed {seed}",300,123,urban,500,240
sim-heavy-traffic,simroute,"simulate --scenario {scenario} --vehicles {param_vehicles} --duration {param_duration} --seed {seed}",600,456,urban,1000,480
```

## Troubleshooting

### Common Validation Errors

#### Missing Required Columns
```
Error: Missing required column: 'backend'
```
**Solution**: Ensure case_id, backend, cmd_template, timeout_s columns are present

#### Duplicate Case IDs
```
Error: Duplicate case_id: 'test-01' found on rows 2 and 5
```
**Solution**: Make all case_id values unique

#### Invalid Backend
```
Error: Invalid backend 'invalid' in case 'test-01'. Valid backends: shell, dummy, simroute
```
**Solution**: Use only supported backend values

#### Invalid Timeout
```
Error: Invalid timeout_s '0' in case 'test-01'. Must be positive integer
```
**Solution**: Set timeout_s to positive integer value

#### Missing Dependency
```
Error: Case 'test-02' depends on 'setup', but 'setup' not found
```
**Solution**: Ensure all depends_on references exist as case_ids

### Performance Considerations

#### Large Case Files
- **Rows**: DOE Runner can handle 1000+ cases efficiently
- **Columns**: No practical limit on column count
- **Memory**: ~1MB per 10,000 cases with standard columns

#### Optimization Tips
- Use appropriate timeout values (not too high)
- Group similar cases with resource_group
- Use priority for important cases
- Consider parallel execution with max_workers

Next: [Metrics Output Format](metrics-output.md)