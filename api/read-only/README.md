# Read-Only API

The OpenProblemAtlas exposes a read-only JSON API via static files generated at build time.

## Endpoints

All endpoints are served as static JSON files from the site build output.

### `GET /api/problems.json`

Returns all verified problems.

```json
[
  {
    "id": "opa.mathematics.number-theory.collatz-conjecture",
    "kind": "problem",
    "title": "Collatz conjecture",
    "status": { "label": "open", ... },
    "domain": "mathematics",
    ...
  }
]
```

### `GET /api/collections.json`

Returns all curated collections.

```json
[
  {
    "collection_id": "col_millennium-problems",
    "title": "Clay Millennium Prize Problems",
    "problems": [...]
  }
]
```

### `GET /api/leads.json`

Returns all radar leads.

### `GET /api/attempts.json`

Returns all recorded attempts.

### `GET /api/stats.json`

Returns aggregate statistics.

```json
{
  "total_problems": 50,
  "open_problems": 48,
  "solved_problems": 2,
  "domains": {
    "mathematics": 25,
    "theoretical-cs": 15,
    "mathematical-physics": 10
  },
  "total_collections": 5,
  "total_attempts": 3,
  "total_leads": 10
}
```

## Data Snapshots

Monthly frozen snapshots are available as GitHub releases:

- `problems.json` — All verified problems
- `problems.parquet` — Same data in Apache Parquet format (if available)

Download from: [Releases](https://github.com/OpenProblemAtlas/open-problem-atlas/releases)

## Usage

```python
import requests

# Fetch all problems
problems = requests.get("https://OpenProblemAtlas.github.io/open-problem-atlas/api/problems.json").json()

# Filter open problems in mathematics
open_math = [p for p in problems if p["status"]["label"] == "open" and p["domain"] == "mathematics"]
```

## Rate Limits

This is a static API with no rate limits. However, please be respectful and cache responses locally.

## Terms

Data is licensed under CC BY-SA 4.0. Please cite the project if you use this data in research.
