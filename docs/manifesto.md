# OpenProblemAtlas Manifesto

## The Problem We're Solving

Many important open problems remain unsolved not just because they're hard, but because they are:

- **Scattered** across papers, problem lists, community pages, and expert-maintained sites
- **Hard to find** without deep domain knowledge
- **Hard to compare** without standardized metadata
- **Lacking actionable entry points** for AI tools, theorem provers, and computational search

## Our Mission

Build a **public infrastructure** that makes open problems searchable, verifiable, contributable, and trackable — for researchers, students, AI agents, and theorem provers alike.

## What We Are

- A **structured, machine-readable database** of verified open problems
- A **radar system** that continuously mines new candidates from the literature
- A **lab** for tracking reproducible AI and human attempts
- A **community-governed** project with clear review standards

## What We Are NOT

- Not a news aggregation site
- Not a "future work" dump from papers
- Not a marketing repository for "AI solves hard problems"
- Not an attempt to cover all domains from day one

## Core Principles

### 1. Precision Over Coverage

We would rather have 300 perfectly verified problems than 10,000 noisy entries. The Atlas layer is our truth layer — it must be clean.

### 2. Layered Architecture

Three distinct layers prevent contamination:

| Layer | Purpose | Noise tolerance |
|-------|---------|-----------------|
| **Atlas** | Verified problems | Zero noise |
| **Radar** | Candidate problems | Noisy is OK |
| **Lab** | Attempts | Clearly labeled |

### 3. Source Accountability

Every fact must trace back to a canonical source. Machine-generated content is clearly marked and never mixed into the truth layer.

### 4. Open Governance

Status changes, especially `open → solved`, require evidence and human review. The project uses GitHub-native workflows (issues, PRs, reviews) for governance.

### 5. AI as Tool, Not Oracle

LLMs help with extraction, summarization, and candidate discovery. They never unilaterally determine whether a problem is open, what its canonical statement is, or whether a proof is valid.

## v1 Scope

**Domains:** Mathematics, Theoretical CS, Mathematical Physics (precise/formalizable subfields only)

**Not in v1:** Biology, chemistry, broad physics mysteries, problems requiring extensive experimental context

## Success Metrics

- 300+ verified problems with full provenance
- 1000+ radar leads
- 20+ gold-standard detail pages
- 3+ curated collections
- Functional search and filter
- JSON/Parquet data exports
- Monthly snapshot releases
