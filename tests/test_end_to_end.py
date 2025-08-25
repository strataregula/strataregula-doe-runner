"""End-to-end integration tests for DOE Runner."""

import csv
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from strataregula_doe_runner.core.runner import Runner
from strataregula_doe_runner.plugin import DOERunnerPlugin


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_cases_csv(temp_dir):
    """Create a sample cases.csv file."""
    cases_file = temp_dir / "cases.csv"
    
    with open(cases_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'case_id', 'backend', 'cmd_template', 'timeout_s', 
            'seed', 'retries', 'resource_group', 'expected_p95', 'threshold_p95'
        ])
        writer.writerow([
            'test-01', 'dummy', 'dummy simulation', '10', 
            '42', '1', 'default', '0.05', '0.06'
        ])
        writer.writerow([
            'test-02', 'shell', "echo 'p95=0.08 p99=0.12 throughput_rps=500'", '10',
            '123', '1', 'default', '0.08', '0.10'
        ])
        writer.writerow([
            'test-03', 'shell', "echo 'p95=0.15 p99=0.20 throughput_rps=200'", '10',
            '456', '0', 'default', '0.12', '0.12'  # This will trigger threshold violation
        ])
    
    return cases_file


@pytest.fixture
def performance_cases_csv(temp_dir):
    """Create performance test cases with larger dataset."""
    cases_file = temp_dir / "perf_cases.csv"
    
    with open(cases_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'case_id', 'backend', 'cmd_template', 'timeout_s', 
            'seed', 'retries', 'resource_group'
        ])
        
        # Generate 50 test cases
        for i in range(50):
            writer.writerow([
                f'perf-{i:02d}', 'dummy', f'dummy simulation {i}', '5',
                str(i * 10), '0', 'perf'
            ])
    
    return cases_file


