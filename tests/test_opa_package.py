"""Test the opa Python package API."""


def test_import():
    from opa import atlas
    assert hasattr(atlas, "load")
    assert hasattr(atlas, "get")
    assert hasattr(atlas, "list_domains")


def test_load_all():
    from opa import atlas
    atlas._load_all.cache_clear()
    problems = atlas.load()
    assert len(problems) > 200
    assert all("id" in p for p in problems)


def test_load_filtered():
    from opa import atlas
    math = atlas.load(domain="mathematics")
    assert len(math) > 50
    assert all(p["domain"] == "mathematics" for p in math)


def test_load_by_status():
    from opa import atlas
    open_problems = atlas.load(status="open")
    assert len(open_problems) > 100


def test_get_by_id():
    from opa import atlas
    p = atlas.get("opa.mathematics.number-theory.collatz-conjecture")
    assert p is not None
    assert p["title"] == "Collatz Conjecture"


def test_get_nonexistent():
    from opa import atlas
    p = atlas.get("opa.fake.nonexistent")
    assert p is None


def test_list_domains():
    from opa import atlas
    domains = atlas.list_domains()
    assert "mathematics" in domains
    assert "theoretical-cs" in domains


def test_list_subdomains():
    from opa import atlas
    subs = atlas.list_subdomains(domain="mathematics")
    assert "number-theory" in subs


def test_search():
    from opa import atlas
    results = atlas.search("Collatz")
    assert len(results) >= 1
    assert any("Collatz" in p["title"] for p in results)


def test_stats():
    from opa import atlas
    s = atlas.stats()
    assert s["total"] > 200
    assert "domains" in s
    assert "tiers" in s
    assert "statuses" in s
