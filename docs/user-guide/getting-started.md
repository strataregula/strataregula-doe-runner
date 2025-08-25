# Getting Started with DOE Runner

This guide will help you get up and running with Strataregula DOE Runner quickly.

## What is DOE Runner?

**DOE Runner is NOT a Design of Experiments design tool.** It is a **batch experiment orchestrator** that takes predefined experiment cases from a CSV file and executes them deterministically, collecting standardized metrics.

### Key Workflow
1. **Input**: Create `cases.csv` with experiment definitions
2. **Execute**: Run cases through various backends (shell, dummy, simroute)
3. **Output**: Get standardized `metrics.csv` with results and run logs

## Installation

### Option 1: From PyPI (Recommended)
```bash
pip install strataregula-doe-runner
```

### Option 2: With Simroute Support
```bash
pip install strataregula-doe-runner[simroute]
```

### Option 3: Development Installation
```bash
git clone https://github.com/strataregula/strataregula-doe-runner.git
cd strataregula-doe-runner
pip install -e ".[dev]"
```

### Verify Installation
```bash
# Check CLI is available
srd --version

# Check plugin integration
python -c "from strataregula_doe_runner.plugin import DOERunnerPlugin; print('✅ Plugin OK')"
```

## Your First Experiment

### Step 1: Create Cases File

Create `my_first_cases.csv`:
```csv
case_id,backend,cmd_template,timeout_s,seed,retries,resource_group,expected_p95,threshold_p95
hello-01,dummy,"dummy hello world test",10,42,1,default,0.05,0.06
hello-02,shell,"echo 'p95=0.03 p99=0.05 throughput_rps=2000'",10,123,1,default,0.03,0.04
hello-03,shell,"echo 'p95=0.08 p99=0.12 throughput_rps=800'",10,456,2,default,0.08,0.09
```

### Step 2: Execute Cases

```bash
# Basic execution
srd run --cases my_first_cases.csv --out results.csv

# With verbose output
srd run --cases my_first_cases.csv --out results.csv --verbose

# Dry run (validation only)
srd run --cases my_first_cases.csv --dry-run
```

### Step 3: Examine Results

View `results.csv`:
```csv
case_id,status,run_seconds,p95,p99,throughput_rps,errors,ts_start,ts_end
hello-01,OK,0.089,0.05,0.08,1000,0,2025-08-25T10:30:00+09:00,2025-08-25T10:30:01+09:00
hello-02,OK,0.123,0.03,0.05,2000,0,2025-08-25T10:30:01+09:00,2025-08-25T10:30:02+09:00
hello-03,OK,0.098,0.08,0.12,800,0,2025-08-25T10:30:02+09:00,2025-08-25T10:30:03+09:00
```

Check run logs in `docs/run/` directory for detailed execution information.

## Understanding Execution Backends

### 1. Dummy Backend
- **Purpose**: Testing and simulation
- **Behavior**: Generates synthetic metrics without actual execution
- **Use Case**: Testing DOE Runner functionality

```csv
case_id,backend,cmd_template,timeout_s
test-dummy,dummy,"dummy simulation test",10
```

### 2. Shell Backend  
- **Purpose**: Execute shell commands and parse output
- **Behavior**: Runs commands and extracts metrics from stdout/stderr
- **Use Case**: Running actual benchmark tools, scripts

```csv
case_id,backend,cmd_template,timeout_s
test-shell,shell,"python benchmark.py --load medium",60
```

Expected output formats:
```bash
# Key-value format
p95=0.05 p99=0.08 throughput_rps=1000

# JSON format  
{"p95": 0.05, "p99": 0.08, "throughput_rps": 1000}
```

### 3. Simroute Backend
- **Purpose**: Integration with world-simulation framework
- **Behavior**: Executes simroute CLI with seed management
- **Use Case**: Running traffic simulations

```csv
case_id,backend,cmd_template,timeout_s,seed
test-simroute,simroute,"python -m simroute_cli --scenario urban --seed {seed}",120,42
```

## Working with Parallel Execution

### Basic Parallel Execution
```bash
# Use 4 worker threads
srd run --cases cases.csv --out metrics.csv --max-workers 4
```

### Resource Groups
Organize cases by resource requirements:

```csv
case_id,backend,cmd_template,timeout_s,resource_group
light-01,shell,"light_benchmark.py",30,light
light-02,shell,"light_benchmark.py",30,light  
heavy-01,shell,"heavy_benchmark.py",300,heavy
heavy-02,shell,"heavy_benchmark.py",300,heavy
```

DOE Runner respects resource groups for optimal scheduling.

## Caching and Reproducibility

### How Caching Works
DOE Runner calculates a `case_hash` from:
- case_id, backend, cmd_template
- timeout_s, seed, retries
- All deterministic case parameters

### Cache Control
```bash
# Use cache (default)
srd run --cases cases.csv --out metrics.csv

# Force re-execution (ignore cache)
srd run --cases cases.csv --out metrics.csv --force

# Check cache status
python -c "
from strataregula_doe_runner.plugin import DOERunnerPlugin
plugin = DOERunnerPlugin()
status = plugin.get_cache_status(cases_path='cases.csv')
print(f'Cache hits: {status[\"cache_hits\"]}')
"
```

### Ensuring Reproducibility
1. **Use seeds**: Always set `seed` column for deterministic results
2. **Fixed environments**: Use consistent execution environments
3. **Version pinning**: Pin dependency versions in your environment