class TestEndToEndWorkflow:
    """Test complete DOE Runner workflow."""
    
    def test_complete_workflow_success(self, sample_cases_csv, temp_dir):
        """Test complete workflow: cases.csv → execution → metrics.csv → validation."""
        metrics_file = temp_dir / "metrics.csv"
        
        # Execute via Runner
        runner = Runner()
        exit_code = runner.execute(
            cases_path=str(sample_cases_csv),
            metrics_path=str(metrics_file),
            max_workers=1,
            verbose=True
        )
        
        # Should return exit code 2 due to threshold violation in test-03
        assert exit_code == 2
        assert metrics_file.exists()
        
        # Verify metrics CSV structure
        with open(metrics_file, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        assert len(rows) == 3  # All 3 cases should be executed
        
        # Verify required columns
        expected_columns = ['case_id', 'status', 'run_seconds', 'p95', 'p99', 
                          'throughput_rps', 'errors', 'ts_start', 'ts_end']
        for col in expected_columns:
            assert col in rows[0].keys()
        
        # Verify case results
        results_by_id = {row['case_id']: row for row in rows}
        
        # test-01 (dummy) should succeed
        assert results_by_id['test-01']['status'] == 'OK'
        
        # test-02 (shell with metrics) should succeed
        assert results_by_id['test-02']['status'] == 'OK'
        assert float(results_by_id['test-02']['p95']) == 0.08
        assert float(results_by_id['test-02']['throughput_rps']) == 500
        
        # test-03 (threshold violation) should succeed but violate threshold
        assert results_by_id['test-03']['status'] == 'OK'
        assert float(results_by_id['test-03']['p95']) == 0.15  # Above threshold of 0.12
    
    def test_workflow_with_cache(self, sample_cases_csv, temp_dir):
        """Test workflow with caching - second run should use cache."""
        metrics_file = temp_dir / "metrics.csv"
        
        runner = Runner()
        
        # First execution
        exit_code1 = runner.execute(
            cases_path=str(sample_cases_csv),
            metrics_path=str(metrics_file),
            max_workers=1
        )
        
        first_metrics = []
        with open(metrics_file, 'r') as f:
            reader = csv.DictReader(f)
            first_metrics = list(reader)
        
        # Second execution (should use cache)
        metrics_file_2 = temp_dir / "metrics2.csv"
        exit_code2 = runner.execute(
            cases_path=str(sample_cases_csv),
            metrics_path=str(metrics_file_2),
            max_workers=1
        )
        
        second_metrics = []
        with open(metrics_file_2, 'r') as f:
            reader = csv.DictReader(f)
            second_metrics = list(reader)
        
        # Both executions should have same exit code
        assert exit_code1 == exit_code2
        
        # Results should be identical (deterministic)
        assert len(first_metrics) == len(second_metrics)
        
        for i, (first, second) in enumerate(zip(first_metrics, second_metrics)):
            assert first['case_id'] == second['case_id']
            assert first['status'] == second['status']
            # Note: execution times may differ slightly due to cache hits
    
    def test_force_execution_bypasses_cache(self, sample_cases_csv, temp_dir):
        """Test that --force flag bypasses cache."""
        metrics_file = temp_dir / "metrics.csv"
        
        runner = Runner()
        
        # First execution
        runner.execute(
            cases_path=str(sample_cases_csv),
            metrics_path=str(metrics_file),
            max_workers=1
        )
        
        # Force execution (bypass cache)
        metrics_file_2 = temp_dir / "metrics_force.csv"
        exit_code = runner.execute(
            cases_path=str(sample_cases_csv),
            metrics_path=str(metrics_file_2),
            max_workers=1,
            force=True  # This should bypass cache
        )
        
        assert exit_code == 2  # Should still have threshold violations
        assert metrics_file_2.exists()
    
    def test_dry_run_validation(self, sample_cases_csv, temp_dir):
        """Test dry run mode - validation only, no execution."""
        metrics_file = temp_dir / "metrics_dry.csv"
        
        runner = Runner()
        exit_code = runner.execute(
            cases_path=str(sample_cases_csv),
            metrics_path=str(metrics_file),
            dry_run=True
        )
        
        # Dry run should succeed (validation only)
        assert exit_code == 0
        # No metrics file should be created
        assert not metrics_file.exists()
    
    def test_parallel_execution(self, performance_cases_csv, temp_dir):
        """Test parallel execution with multiple workers."""
        metrics_file = temp_dir / "metrics_parallel.csv"
        
        runner = Runner()
        exit_code = runner.execute(
            cases_path=str(performance_cases_csv),
            metrics_path=str(metrics_file),
            max_workers=4,  # Use 4 workers for parallel execution
            verbose=True
        )
        
        assert exit_code == 0  # Should succeed
        assert metrics_file.exists()
        
        # Verify all cases were executed
        with open(metrics_file, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        assert len(rows) == 50  # All performance test cases
        
        # All should be successful (dummy backend)
        for row in rows:
            assert row['status'] == 'OK'
    
    def test_invalid_cases_file(self, temp_dir):
        """Test handling of invalid cases file."""
        invalid_cases = temp_dir / "invalid.csv"
        
        # Create invalid CSV (missing required columns)
        with open(invalid_cases, 'w') as f:
            f.write("case_id,invalid_column\ntest,value\n")
        
        metrics_file = temp_dir / "metrics.csv"
        
        runner = Runner()
        exit_code = runner.execute(
            cases_path=str(invalid_cases),
            metrics_path=str(metrics_file)
        )
        
        # Should fail with exit code 3 (configuration error)
        assert exit_code == 3
        # No metrics file should be created
        assert not metrics_file.exists()
    
    def test_missing_cases_file(self, temp_dir):
        """Test handling of missing cases file."""
        missing_file = temp_dir / "nonexistent.csv"
        metrics_file = temp_dir / "metrics.csv"
        
        runner = Runner()
        exit_code = runner.execute(
            cases_path=str(missing_file),
            metrics_path=str(metrics_file)
        )
        
        # Should fail with exit code 3 (I/O error)
        assert exit_code == 3


class TestPluginIntegration:
    """Test plugin interface and integration."""
    
    def test_plugin_discovery_and_execution(self, sample_cases_csv, temp_dir):
        """Test plugin discovery and execution through plugin interface."""
        metrics_file = temp_dir / "plugin_metrics.csv"
        
        # Test plugin instantiation
        plugin = DOERunnerPlugin()
        
        # Verify plugin info
        info = plugin.get_info()
        assert info['name'] == 'doe_runner'
        assert 'execute_cases' in info['supported_commands']
        
        # Execute via plugin interface
        result = plugin.execute_cases(
            cases_path=str(sample_cases_csv),
            metrics_path=str(metrics_file),
            max_workers=1,
            verbose=True
        )
        
        # Verify result structure
        assert result['status'] == 'success'
        assert result['exit_code'] == 2  # Threshold violations
        assert 'stats' in result
        
        # Verify stats
        stats = result['stats']
        assert stats['total_cases'] == 3
        assert stats['successful'] == 3  # All cases execute successfully
        assert len(stats['threshold_violations']) > 0  # But have threshold violations
        
        # Verify metrics file was created
        assert metrics_file.exists()
    
    def test_plugin_validation_command(self, sample_cases_csv):
        """Test plugin validation command."""
        plugin = DOERunnerPlugin()
        
        result = plugin.validate_cases(cases_path=str(sample_cases_csv))
        
        assert result['status'] == 'success'
        assert result['valid'] is True
        assert 'validation_details' in result
    
    def test_plugin_cache_status(self, sample_cases_csv, temp_dir):
        """Test plugin cache status command."""
        plugin = DOERunnerPlugin()
        
        # Initially no cache
        result = plugin.get_cache_status(cases_path=str(sample_cases_csv))
        assert result['status'] == 'success'
        assert result['cache_hits'] == 0
        
        # Execute cases to populate cache
        metrics_file = temp_dir / "cache_test_metrics.csv"
        plugin.execute_cases(
            cases_path=str(sample_cases_csv),
            metrics_path=str(metrics_file),
            max_workers=1
        )
        
        # Check cache status again
        result = plugin.get_cache_status(cases_path=str(sample_cases_csv))
        assert result['status'] == 'success'
        assert result['cache_hits'] > 0  # Should have cache hits now
    
    def test_plugin_clear_cache(self, sample_cases_csv, temp_dir):
        """Test plugin cache clearing."""
        plugin = DOERunnerPlugin()
        
        # Execute cases to populate cache
        metrics_file = temp_dir / "clear_cache_metrics.csv"
        plugin.execute_cases(
            cases_path=str(sample_cases_csv),
            metrics_path=str(metrics_file)
        )
        
        # Verify cache exists
        cache_status = plugin.get_cache_status(cases_path=str(sample_cases_csv))
        assert cache_status['cache_hits'] > 0
        
        # Clear cache
        result = plugin.clear_cache(cases_path=str(sample_cases_csv))
        assert result['status'] == 'success'
        
        # Verify cache is cleared
        cache_status = plugin.get_cache_status(cases_path=str(sample_cases_csv))
        assert cache_status['cache_hits'] == 0
    
    def test_plugin_error_handling(self, temp_dir):
        """Test plugin error handling with invalid inputs."""
        plugin = DOERunnerPlugin()
        
        # Test with missing cases file
        result = plugin.execute_cases(
            cases_path="nonexistent.csv",
            metrics_path="output.csv"
        )
        
        assert result['status'] == 'error'
        assert 'message' in result
        assert 'not found' in result['message'].lower()
    
    def test_plugin_get_adapters(self):
        """Test plugin adapter listing."""
        plugin = DOERunnerPlugin()
        
        result = plugin.get_adapters()
        
        assert result['status'] == 'success'
        assert 'adapters' in result
        
        adapters = result['adapters']
        assert 'dummy' in adapters
        assert 'shell' in adapters
        
        # Verify adapter info structure
        for adapter_name, adapter_info in adapters.items():
            assert 'description' in adapter_info
            assert 'supported_features' in adapter_info


class TestCLIIntegration:
    """Test CLI command integration."""
    
    @patch('strataregula_doe_runner.cli.main.Runner')
    def test_cli_basic_execution(self, mock_runner_class, sample_cases_csv):
        """Test CLI command execution."""
        from strataregula_doe_runner.cli.main import run_command
        
        # Mock runner
        mock_runner = mock_runner_class.return_value
        mock_runner.execute.return_value = 0
        
        # Test CLI command
        exit_code = run_command(
            cases_path=str(sample_cases_csv),
            metrics_path="test_output.csv",
            max_workers=1,
            verbose=False
        )
        
        assert exit_code == 0
        mock_runner.execute.assert_called_once()
    
    def test_cli_help_and_version(self):
        """Test CLI help and version commands."""
        from strataregula_doe_runner.cli.main import get_version
        
        # Test version
        version = get_version()
        assert version is not None
        assert len(version) > 0


class TestDeterministicOutput:
    """Test output determinism and reproducibility."""
    
    def test_deterministic_metrics_output(self, sample_cases_csv, temp_dir):
        """Test that metrics output is deterministic across runs."""
        runner = Runner()
        
        # Execute twice with same parameters
        metrics1 = temp_dir / "det1.csv"
        metrics2 = temp_dir / "det2.csv"
        
        runner.execute(
            cases_path=str(sample_cases_csv),
            metrics_path=str(metrics1),
            force=True  # Bypass cache for fair comparison
        )
        
        runner.execute(
            cases_path=str(sample_cases_csv),
            metrics_path=str(metrics2),
            force=True  # Bypass cache for fair comparison
        )
        
        # Compare file contents (excluding timestamp columns which may vary slightly)
        with open(metrics1, 'r') as f1, open(metrics2, 'r') as f2:
            reader1 = csv.DictReader(f1)
            reader2 = csv.DictReader(f2)
            
            rows1 = list(reader1)
            rows2 = list(reader2)
            
            assert len(rows1) == len(rows2)
            
            for row1, row2 in zip(rows1, rows2):
                # Compare deterministic fields
                assert row1['case_id'] == row2['case_id']
                assert row1['status'] == row2['status']
                assert row1['p95'] == row2['p95']
                assert row1['p99'] == row2['p99']
                assert row1['throughput_rps'] == row2['throughput_rps']
                assert row1['errors'] == row2['errors']
    
    def test_csv_format_compliance(self, sample_cases_csv, temp_dir):
        """Test that output CSV follows format specifications."""
        metrics_file = temp_dir / "format_test.csv"
        
        runner = Runner()
        runner.execute(
            cases_path=str(sample_cases_csv),
            metrics_path=str(metrics_file)
        )
        
        # Read and verify CSV format
        with open(metrics_file, 'rb') as f:
            content = f.read()
        
        # Verify LF line endings
        assert b'\r\n' not in content, "Should use LF line endings, not CRLF"
        
        # Verify CSV structure
        with open(metrics_file, 'r') as f:
            reader = csv.reader(f)
            header = next(reader)
            
            # Verify required columns are present and in correct order
            required_start = ['case_id', 'status', 'run_seconds', 'p95', 'p99', 
                            'throughput_rps', 'errors', 'ts_start', 'ts_end']
            
            for i, required_col in enumerate(required_start):
                assert header[i] == required_col, f"Column {i} should be {required_col}, got {header[i]}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])