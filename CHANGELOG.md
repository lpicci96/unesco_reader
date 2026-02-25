# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [3.1.1] - 2026-02-25

### Fixed
- Fixed `available_indicators` and `available_versions` mutating cached API responses in place, causing `KeyError` on repeated calls
- Fixed `available_geo_units` using substring matching (`in`) instead of equality (`==`) for `geoUnitType` filtering
- Fixed `get_metadata` returning direct references to cached dicts, allowing callers to corrupt the cache

### Added
- Idempotency and cache-safety tests for `available_indicators`, `available_versions`, `available_geo_units`, `available_themes`, and `get_metadata`

## [3.1.0] - 2025-02-25

### Added
- In-memory session caching for API definition endpoints (`get_indicators`, `get_geo_units`, `get_versions`, `get_default_version`) to avoid redundant network calls
- `clear_cache()` function to manually invalidate all cached data mid-session
- Single retry with delay for transient network errors (timeouts, connection errors, 502/503/504 responses) with warning logs on retry attempts
- `set_max_retries()` function to configure the number of retries for transient network errors
- `py.typed` marker for PEP 561 type checker support
- `__all__` to `__init__.py` for explicit public API surface
- Live API smoke tests (opt-in via `RUN_LIVE_SMOKE_TESTS=1`)
- Full test coverage (100%) across all modules

### Changed
- Replaced library-level `StreamHandler` logging with per-module loggers and a `NullHandler`, following Python library best practices. Logs are now silent by default; users can configure the `unesco_reader` logger to enable output.
- Migrated dependency management from Poetry to uv
- Replaced `poetry-core` build backend with `hatchling`
- Converted `pyproject.toml` from Poetry format to PEP 621
- Updated CI workflows to use `astral-sh/setup-uv@v4`, `actions/checkout@v4`, `actions/setup-python@v5`, `codecov/codecov-action@v5`
- Expanded CI test matrix to include Python 3.13 and 3.14
- Updated core data formatting for indicators GET endpoint for clarity:
  - removed new `last_data_update` creation and instead edited the `lastDataUpdate` directly.
  - renamed fields `max` and `min` to `timeLine_min` and `timeLine_max` for clarity.

### Fixed
- Corrected `TooManyRecordsError` message in `core.get_data` to reference the actual 100,000 record limit instead of 1,000
- Fixed `_normalize_footnotes` mutating the original API response data in place
- Fixed `_check_for_too_many_records` crashing on non-JSON or unexpected 400 responses
- Fixed O(n) per-item scan in `_convert_codes` by using a reverse lookup set for code validation
- Corrected `geoUnitType` error message for consistent parameter naming using camel case

### Removed
- Removed `poetry.lock`, `requirements.txt`, and `requirements-dev.txt` (replaced by `uv.lock`)

## [3.0.0] - 2024-11-22

### Changed
- Refactored package to support the UIS API
- Removed support for bulk data files

## [2.0.0] - 2024-04-08

### Added
- Support for Python 3.12

### Removed
- Support for Python < 3.10

## [1.0.0] - 2024-04-04

### Added
- First stable release of the package
- Caching to the UIS class to speed up data retrieval

### Changed
- User interface and backend following UIS website changes (breaking)

## [0.3.1] - 2023-03-17

### Fixed
- Bug in data extraction to handle changes in UIS column naming conventions

## [0.3.0] - 2023-01-28

### Changed
- Reformatted package to use Poetry for dependency management
- Removed `link` and `regional` from `uis_datasets.csv` and from functions and methods returning info

## [0.2.0] - 2023-01-25

### Added
- Tests to cover `common` and `uis` modules

### Changed
- Reformatted UIS module function to read CSVs from zip file
- Reformatted UIS class attributes to be set in `__init__` method

## [0.1.2] - 2022-12-10

### Fixed
- Bug preventing regional data from being returned
- Optimized metadata retrieval

## [0.1.1] - 2022-12-09

### Fixed
- Typing bug in Python 3.8

## [0.1.0] - 2022-12-09

### Added
- Initial release of `unesco_reader` `uis` module

## [0.0.1] - 2022-09-16

### Added
- Initial release for testing
