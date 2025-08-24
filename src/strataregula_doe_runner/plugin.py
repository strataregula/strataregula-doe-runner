"""
Strataregula plugin integration for DOE Runner
"""
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
import json

from .core.runner import Runner
from .core.cache import CaseCache

logger = logging.getLogger(__name__)

class DOERunnerPlugin:
    """Strataregula plugin for DOE Runner batch experiment orchestrator."""
    
    # Plugin metadata
    name = "doe_runner"
    version = "0.1.0"
    description = "Batch experiment orchestrator for cases.csv → metrics.csv pipeline"
    author = "Strataregula Team"
    
    def __init__(self):
        """Initialize DOE Runner plugin."""
        self.runner = None
        self.cache = CaseCache()
        logger.info(f"Initialized {self.name} v{self.version}")
    
    def get_info(self) -> Dict[str, Any]:
        """Get plugin information."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "supported_commands": [
                "execute_cases",
                "validate_cases", 
                "get_cache_status",
                "clear_cache",
                "get_adapters"
            ],
            "supported_backends": ["shell", "dummy", "simroute"],
            "exit_codes": {
                "0": "All cases executed successfully",
                "2": "Threshold violations detected",
                "3": "Execution or configuration error"
            }
        }
    
    def execute_cases(self, cases_path: str, metrics_path: str = "metrics.csv",
                     **options) -> Dict[str, Any]:
        """Execute cases from CSV file."""
        try:
            config = {
                'max_workers': options.get('max_workers', 1),
                'fail_fast': options.get('fail_fast', False),
                'force_rerun': options.get('force', False),
                'dry_run': options.get('dry_run', False),
                'verbose': options.get('verbose', False),
                'run_log_dir': options.get('run_log_dir', 'docs/run'),
                'compat_mode': options.get('compat_mode', False)
            }
            
            self.runner = Runner(**config)
            exit_code = self.runner.execute(cases_path, metrics_path)
            
            return {
                "status": "success",
                "exit_code": exit_code,
                "exit_meaning": self._get_exit_meaning(exit_code),
                "cases_path": cases_path,
                "metrics_path": metrics_path,
                "stats": self.runner.stats if self.runner else {}
            }
            
        except Exception as e:
            logger.error(f"Execution failed: {e}")
            return {
                "status": "error",
                "exit_code": 3,
                "message": str(e)
            }
    
    def _get_exit_meaning(self, exit_code: int) -> str:
        """Get human-readable exit code meaning."""
        meanings = {
            0: "All cases executed successfully, thresholds met",
            2: "Execution completed but threshold violations detected", 
            3: "I/O error, invalid configuration, or execution failure"
        }
        return meanings.get(exit_code, f"Unknown exit code: {exit_code}")

# Plugin factory function for strataregula
def create_plugin():
    """Factory function to create plugin instance."""
    return DOERunnerPlugin()