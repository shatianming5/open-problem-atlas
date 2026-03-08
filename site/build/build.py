"""Build static site from atlas data."""

import json
import shutil
from pathlib import Path

import yaml
from jinja2 import ChainableUndefined, Environment, FileSystemLoader

ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = ROOT / "data"
CONTRACTS_DIR = ROOT / "verifiers" / "contracts"
TEMPLATES_DIR = Path(__file__).parent.parent / "app" / "templates"
OUTPUT_DIR = Path(__file__).parent / "output"
STATIC_DIR = Path(__file__).parent.parent / "app" / "static"


def load_problems() -> list[dict]:
    """Load all verified problems."""
    problems = []
    problems_dir = DATA_DIR / "problems"
    for yaml_file in sorted(problems_dir.rglob("*.yaml")):
        with open(yaml_file) as f:
            data = yaml.safe_load(f)
            if data:
                problems.append(data)
    return problems


def load_collections() -> list[dict]:
    """Load all collections."""
    collections = []
    collections_dir = DATA_DIR / "collections"
    for yaml_file in sorted(collections_dir.rglob("*.yaml")):
        with open(yaml_file) as f:
            data = yaml.safe_load(f)
            if data:
                collections.append(data)
    return collections


def load_attempts() -> list[dict]:
    """Load all attempts."""
    attempts = []
    attempts_dir = DATA_DIR / "attempts"
    if attempts_dir.exists():
        for yaml_file in sorted(attempts_dir.rglob("*.yaml")):
            with open(yaml_file) as f:
                data = yaml.safe_load(f)
                if data:
                    attempts.append(data)
    return attempts


def load_leads() -> list[dict]:
    """Load all leads."""
    leads = []
    leads_dir = DATA_DIR / "leads"
    if leads_dir.exists():
        for yaml_file in sorted(leads_dir.rglob("*.yaml")):
            with open(yaml_file) as f:
                data = yaml.safe_load(f)
                if data:
                    leads.append(data)
    # Sort by discovered_at descending (newest first)
    leads.sort(key=lambda x: x.get("discovered_at", ""), reverse=True)
    return leads


def build_graph_data(problems: list[dict], problems_by_id: dict) -> dict:
    """Build graph data from problem relations and shared domains/subdomains."""
    nodes = []
    edges = []
    node_ids = set()
    edge_set = set()

    for p in problems:
        pid = p["id"]
        slug = pid.replace(".", "-")
        nodes.append({
            "id": pid,
            "title": p.get("title", pid),
            "domain": p.get("domain", "unknown"),
            "slug": slug,
        })
        node_ids.add(pid)

        # Extract relations if present (dict format: {equivalent_to: [], related: [], ...})
        relations = p.get("relations", {})
        if isinstance(relations, dict):
            for rel_type, target_ids in relations.items():
                if not isinstance(target_ids, list):
                    continue
                for target_id in target_ids:
                    if target_id and target_id in problems_by_id:
                        edge_key = tuple(sorted([pid, target_id]))
                        if edge_key not in edge_set:
                            edge_set.add(edge_key)
                            edges.append({
                                "source": pid,
                                "target": target_id,
                                "label": rel_type,
                            })

    # If no explicit relations exist, create edges based on shared subdomains
    if not edges:
        subdomain_map = {}
        for p in problems:
            for sd in p.get("subdomains", []):
                subdomain_map.setdefault(sd, []).append(p["id"])
        for sd, pids in subdomain_map.items():
            for i in range(len(pids)):
                for j in range(i + 1, len(pids)):
                    edge_key = tuple(sorted([pids[i], pids[j]]))
                    if edge_key not in edge_set:
                        edge_set.add(edge_key)
                        edges.append({
                            "source": pids[i],
                            "target": pids[j],
                            "label": sd,
                        })

    return {"nodes": nodes, "edges": edges}


