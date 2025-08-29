"""
Strataregula plugin integration for DOE Runner
"""
import logging
from pathlib import Path
from typing import Any, Dict, Optional

from .core.runner import Runner
from .core.cache import CaseCache
from .core.validator import CaseValidator
from .io import CSVHandler
from .core.executor import CaseExecutor

logger = logging.getLogger(__name__)


class DOERunnerPlugin:
    """Strataregula plugin for DOE Runner batch experiment orchestrator."""

    name = "doe_runner"
    version = "0.1.0"
    description = "Batch experiment orchestrator for cases.csv → metrics.csv pipeline"
    author = "Strataregula Team"

    def __init__(self) -> None:
        self.runner: Optional[Runner] = None
        self.cache: Optional[CaseCache] = None
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
                "get_adapters",
            ],
            "supported_backends": ["shell", "dummy", "simroute"],
            "exit_codes": {
                "0": "All cases executed successfully",
                "2": "Threshold violations detected",
                "3": "Execution or configuration error",
            },
        }

    def execute_cases(
        self, cases_path: str, metrics_path: str = "metrics.csv", **options
    ) -> Dict[str, Any]:
        """Execute cases from CSV file."""
        try:
            cache_dir = Path(cases_path).parent / ".doe_cache"
            config = {
                "max_workers": options.get("max_workers", 1),
                "fail_fast": options.get("fail_fast", False),
                "force_rerun": options.get("force", False),
                "dry_run": options.get("dry_run", False),
                "verbose": options.get("verbose", False),
                "run_log_dir": options.get("run_log_dir", "docs/run"),
                "compat_mode": options.get("compat_mode", False),
            }

            if not Path(cases_path).exists():
                raise FileNotFoundError(f"Cases file not found: {cases_path}")

            self.runner = Runner(**config)
            self.cache = CaseCache(str(cache_dir))
            self.runner.cache = self.cache

            exit_code = self.runner.execute(
                cases_path,
                metrics_path,
                max_workers=config["max_workers"],
                dry_run=config["dry_run"],
                force=config["force_rerun"],
                verbose=config["verbose"],
            )

            stats = {
                "total_cases": self.runner.stats.get("total", 0),
                "successful": self.runner.stats.get("success", 0),
                "threshold_violations": self.runner.stats.get(
                    "threshold_violations_list", []
                ),
            }

            status = "success" if exit_code in (0, 2) else "error"
            result = {
                "status": status,
                "exit_code": exit_code,
                "exit_meaning": self._get_exit_meaning(exit_code),
                "stats": stats,
                "metrics_path": metrics_path,
            }
            if status == "error":
                result["message"] = "Execution failed"
            return result

        except Exception as e:
            logger.error(f"Execution failed: {e}")
            return {"status": "error", "exit_code": 3, "message": str(e)}

    def validate_cases(self, cases_path: str) -> Dict[str, Any]:
        """Validate cases CSV file format and content."""
        validator = CaseValidator()
        format_errors = validator.validate_file_format(cases_path)
        if format_errors:
            return {
                "status": "error",
                "valid": False,
                "validation_details": format_errors,
            }

        cases = CSVHandler().load_cases(cases_path)
        errors = validator.validate_cases(cases)
        return {
            "status": "success" if not errors else "error",
            "valid": not errors,
            "validation_details": errors,
        }

    def get_cache_status(self, cases_path: str) -> Dict[str, Any]:
        """Get cache status for given cases."""
        cache_dir = Path(cases_path).parent / ".doe_cache"
        cache = CaseCache(str(cache_dir))
        self.cache = cache
        try:
            cases = CSVHandler().load_cases(cases_path)
            runner = Runner()
            hits = 0
            for case in cases:
                case_hash = runner._compute_case_hash(case)
                if cache.exists(case_hash):
                    hits += 1
            return {"status": "success", "cache_hits": hits}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def clear_cache(self, cases_path: str) -> Dict[str, Any]:
        """Clear cache for given cases."""
        cache_dir = Path(cases_path).parent / ".doe_cache"
        cache = CaseCache(str(cache_dir))
        cleared = cache.clear()
        return {"status": "success", "cleared": cleared}

    def get_adapters(self) -> Dict[str, Any]:
        """List available adapters."""
        executor = CaseExecutor()
        adapters: Dict[str, Dict[str, Any]] = {}
        for name, adapter in executor.adapters.items():
            adapters[name] = {
                "description": getattr(adapter, "description", ""),
                "supported_features": getattr(adapter, "supported_features", []),
            }
        return {"status": "success", "adapters": adapters}

    def _get_exit_meaning(self, exit_code: int) -> str:
        """Get human-readable exit code meaning."""
        meanings = {
            0: "All cases executed successfully, thresholds met",
            2: "Execution completed but threshold violations detected",
            3: "I/O error, invalid configuration, or execution failure",
        }
        return meanings.get(exit_code, f"Unknown exit code: {exit_code}")


# Plugin factory function for strataregula
def create_plugin():
    """Factory function to create plugin instance."""
    return DOERunnerPlugin()
