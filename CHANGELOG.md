# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.1.0] - 2026-03-07

### Added
- Initial project structure and documentation
- `manifesto.md`, `taxonomy.md`, `source-policy.md`, `review-guidelines.md`, `attempt-policy.md`, `architecture.md`
- Chinese translations in `docs/zh/`
- JSON Schemas: `problem.schema.json`, `source.schema.json`, `attempt.schema.json`, `collection.schema.json`
- 50 gold-standard seed problems across 3 domains:
  - 25 Mathematics (number theory, combinatorics, graph theory, algebra, analysis, topology, geometry, probability, dynamical systems, logic)
  - 15 Theoretical CS (complexity theory, algorithms, graph algorithms, cryptography, information theory, quantum computing)
  - 10 Mathematical Physics (quantum information, statistical mechanics, quantum field theory, general relativity, condensed matter theory)
- 4 curated collections: Millennium Problems, Graph Theory Classics, Formalization Wanted, Solver-Ready
- 10 sample radar leads
- 3 sample AI attempts
- Data validation pipeline (`review/validators/validate_all.py`)
- Pre-commit configuration
- Ingestion pipeline with 7 source adapters: arXiv, OpenAlex, Crossref, Semantic Scholar, ErdosProblems, FormalConjectures, OpenProblemGarden
- Extraction pipeline: candidate extractor, status classifier, alias linker, deduplicator, ranking scorer
- Fetch cache for API responses
- Static site with 7 pages: index, problems explorer, problem detail, collections, radar, attempts, graph
- Client-side search and multi-dimensional filtering (domain, status, type, underexplored, formalizable, solver-ready)
- Relationship graph visualization
- JSON API endpoints (problems, collections, leads, attempts, stats)
- Parquet export support
- GitHub Issue templates (5 forms) and PR template
- GitHub Actions workflows: validate, lint-data, build-site, release-snapshot, refresh-radar
- GitHub labels configuration
- Benchmark protocol documentation
- 3 demo Jupyter notebooks
- `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `CITATION.cff`

### Notes
- v1 covers Mathematics, Theoretical CS, and Mathematical Physics only
- 50 verified problems (target: 300 for full launch)
- Monthly snapshot releases begin with this version
