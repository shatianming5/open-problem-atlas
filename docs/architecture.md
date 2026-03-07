# Architecture

## Overview

OpenProblemAtlas is a monorepo with four logical layers:

```
┌─────────────────────────────────────────┐
│           Explorer / Site               │  ← Presentation layer
├─────────────────────────────────────────┤
│  Atlas (verified)  │  Radar (leads)     │  ← Data layers
│  Lab (attempts)    │  Collections       │
├─────────────────────────────────────────┤
│         Ingestion + Extraction          │  ← Pipeline layer
├─────────────────────────────────────────┤
│     Schema + Validators + CI            │  ← Quality layer
└─────────────────────────────────────────┘
```

## Data Flow

```
Source Adapters → Raw Source Records → Section Splitter → Candidate Extractor
    → Status Classifier → Alias Linker → Dedupe → Reviewer Queue → Publish Build
```

### Pipeline Stages

1. **Source Adapter**: Converts external content into unified `source` records
2. **Section Splitter**: Identifies relevant sections (Open Problems, Conjectures, Future Work)
3. **Candidate Extractor**: Uses rules + LLM to extract candidate problem statements
4. **Status Classifier**: Classifies candidates as open/solved/future-work/vague/non-problem
5. **Alias Linker**: Merges different names for the same problem
6. **Dedupe**: Prevents duplicate entries across sources
7. **Reviewer Queue**: Human review gate before promotion to Atlas
8. **Publish Build**: Generates site, search index, release artifacts from canonical data

## Storage Strategy

### In Repository
- Canonical YAML data files (problems, leads, attempts, collections)
- JSON Schemas for validation
- Code (adapters, extractors, validators, site)
- Configuration and CI/CD

### NOT in Repository
- Raw full-text PDFs
- Cached web pages
- Large binary artifacts
- API keys or credentials

## Technology Choices

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Data format | YAML | Human-readable, contributor-friendly |
| Schema | JSON Schema | Standard, tooling-rich |
| Validation | Python + jsonschema | Simple, extensible |
| CI/CD | GitHub Actions | Native to GitHub |
| Site | Static (Jinja2 + vanilla JS) | No server needed, free hosting |
| API | Static JSON files | Zero infrastructure cost |
| Ingestion | Python + httpx | Async-capable, clean |
| Extraction | Python + LLM APIs | Flexible model choice |

## Scalability Path

v1 targets:
- ~300 verified problems → YAML files in git
- ~1000 leads → YAML files in git
- Static site on GitHub Pages

If growth demands it:
- Move to SQLite or PostgreSQL for data
- Add server-side API
- Use CDN for site
- Move extraction to cloud workers
