#!/usr/bin/env python3
"""
Build and test package script for PyPI preparation.
"""

import subprocess
import sys
import tempfile
import venv
from pathlib import Path


def run_command(cmd, cwd=None, check=True):
    """Run shell command and return result."""
    print(f"Running: {cmd}")
    result = subprocess.run(
        cmd, 
        shell=True, 
        cwd=cwd, 
        capture_output=True, 
        text=True, 
        check=check
    )
    if result.stdout:
        print("STDOUT:", result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    return result


def main():
    """Main build and test workflow."""
    project_root = Path(__file__).parent.parent
    print(f"Project root: {project_root}")
    
    # Clean previous builds
    print("\n🧹 Cleaning previous builds...")
    for path in ["build", "dist", "*.egg-info"]:
        run_command(f"rm -rf {path}", cwd=project_root, check=False)
    
    # Build package
    print("\n📦 Building package...")
    run_command("python -m build", cwd=project_root)
    
    # Check package
    print("\n🔍 Checking package...")
    run_command("python -m twine check dist/*", cwd=project_root)
    
    # Test installation in clean environment
    print("\n🧪 Testing installation in clean environment...")
    with tempfile.TemporaryDirectory() as temp_dir:
        venv_path = Path(temp_dir) / "test_venv"
        
        # Create virtual environment
        print(f"Creating virtual environment at {venv_path}")
        venv.create(venv_path, with_pip=True)
        
        # Determine activation script
        if sys.platform == "win32":
            activate_script = venv_path / "Scripts" / "activate"
            pip_cmd = str(venv_path / "Scripts" / "pip")
            python_cmd = str(venv_path / "Scripts" / "python")
        else:
            activate_script = venv_path / "bin" / "activate"
            pip_cmd = str(venv_path / "bin" / "pip")
            python_cmd = str(venv_path / "bin" / "python")
        
        # Find wheel file
        dist_dir = project_root / "dist"
        wheel_files = list(dist_dir.glob("*.whl"))
        if not wheel_files:
            print("❌ No wheel file found!")
            return 1
        
        wheel_file = wheel_files[0]
        print(f"Testing wheel: {wheel_file}")
        
        # Install package from wheel
        print("Installing package from wheel...")
        run_command(f"{pip_cmd} install '{wheel_file}'")
        
        # Test CLI
        print("Testing CLI...")
        result = run_command(f"{python_cmd} -c 'from strataregula_doe_runner.cli.main import main; main()'", 
                           check=False)
        
        # Test plugin
        print("Testing plugin...")
        test_plugin_code = """
from strataregula_doe_runner.plugin import DOERunnerPlugin
plugin = DOERunnerPlugin()
info = plugin.get_info()
print(f"Plugin: {info['name']} v{info['version']}")
assert info['name'] == 'doe_runner'
print("✅ Plugin test passed!")
"""
        run_command(f"{python_cmd} -c \"{test_plugin_code}\"")
        
        # Test entry points
        print("Testing entry points...")
        entry_point_test = """
import pkg_resources
eps = list(pkg_resources.iter_entry_points('strataregula.plugins'))
doe_runner_eps = [ep for ep in eps if ep.name == 'doe_runner']
assert len(doe_runner_eps) > 0, 'DOE Runner entry point not found'
plugin_class = doe_runner_eps[0].load()
plugin = plugin_class()
assert plugin.get_info()['name'] == 'doe_runner'
print("✅ Entry point test passed!")
"""
        run_command(f"{python_cmd} -c \"{entry_point_test}\"")
    
    print("\n✅ All tests passed! Package is ready for PyPI.")
    
    # Show next steps
    print("\n📋 Next steps:")
    print("1. Test upload to TestPyPI:")
    print("   python -m twine upload --repository testpypi dist/*")
    print("\n2. Test installation from TestPyPI:")
    print("   pip install -i https://test.pypi.org/simple/ strataregula-doe-runner")
    print("\n3. Upload to PyPI:")
    print("   python -m twine upload dist/*")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())