## Threshold Validation

### Setting Thresholds
```csv
case_id,backend,cmd_template,timeout_s,expected_p95,threshold_p95,expected_p99,threshold_p99
perf-01,shell,"benchmark.py",60,0.10,0.12,0.15,0.18
```

### Exit Code Interpretation
- **0**: All tests passed, no threshold violations
- **2**: Tests completed but some thresholds were violated
- **3**: Execution failed (configuration error, I/O error, etc.)

### Handling Threshold Violations
```bash
#!/bin/bash
srd run --cases performance_cases.csv --out metrics.csv

case $? in
  0)
    echo "✅ All performance tests passed"
    ;;
  2) 
    echo "⚠️ Performance thresholds violated - check metrics.csv"
    # Still continue with deployment but with warnings
    ;;
  3)
    echo "❌ Execution failed - check logs"
    exit 1
    ;;
esac
```

## Plugin Usage

### As a Strataregula Plugin
```python
from strataregula_doe_runner.plugin import DOERunnerPlugin

# Initialize plugin  
plugin = DOERunnerPlugin()

# Get plugin info
info = plugin.get_info()
print(f"Plugin: {info['name']} v{info['version']}")

# Execute cases
result = plugin.execute_cases(
    cases_path="cases.csv",
    metrics_path="metrics.csv",
    max_workers=2,
    verbose=True
)

if result['status'] == 'success':
    print(f"✅ Execution completed with exit code {result['exit_code']}")
    stats = result['stats']
    print(f"Total cases: {stats['total_cases']}")
    print(f"Successful: {stats['successful']}")
    print(f"Failed: {stats['failed']}")
else:
    print(f"❌ Execution failed: {result['message']}")
```

### Plugin Commands
- `execute_cases`: Run experiment cases
- `validate_cases`: Validate case file format
- `get_cache_status`: Check cache statistics
- `clear_cache`: Clear cached results
- `get_adapters`: List available execution backends

## Environment Configuration

### Environment Variables
```bash
# Custom log directory
export RUN_LOG_DIR="/var/log/doe-runner"

# Compatibility mode (for legacy systems)
export RUN_LOG_WRITE_COMPAT=1

# Default worker count
export DOE_MAX_WORKERS=8
```

### Directory Structure
```
project/
├── cases/
│   ├── basic_cases.csv
│   └── performance_cases.csv
├── results/
│   ├── basic_metrics.csv
│   └── performance_metrics.csv
└── docs/
    └── run/                    # Run logs (JST timezone)
        ├── run_20250825_103000.md
        └── run_20250825_103001.md
```

## Common Patterns

### 1. Testing Pattern
```csv
case_id,backend,cmd_template,timeout_s,seed
unit-test-01,shell,"pytest tests/unit/test_core.py",30,42
unit-test-02,shell,"pytest tests/unit/test_api.py",30,123
integration-test-01,shell,"pytest tests/integration/",120,456
```

### 2. Performance Testing Pattern  
```csv
case_id,backend,cmd_template,timeout_s,threshold_p95,threshold_p99
load-light,shell,"wrk -t4 -c100 -d30s --latency http://api/endpoint",45,0.10,0.15
load-medium,shell,"wrk -t8 -c200 -d60s --latency http://api/endpoint",75,0.20,0.30
load-heavy,shell,"wrk -t12 -c400 -d120s --latency http://api/endpoint",135,0.50,1.00
```

### 3. Simulation Pattern
```csv
case_id,backend,cmd_template,timeout_s,seed,retries
sim-urban-rush,simroute,"python -m simroute_cli --scenario urban_rush --seed {seed}",300,42,2
sim-highway,simroute,"python -m simroute_cli --scenario highway --seed {seed}",300,123,2
sim-rural,simroute,"python -m simroute_cli --scenario rural --seed {seed}",300,456,1
```

## Next Steps

Now that you've run your first experiments, explore:

1. **[Cases CSV Format](cases-format.md)** - Complete specification of input format
2. **[Metrics Output](metrics-output.md)** - Understanding all output columns
3. **[CLI Reference](cli-reference.md)** - All available command-line options
4. **[Examples](../examples/basic.md)** - More complex use cases

## Troubleshooting

### Common Issues

#### Cases file not found
```bash
srd run --cases missing.csv --out metrics.csv
# Error: Cases file not found: missing.csv
```
**Solution**: Check file path and permissions

#### Invalid CSV format
```bash
# Error: Missing required column: backend
```
**Solution**: Ensure all required columns are present (case_id, backend, cmd_template, timeout_s)

#### Command timeout
```csv
case_id,backend,cmd_template,timeout_s
slow-test,shell,"sleep 60",30
# Will timeout after 30 seconds
```
**Solution**: Increase timeout_s or optimize the command

#### Permission errors
```bash
# Error: Permission denied executing command
```
**Solution**: Check file permissions and execution rights

### Getting Help

- **Documentation**: Continue reading this documentation
- **Examples**: Check the `examples/` directory
- **Issues**: [GitHub Issues](https://github.com/strataregula/strataregula-doe-runner/issues)  
- **Discussions**: [GitHub Discussions](https://github.com/strataregula/strataregula-doe-runner/discussions)

Ready to dive deeper? Continue with [Cases CSV Format](cases-format.md) to learn about all available options.