import os
import sys
import click

from ..core.runner import Runner
from ..core.validator import CaseValidator


def get_version() -> str:
    """Return package version."""
    return Runner.VERSION


def run_command(
    *,
    cases_path: str,
    metrics_path: str = "metrics.csv",
    max_workers: int = 1,
    fail_fast: bool = False,
    force: bool = False,
    dry_run: bool = False,
    verbose: bool = False,
) -> int:
    """Execute cases via Runner and return exit code."""
    runner = Runner(
        max_workers=max_workers,
        fail_fast=fail_fast,
        force_rerun=force,
        dry_run=dry_run,
        verbose=verbose,
        run_log_dir=os.getenv("RUN_LOG_DIR", "docs/run"),
        compat_mode=os.getenv("RUN_LOG_WRITE_COMPAT", "0") == "1",
    )
    return runner.execute(
        cases_path,
        metrics_path,
        max_workers=max_workers,
        dry_run=dry_run,
        force=force,
        verbose=verbose,
    )


@click.group()
@click.version_option(version=get_version())
def cli() -> None:
    """Strataregula DOE Runner - Batch experiment orchestrator"""


@cli.command(name="run")
@click.option("--cases", required=True, type=click.Path(exists=True))
@click.option("--out", default="metrics.csv")
@click.option("--max-workers", default=1, type=int)
@click.option("--fail-fast", is_flag=True)
@click.option("--force", is_flag=True)
@click.option("--dry-run", is_flag=True)
@click.option("--verbose", "-v", is_flag=True)
def run_cli(cases, out, max_workers, fail_fast, force, dry_run, verbose) -> None:
    """CLI wrapper around run_command."""
    code = run_command(
        cases_path=cases,
        metrics_path=out,
        max_workers=max_workers,
        fail_fast=fail_fast,
        force=force,
        dry_run=dry_run,
        verbose=verbose,
    )
    sys.exit(code)


@cli.command()
@click.option("--cases", required=True, type=click.Path(exists=True))
def validate(cases) -> None:
    """Validate cases CSV file."""
    validator = CaseValidator()
    errors = validator.validate_file_format(cases)
    if errors:
        click.echo("File format errors:", err=True)
        for error in errors:
            click.echo(f"- {error}", err=True)
        sys.exit(1)
    click.echo("\u2713 Validation passed")


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