def load_contracts() -> dict[str, dict]:
    """Load all verifier contracts, keyed by problem_id."""
    contracts = {}
    if CONTRACTS_DIR.exists():
        for yaml_file in sorted(CONTRACTS_DIR.glob("*.yaml")):
            with open(yaml_file) as f:
                data = yaml.safe_load(f)
                if data and data.get("problem_id"):
                    contracts[data["problem_id"]] = data
    return contracts


def build():
    """Build the static site."""
    # Load data
    problems = load_problems()
    collections = load_collections()
    attempts = load_attempts()
    leads = load_leads()
    contracts = load_contracts()

    # Create problem index by ID
    problems_by_id = {p["id"]: p for p in problems}

    # Enrich attempts with problem titles
    for att in attempts:
        pid = att.get("problem_id", "")
        if pid in problems_by_id:
            att["problem_title"] = problems_by_id[pid].get("title", pid)

    # Sort attempts by date descending (newest first)
    attempts.sort(key=lambda x: x.get("date", ""), reverse=True)

    # Compute stats
    stats = {
        "total_problems": len(problems),
        "open_problems": sum(1 for p in problems if p.get("status", {}).get("label") == "open"),
        "solved_problems": sum(1 for p in problems if p.get("status", {}).get("label") == "solved"),
        "domains": {},
        "total_collections": len(collections),
        "total_attempts": len(attempts),
        "total_leads": len(leads),
    }

    for p in problems:
        domain = p.get("domain", "unknown")
        stats["domains"][domain] = stats["domains"].get(domain, 0) + 1

    # Machine-verifiable count (problems with a verifier contract)
    stats["machine_verifiable"] = sum(1 for p in problems if p["id"] in contracts)

    # Enrich problems with contract info
    for p in problems:
        p["_has_contract"] = p["id"] in contracts
        if p["id"] in contracts:
            p["_contract"] = contracts[p["id"]]

    # Tier distribution
    stats["tiers"] = {"tier_1": 0, "tier_2": 0, "tier_3": 0}
    for p in problems:
        tier = p.get("tier", "tier_3")
        if tier in stats["tiers"]:
            stats["tiers"][tier] += 1

    # Compute recently added and recently solved lists (by last_reviewed_at)
    problems_with_date = [
        p for p in problems if p.get("status", {}).get("last_reviewed_at")
    ]
    recently_added = sorted(
        problems_with_date,
        key=lambda p: p["status"]["last_reviewed_at"],
        reverse=True,
    )
    recently_solved = sorted(
        [p for p in problems_with_date if p.get("status", {}).get("label") == "solved"],
        key=lambda p: p["status"]["last_reviewed_at"],
        reverse=True,
    )

    # Build graph data
    graph_data = build_graph_data(problems, problems_by_id)

    # Setup Jinja2
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)), autoescape=True, undefined=ChainableUndefined)

    # Prepare output
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True)

    # Copy static files
    if STATIC_DIR.exists():
        shutil.copytree(STATIC_DIR, OUTPUT_DIR / "static")

    # Build index page
    template = env.get_template("index.html")
    (OUTPUT_DIR / "index.html").write_text(template.render(
        stats=stats,
        problems=problems,
        collections=collections,
        recently_added=recently_added,
        recently_solved=recently_solved,
    ))

    # Build problems explorer page
    template = env.get_template("problems.html")
    (OUTPUT_DIR / "problems.html").write_text(template.render(
        problems=problems,
        stats=stats,
    ))

    # Build individual problem pages
    problems_out = OUTPUT_DIR / "problem"
    problems_out.mkdir()
    template = env.get_template("problem_detail.html")
    for problem in problems:
        slug = problem["id"].replace(".", "-")
        page = template.render(problem=problem, attempts=[
            a for a in attempts if a.get("problem_id") == problem["id"]
        ])
        (problems_out / f"{slug}.html").write_text(page)

    # Build collections page
    template = env.get_template("collections.html")
    (OUTPUT_DIR / "collections.html").write_text(template.render(
        collections=collections,
        problems_by_id=problems_by_id,
    ))

    # Compute hot sources (sources producing the most leads)
    source_counts: dict[str, int] = {}
    for lead in leads:
        src = lead.get("source", "unknown")
        source_counts[src] = source_counts.get(src, 0) + 1
    hot_sources = sorted(
        [{"name": k, "count": v} for k, v in source_counts.items()],
        key=lambda x: x["count"],
        reverse=True,
    )

    # Recently promoted: problems with review_state == human_verified sorted by date
    recently_promoted = sorted(
        [p for p in problems if p.get("status", {}).get("review_state") == "human_verified"],
        key=lambda p: p.get("status", {}).get("last_reviewed_at", ""),
        reverse=True,
    )[:5]

    # Build radar page
    template = env.get_template("radar.html")
    (OUTPUT_DIR / "radar.html").write_text(template.render(
        leads=leads,
        hot_sources=hot_sources,
        recently_promoted=recently_promoted,
    ))

    # Build attempts page
    template = env.get_template("attempts.html")
    (OUTPUT_DIR / "attempts.html").write_text(template.render(
        attempts=attempts,
    ))

    # Build leaderboard
    systems = {}
    for att in attempts:
        model = att.get("model", att.get("actor", "Unknown"))
        if isinstance(model, dict):
            model = model.get("name", att.get("actor", "Unknown"))
        if model not in systems:
            systems[model] = {"system": model, "attempts": 0, "partial": 0, "verified": 0, "best_result": None, "best_problem_slug": ""}
        systems[model]["attempts"] += 1
        outcome = att.get("outcome", {})
        result_type = outcome.get("result_type", "") if isinstance(outcome, dict) else ""
        if result_type == "partial":
            systems[model]["partial"] += 1
        if att.get("verification_status") == "verified":
            systems[model]["verified"] += 1
        if result_type in ("proof", "partial") and not systems[model]["best_result"]:
            systems[model]["best_result"] = result_type
            systems[model]["best_problem_slug"] = att.get("problem_id", "").replace(".", "-")

    leaderboard = sorted(systems.values(), key=lambda x: (x["verified"], x["partial"], x["attempts"]), reverse=True)
    leaderboard_stats = {
        "total_attempts": len(attempts),
        "unique_models": len(systems),
        "problems_attempted": len(set(a.get("problem_id", "") for a in attempts)),
        "verified_results": sum(1 for a in attempts if a.get("verification_status") == "verified"),
    }

    template = env.get_template("leaderboard.html")
    (OUTPUT_DIR / "leaderboard.html").write_text(template.render(
        leaderboard=leaderboard,
        leaderboard_stats=leaderboard_stats,
        recent_attempts=attempts,
    ))

    # Build graph page
    template = env.get_template("graph.html")
    (OUTPUT_DIR / "graph.html").write_text(template.render(
        graph_data=graph_data,
    ))

    # Build JSON API
    api_dir = OUTPUT_DIR / "api"
    api_dir.mkdir()
    with open(api_dir / "problems.json", "w") as f:
        json.dump(problems, f, indent=2, ensure_ascii=False)
    with open(api_dir / "collections.json", "w") as f:
        json.dump(collections, f, indent=2, ensure_ascii=False)
    with open(api_dir / "stats.json", "w") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    with open(api_dir / "leads.json", "w") as f:
        json.dump(leads, f, indent=2, ensure_ascii=False)
    with open(api_dir / "attempts.json", "w") as f:
        json.dump(attempts, f, indent=2, ensure_ascii=False)

    print(f"Site built: {len(problems)} problems, {len(collections)} collections, "
          f"{len(leads)} leads, {len(attempts)} attempts")
    print(f"Output: {OUTPUT_DIR}")


if __name__ == "__main__":
    build()
