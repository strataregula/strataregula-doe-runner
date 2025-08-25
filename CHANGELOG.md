# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-01-24

### Added
- Initial implementation of batch experiment orchestrator
- Support for cases.csv → metrics.csv pipeline
- Shell and dummy execution adapters
- Deterministic CSV I/O with fixed column ordering
- case_hash based caching system
- Parallel execution with configurable workers
- Threshold validation with exit codes (0/2/3)
- JST timezone run logs with markdown format
- CLI interface with `srd` and `sr-doe` commands
- Strataregula plugin integration
- Comprehensive README with usage examples
- Apache-2.0 license

### Architecture
- Independent plugin design (no BasePlugin inheritance)
- Modular adapter system for different backends
- Forward-compatible naming convention (strataregula-*)
- Type-safe implementation with proper error handling

### Documentation
- Complete README with quick start guide
- API documentation for plugin commands
- Example cases.csv files
- Architecture decision records

[Unreleased]: https://github.com/unizontech/strataregula-doe-runner/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/unizontech/strataregula-doe-runner/releases/tag/v0.1.0