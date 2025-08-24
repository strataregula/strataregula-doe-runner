"""
Run log writer stub
"""
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List

class RunlogWriter:
    """Simple runlog writer for testing"""
    
    def __init__(self, log_path: Path, compat_mode: bool = False):
        self.log_path = Path(log_path)
        self.compat_mode = compat_mode
        self.content = []
        
        # Create directory
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
    
    def write_header(self, start_time: datetime, cases_path: str, total_cases: int):
        """Write log header"""
        self.content.append(f"# DOE Runner Execution Log")
        self.content.append(f"")
        self.content.append(f"**Started:** {start_time.isoformat()}")
        self.content.append(f"**Cases File:** {cases_path}")
        self.content.append(f"**Total Cases:** {total_cases}")
        self.content.append(f"")
    
    def write_summary(self, stats: Dict, results: List, duration: timedelta):
        """Write execution summary"""
        self.content.append(f"## Summary")
        self.content.append(f"")
        self.content.append(f"- **Duration:** {duration}")
        self.content.append(f"- **Total Cases:** {stats.get('total', 0)}")
        self.content.append(f"- **Success:** {stats.get('success', 0)}")
        self.content.append(f"- **Failed:** {stats.get('failed', 0)}")
        self.content.append(f"- **Timeout:** {stats.get('timeout', 0)}")
        self.content.append(f"- **Skipped (Cached):** {stats.get('skipped', 0)}")
        self.content.append(f"")
        
        # Write to file
        with open(self.log_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.content))
    
    def write_artifacts(self, artifact_paths: List[str]):
        """Write artifact references"""
        if artifact_paths:
            self.content.append("## Artifacts")
            for path in artifact_paths:
                self.content.append(f"- {path}")
            self.content.append("")
    
    def has_non_empty_summary(self) -> bool:
        """Check if summary is non-empty"""
        return len(self.content) > 5  # Header + some content