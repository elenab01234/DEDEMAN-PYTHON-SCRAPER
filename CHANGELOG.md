# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [1.1.0] - 2026-09-21

### Changed
- Adapted the scraper for **DEDEMAN S.R.L.** (CIF `2816464`), replacing the
  E-INFRA/applytojob source with the Dedeman careers board
  (`https://recrutare.dedeman.ro`).
- `scraper/index.py` now consumes the sinapsi JSON API
  (`POST /api/sinapsi/jobs`) instead of parsing board HTML; `parse_api_jobs`
  reads `d.JobAnnounces` and job URLs are built as
  `/detalii-post?job=<title>&id=<id>`.
- `scraper/config/company.json` and `scraper/config/scraper.json` now hold the
  Dedeman identity and API endpoints (single source of truth).
- Stale-job deletion scoped to the Dedeman board prefix
  (`/detalii-post?`), taken from `scraper.json`.
- Added Dedeman store cities missing from the location allow-list
  (Alexandria, Barlad, Medias, Sfantu Gheorghe, Miercurea Ciuc,
  Campulung Moldovenesc).
- Removed the now-unused `beautifulsoup4` dependency.
- README, `docs/`, `ai/` documentation, workflows and tests updated to the
  Dedeman repo identity.

## [1.0.0] - 2026-08-03

### Added
- Python scraper for the E-INFRA S.A. department on the group's applytojob board (`?department=E-INFRA`).
- Publisher to peviitor v1 API: company upsert, job upload, stale-job delete.
- ANAF company validation with CUIScan fallback and cache.
- ANOFM job search mirroring the Node.js template.
- `validate_jobs.py` CLI for head/content URL validation.
- Unit, integration, e2e, and consistency tests.
- GitHub Actions workflows: `job-seeker-ro-spider`, `automation-testing`, deep-validate, recovery.
- GitHub Pages (`docs/`) with generated `jobs.md` and `company.json`.
- AI documentation under `ai/`.

### Fixed
- Location normalization: common spellings (`Bucuresti`, `Turda`, etc.) and case/diacritic variants are no longer dropped to `România`.
- Stale-job deletion is scoped to this scraper's applytojob board, so jobs published by other peviitor scrapers under the same CIF are never removed.
- E2E `EXPECTED_MIN_JOBS` and integration tests reflect the E-INFRA department and CIF `38647188`.
