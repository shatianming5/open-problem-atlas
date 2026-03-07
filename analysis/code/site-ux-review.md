---
analyzer: codex/gpt-5.4
reasoning: xhigh
date: 2026-03-07
task: site UX review
scope: site/
---

# OpenProblemAtlas site UX review

## Method

I read all requested source files:

- `site/app/templates/base.html`
- `site/app/templates/index.html`
- `site/app/templates/problems.html`
- `site/app/templates/problem_detail.html`
- `site/app/templates/radar.html`
- `site/app/templates/attempts.html`
- `site/app/templates/collections.html`
- `site/app/templates/graph.html`
- `site/app/static/css/style.css`
- `site/app/static/js/explorer.js`
- `site/app/static/js/graph.js`
- `site/build/build.py`

I also inspected the generated output in `site/build/output/` on desktop and mobile widths.

Reference inputs used for comparison:

- [Erdos Problems](https://erdosproblems.com/)
- [Open Problem Garden](http://openproblemgarden.org/) and a mirror summary when the canonical site was unstable during review: [wiki mirror](https://wiki.riteme.site/wiki/Open_Problem_Garden)
- [Awesome on GitHub](https://github.com/sindresorhus/awesome)

## Executive summary

OpenProblemAtlas already has the hard part: a rich data model, a static build that works, and enough structured content to support a very strong product. The current site is not bad. It is consistent, readable, and clearly built by engineers who care about the data.

The problem is that it still looks and behaves like an internal dashboard, not like a flagship open-source knowledge product. The visual system is too close to generic GitHub dark mode, the home page does not create enough excitement or trust, the explorer is functional but shallow, the problem detail page is rich but exhausting, and the graph page is currently the weakest part of the site by a wide margin.

If this launched on GitHub today, people would likely respect the dataset but not star the site for its UX. The site needs a stronger editorial point of view, better interaction design, and one or two truly polished surfaces that feel intentionally designed rather than merely rendered.

## Current state assessment

| Dimension | Score (1-10) | Assessment |
| --- | --- | --- |
| Visual hierarchy and typography | 5 | Clear enough, but too many sections share the same weight. System fonts and repeated card styling make the whole site feel flat. Inline styles fragment the hierarchy further. |
| Color scheme and contrast | 6 | Contrast is mostly acceptable, but the palette is generic and over-reliant on one GitHub-like dark/blue treatment. It feels credible, not memorable. |
| Responsive design / mobile support | 4 | There is only one real breakpoint. The nav wraps instead of becoming intentional, filters eat too much vertical space, and the graph is not touch-first. |
| Navigation and information architecture | 5 | Top-level pages exist, but everything is treated as equally primary. There is no stronger "start here" path, no secondary nav, and no breadcrumbs or in-page navigation where needed. |
| Search / filter UX | 5 | Basic search and chips work, but there is no multi-select, sort, clear-all, URL state, empty filtered state, or filter summary. It works for a demo, not for serious browsing. |
| Problem detail completeness | 6 | The raw data coverage is strong. The presentation is not. The page is long, linear, and hard to scan, with tables and sections that feel like schema dumps rather than research briefs. |
| Graph visualization quality | 2 | This is the biggest problem. Labels overlap, nodes collapse into corners, there is no zoom, no search, no touch-friendly behavior, and the result looks like an unfinished demo. |
| Overall wow factor | 4 | The home page is competent, but it does not create desire. There is no memorable visual motif, no editorial curation on the first screen, and no standout interaction that makes people want to share the site. |

**Overall:** `4.6/10`

## Comparison to the references

| Reference | What it gets right | What OpenProblemAtlas should borrow |
| --- | --- | --- |
| [Erdos Problems](https://erdosproblems.com/) | Strong problem-first framing. Minimal chrome. Immediate sense that the content matters more than the UI. | Lead with iconic problems and curation, not just stats. Make the first action "enter the problems" feel irresistible. |
| [Open Problem Garden](http://openproblemgarden.org/) | Problems feel like living objects in a network: relations, links, community context, and exploratory browsing matter. | Make detail pages feel relational and alive. Titles, related problems, collections, sources, and contribution pathways should be first-class. |
| [Awesome on GitHub](https://github.com/sindresorhus/awesome) | Extremely scannable. Strong table-of-contents behavior. Concise annotations. Clear contribution trust signals. | Use concise summaries, better list structure, anchor navigation, and stronger "how to contribute" affordances. |

## What is working today

- The data model is much better than the current presentation. `problem_detail.html` exposes statements, sources, relations, scores, formalization, AI readiness, and attempts.
- The build is simple and reliable. `site/build/build.py` cleanly turns YAML into HTML and JSON.
- The site has consistent card and tag patterns, which means a better design system can be layered on without rethinking the entire architecture.
- Search/filter logic exists already, so the next step is refinement rather than starting from zero.

## What is holding the site back

- `style.css` uses a safe, GitHub-dark-adjacent palette with a system font stack. It reads as "developer default" instead of "curated open-source product."
- There is heavy inline styling in templates, which makes polish drift page by page.
- `base.html` has no intentional mobile nav, no skip link, no stronger shell, and no persistent trust signal.
- `problems.html` plus `explorer.js` provides only the minimum viable explorer.
- `problem_detail.html` is rich but not editorialized; it needs an "at a glance" layer and titled relation context, not just schema sections.
- `graph.js` draws every label, has no camera model, and produces a network that is difficult to use at the current data scale.
- `attempts.html` and `radar.html` repeat inline filtering logic instead of sharing a reusable interaction pattern.

## Top 10 specific improvements

| Priority | Improvement | Why it matters | Primary files |
| --- | --- | --- | --- |
| P0 | Create a distinctive site shell and landing experience | First impressions decide whether the project feels star-worthy or merely functional. | `base.html`, `index.html`, `style.css` |
| P0 | Turn Problems into a real explorer | The problems index is the core product surface and currently feels too shallow for 300+ entries. | `problems.html`, `explorer.js`, `style.css` |
| P0 | Rebuild problem detail as a research brief | The detail page has the data to be great, but it needs scan structure and relational context. | `problem_detail.html`, `build.py`, `style.css` |
| P0 | Replace the graph demo with a usable network explorer | The current graph is the least polished page and damages perceived quality. | `graph.html`, `graph.js`, `style.css` |
| P1 | Unify radar and attempts with the same explorer pattern | Those pages should feel like siblings of Problems, not separate one-off UIs. | `radar.html`, `attempts.html`, shared JS/CSS |
| P1 | Upgrade the typography and spacing system | Better fonts, tighter rhythm, and fewer inline styles will raise every page at once. | `base.html`, `style.css`, all templates |
| P1 | Add trust and contribution signals | Good open-source products show freshness, governance, and contribution paths immediately. | `index.html`, `base.html`, build metadata |
| P1 | Add math-first content rendering and citation polish | A math problem site should handle formulas, references, and statements with more authority. | `problem_detail.html`, `base.html`, content pipeline |
| P2 | Curate collections, radar, and attempts more aggressively | These pages need "why should I care" framing, not only raw lists. | `collections.html`, `radar.html`, `attempts.html` |
| P2 | Add subtle motion and richer social presentation | A bit of motion, stronger OG cards, and better empty states will make the site feel more alive and shareable. | `style.css`, templates, build output metadata |

## P0 implementation details with code

The snippets below are the minimum viable code changes I would make first. They are intentionally practical and constrained to the current stack.

### P0.1 Build a distinct site shell and landing experience

**Before**

- The site shell is a simple header + footer with no distinctive identity.
- Mobile nav just wraps.
- The home page starts with stats, which is useful but not emotionally strong.

**After**

- The shell feels like a product, not a prototype.
- The home page leads with a clear thesis, strong calls to action, and immediate trust signals.
- The first screen sells the atlas, not just the count of items in it.

**Code changes**

`site/app/templates/base.html`

```html
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{% block title %}OpenProblemAtlas{% endblock %}</title>
  <meta name="description" content="A living, machine-readable atlas of open problems for researchers, AI agents, and theorem provers.">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Sora:wght@600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/static/css/style.css">
  {% block head %}{% endblock %}
</head>
<body class="page-{{ page | default('home') }}">
  <a class="skip-link" href="#main-content">Skip to content</a>

  <div class="site-banner">
    <div class="container">
      Open data for frontier mathematics and theorem proving
    </div>
  </div>

  <header class="site-header">
    <div class="container site-header__inner">
      <a href="/" class="logo">
        <span class="logo-mark" aria-hidden="true"></span>
        <span>OpenProblemAtlas</span>
      </a>

      <button
        class="nav-toggle"
        type="button"
        aria-expanded="false"
        aria-controls="site-nav">
        Menu
      </button>

      <nav id="site-nav" class="site-nav" aria-label="Primary">
        <a href="/problems.html" {% if page == 'problems' %}class="active"{% endif %}>Problems</a>
        <a href="/collections.html" {% if page == 'collections' %}class="active"{% endif %}>Collections</a>
        <a href="/radar.html" {% if page == 'radar' %}class="active"{% endif %}>Radar</a>
        <a href="/attempts.html" {% if page == 'attempts' %}class="active"{% endif %}>Attempts</a>
        <a href="/graph.html" {% if page == 'graph' %}class="active"{% endif %}>Graph</a>
      </nav>

      <a
        class="button button--ghost header-cta"
        href="https://github.com/OpenProblemAtlas/open-problem-atlas"
        target="_blank"
        rel="noreferrer">
        GitHub
      </a>
    </div>
  </header>

  <main id="main-content">
    {% block content %}{% endblock %}
  </main>

  <footer class="site-footer">
    <div class="container site-footer__inner">
      <div>
        <strong>OpenProblemAtlas</strong>
        <p>Data: CC BY-SA 4.0. Code: MIT.</p>
      </div>
      <div class="footer-links">
        <a href="/api/problems.json">API</a>
        <a href="https://github.com/OpenProblemAtlas/open-problem-atlas/blob/main/CONTRIBUTING.md">Contribute</a>
      </div>
    </div>
  </footer>

  <script>
    document.addEventListener('DOMContentLoaded', () => {
      const toggle = document.querySelector('.nav-toggle');
      const nav = document.getElementById('site-nav');
      if (!toggle || !nav) return;

      toggle.addEventListener('click', () => {
        const open = nav.classList.toggle('is-open');
        toggle.setAttribute('aria-expanded', String(open));
      });
    });
  </script>

  {% block scripts %}{% endblock %}
</body>
```

`site/app/templates/index.html`

```html
{% extends "base.html" %}
{% set page = 'home' %}

{% block content %}
<div class="container">
  <section class="home-hero">
    <div class="hero-copy">
      <p class="eyebrow">Open data for unsolved mathematics</p>
      <h1>Browse open problems the way researchers browse literature.</h1>
      <p class="hero-lede">
        OpenProblemAtlas turns conjectures, relations, sources, formalization status,
        and AI or human attempts into a navigable research surface.
      </p>

      <div class="hero-actions">
        <a href="/problems.html" class="button button--primary">Explore problems</a>
        <a href="/collections.html" class="button button--ghost">View collections</a>
      </div>

      <ul class="hero-proof">
        <li><strong>{{ stats.total_problems }}</strong><span>reviewed problems</span></li>
        <li><strong>{{ stats.total_collections }}</strong><span>curated collections</span></li>
        <li><strong>{{ stats.total_attempts }}</strong><span>recorded attempts</span></li>
      </ul>
    </div>

    <aside class="hero-panel">
      {% set featured = recently_added[0] if recently_added else problems[0] %}
      <p class="hero-panel__label">Featured problem</p>
      <a class="feature-spotlight" href="/problem/{{ featured.id | replace('.', '-') }}.html">
        <h2>{{ featured.title }}</h2>
        <p>{{ featured.statement.informal[:220] }}{% if featured.statement.informal | length > 220 %}...{% endif %}</p>
        <div class="meta">
          <span class="tag tag-open">{{ featured.status.label }}</span>
          <span class="tag tag-domain">{{ featured.domain | replace('-', ' ') }}</span>
        </div>
      </a>
    </aside>
  </section>

  <section class="trust-strip">
    <div class="trust-item">
      <span class="trust-label">Structured data</span>
      <strong>Problems, sources, relations, attempts</strong>
    </div>
    <div class="trust-item">
      <span class="trust-label">Open source</span>
      <strong>Community-editable on GitHub</strong>
    </div>
    <div class="trust-item">
      <span class="trust-label">Research ready</span>
      <strong>Designed for humans and agents</strong>
    </div>
  </section>

  <section class="section-heading">
    <div>
      <p class="eyebrow">Start here</p>
      <h2>High-signal entry points</h2>
    </div>
  </section>

  <div class="feature-grid">
    <a class="feature-card" href="/problems.html">
      <h3>Problem explorer</h3>
      <p>Search by title, statement, domain, status, and solver-readiness.</p>
    </a>
    <a class="feature-card" href="/collections.html">
      <h3>Curated collections</h3>
      <p>Browse famous clusters like formalization targets or classic graph theory problems.</p>
    </a>
    <a class="feature-card" href="/radar.html">
      <h3>Radar</h3>
      <p>Track leads mined from the literature before they are promoted to verified problems.</p>
    </a>
  </div>

  <!-- Keep the existing stats, featured collections, and recency sections below this point. -->
</div>
{% endblock %}
```

`site/app/static/css/style.css`

```css
:root {
  --bg: #08111d;
  --bg-card: rgba(13, 24, 40, 0.84);
  --bg-hover: #13253d;
  --border: rgba(148, 163, 184, 0.18);
  --text: #ecf3ff;
  --text-muted: #9bb0c7;
  --accent: #7dd3fc;
  --accent-hover: #bae6fd;
  --green: #22c55e;
  --yellow: #f59e0b;
  --red: #ef4444;
  --purple: #a78bfa;
  --radius: 18px;
  --shadow-lg: 0 24px 80px rgba(2, 8, 23, 0.42);
  --font-sans: "Manrope", sans-serif;
  --font-display: "Sora", sans-serif;
  --font-mono: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
}

body {
  font-family: var(--font-sans);
  background:
    radial-gradient(circle at top left, rgba(125, 211, 252, 0.10), transparent 24rem),
    radial-gradient(circle at top right, rgba(167, 139, 250, 0.08), transparent 24rem),
    linear-gradient(180deg, #08111d 0%, #050b13 100%);
  color: var(--text);
}

.skip-link {
  position: absolute;
  left: -9999px;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

.skip-link:focus {
  left: 16px;
  top: 16px;
  z-index: 100;
  padding: 10px 14px;
  border-radius: 999px;
  background: var(--accent);
  color: #08111d;
}

.site-banner {
  border-bottom: 1px solid var(--border);
  background: rgba(5, 11, 19, 0.9);
  color: var(--text-muted);
  font-size: 13px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.site-banner .container {
  padding-top: 10px;
  padding-bottom: 10px;
}

.site-header {
  position: sticky;
  top: 0;
  z-index: 50;
  backdrop-filter: blur(18px);
  background: rgba(8, 17, 29, 0.78);
  border-bottom: 1px solid var(--border);
}

.site-header__inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  min-height: 76px;
}

.logo {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  color: var(--text);
  font-family: var(--font-display);
  font-size: 20px;
  font-weight: 700;
}

.logo-mark {
  width: 12px;
  height: 12px;
  border-radius: 999px;
  background: linear-gradient(135deg, var(--accent), var(--purple));
  box-shadow: 0 0 0 6px rgba(125, 211, 252, 0.10);
}

.site-nav {
  display: flex;
  gap: 18px;
  align-items: center;
}

.site-nav a {
  margin-left: 0;
  padding: 10px 12px;
  border-radius: 999px;
  color: var(--text-muted);
}

.site-nav a.active,
.site-nav a:hover {
  color: var(--text);
  background: rgba(125, 211, 252, 0.08);
  text-decoration: none;
}

.nav-toggle {
  display: none;
}

.button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 44px;
  padding: 0 18px;
  border-radius: 999px;
  border: 1px solid var(--border);
  font-weight: 700;
  text-decoration: none;
}

.button--primary {
  background: linear-gradient(135deg, #38bdf8, #7c3aed);
  border-color: transparent;
  color: #fff;
}

.button--ghost {
  background: rgba(255, 255, 255, 0.02);
  color: var(--text);
}

.home-hero {
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(300px, 420px);
  gap: 28px;
  align-items: stretch;
  padding: 56px 0 28px;
}

.eyebrow {
  margin-bottom: 14px;
  color: var(--accent);
  font-size: 13px;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.hero-copy h1 {
  margin-bottom: 18px;
  font-family: var(--font-display);
  font-size: clamp(2.6rem, 5vw, 4.6rem);
  line-height: 0.98;
}

.hero-lede {
  max-width: 62ch;
  margin-bottom: 22px;
  color: var(--text-muted);
  font-size: 19px;
  line-height: 1.7;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 26px;
}

.hero-proof {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  list-style: none;
}

.hero-proof li,
.hero-panel,
.trust-strip,
.feature-card {
  border: 1px solid var(--border);
  background: var(--bg-card);
  box-shadow: var(--shadow-lg);
}

.hero-proof li {
  min-width: 144px;
  padding: 16px 18px;
  border-radius: var(--radius);
}

.hero-proof strong {
  display: block;
  font-size: 24px;
}

.hero-proof span {
  color: var(--text-muted);
  font-size: 14px;
}

.hero-panel {
  padding: 22px;
  border-radius: 24px;
}

.hero-panel__label {
  margin-bottom: 10px;
  color: var(--text-muted);
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.feature-spotlight h2 {
  margin-bottom: 10px;
  font-size: 28px;
}

.feature-spotlight p {
  margin-bottom: 16px;
  color: var(--text-muted);
}

.trust-strip {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin: 18px 0 42px;
  padding: 18px;
  border-radius: 24px;
}

.trust-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.trust-label {
  color: var(--text-muted);
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
  margin-bottom: 40px;
}

.section-heading {
  margin: 24px 0 16px;
}

.feature-card {
  padding: 22px;
  border-radius: 22px;
}

.feature-card h3 {
  margin-bottom: 8px;
  font-size: 20px;
}

.feature-card p {
  color: var(--text-muted);
}

.site-footer__inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.footer-links {
  display: flex;
  gap: 16px;
}

@media (max-width: 960px) {
  .site-header__inner {
    min-height: auto;
    padding-top: 14px;
    padding-bottom: 14px;
    flex-wrap: wrap;
  }

  .nav-toggle {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-height: 40px;
    padding: 0 14px;
    border: 1px solid var(--border);
    border-radius: 999px;
    background: transparent;
    color: var(--text);
  }

  .site-nav {
    display: none;
    width: 100%;
    flex-direction: column;
    align-items: stretch;
    padding-top: 8px;
  }

  .site-nav.is-open {
    display: flex;
  }

  .header-cta {
    margin-left: auto;
  }

  .home-hero,
  .trust-strip,
  .feature-grid {
    grid-template-columns: 1fr;
  }

  .site-footer__inner {
    flex-direction: column;
    align-items: flex-start;
  }
}
```

### P0.2 Turn Problems into a real explorer

**Before**

- Search and single-select chips work, but they feel like a basic demo.
- No sort, no clear-all, no URL state, no filter summary, and no empty filtered state.
- On mobile, the filter area becomes tall but not better.

**After**

- The explorer feels intentional and fast.
- Filters are multi-select, restorable from the URL, and obvious to undo.
- Users can search, sort, and understand why they are seeing the current results.

**Code changes**

`site/app/templates/problems.html`

```html
<div class="container explorer-page">
  <div class="page-intro">
    <p class="eyebrow">Core surface</p>
    <h1>Problem explorer</h1>
    <p class="page-copy">Search by title, aliases, statement, domain, status, and machine-readiness signals.</p>
  </div>

  <div class="explorer-toolbar">
    <label class="search-shell">
      <span class="sr-only">Search problems</span>
      <input type="search" id="search-input" placeholder="Search title, aliases, statement, subdomain...">
    </label>

    <select id="sort-select" class="sort-select" aria-label="Sort problems">
      <option value="reviewed">Recently reviewed</option>
      <option value="impact">Highest impact</option>
      <option value="title">Title A-Z</option>
    </select>

    <button id="clear-filters" class="button button--ghost" type="button">Clear all</button>
  </div>

  <div id="active-filter-pills" class="active-pills" hidden></div>

  <div class="filters filters--framed">
    <span class="filter-label">Domain</span>
    <button class="filter-btn" data-filter-key="domain" data-filter-value="mathematics">Mathematics</button>
    <button class="filter-btn" data-filter-key="domain" data-filter-value="theoretical-cs">Theoretical CS</button>
    <button class="filter-btn" data-filter-key="domain" data-filter-value="mathematical-physics">Math Physics</button>
  </div>

  <div class="filters filters--framed">
    <span class="filter-label">Status</span>
    <button class="filter-btn" data-filter-key="status" data-filter-value="open">Open</button>
    <button class="filter-btn" data-filter-key="status" data-filter-value="solved">Solved</button>
    <button class="filter-btn" data-filter-key="status" data-filter-value="partially_solved">Partial</button>
  </div>

  <div class="filters filters--framed">
    <span class="filter-label">Type</span>
    <button class="filter-btn" data-filter-key="type" data-filter-value="conjecture">Conjecture</button>
    <button class="filter-btn" data-filter-key="type" data-filter-value="open_question">Open question</button>
    <button class="filter-btn" data-filter-key="type" data-filter-value="existence">Existence</button>
    <button class="filter-btn" data-filter-key="type" data-filter-value="computation">Computation</button>
  </div>

  <div class="filters filters--framed">
    <span class="filter-label">Special</span>
    <button class="filter-btn" data-filter-key="special" data-filter-value="underexplored">Underexplored</button>
    <button class="filter-btn" data-filter-key="special" data-filter-value="formalizable">Formalizable</button>
    <button class="filter-btn" data-filter-key="special" data-filter-value="solver-ready">Solver-ready</button>
  </div>

  <div class="explorer-meta">
    <p><span id="result-count">{{ problems | length }} problems</span></p>
  </div>

  <div id="empty-state" class="empty-state" hidden>
    <h2>No problems match the current filters</h2>
    <p>Clear one or more filters, or broaden the search terms.</p>
  </div>

  <div class="problem-list" id="problem-list">
    {% for p in problems %}
    <a href="/problem/{{ p.id | replace('.', '-') }}.html" class="problem-link">
      <article
        class="problem-card"
        data-title="{{ p.title }}"
        data-domain="{{ p.domain }}"
        data-status="{{ p.status.label }}"
        data-type="{{ p.problem_type | default('') }}"
        data-statement="{{ p.statement.canonical[:260] | default('') }}"
        data-aliases="{{ p.aliases | join(' ') if p.aliases else '' }}"
        data-subdomains="{{ p.subdomains | join(' ') if p.subdomains else '' }}"
        data-reviewed="{{ p.status.last_reviewed_at | default('') }}"
        data-score-underexplored="{{ p.scores.underexplored | default(0) }}"
        data-score-impact="{{ p.scores.impact | default(0) }}"
        data-formalization-wanted="{{ p.formalization.wanted | default(false) }}"
        data-formalization-available="{{ p.formalization.available | default(false) }}"
        data-solver-ready="{{ p.ai.solver_ready | default(false) if p.ai else false }}">
        <div class="title">{{ p.title }}</div>
        <div class="meta">
          <span class="tag {% if p.status.label == 'open' %}tag-open{% elif p.status.label == 'solved' %}tag-solved{% endif %}">
            {{ p.status.label }}
          </span>
          <span class="tag tag-domain">{{ p.domain | replace('-', ' ') }}</span>
          {% if p.problem_type %}
          <span class="tag tag-type">{{ p.problem_type | replace('_', ' ') }}</span>
          {% endif %}
          {% if p.status.last_reviewed_at %}
          <span>{{ p.status.last_reviewed_at }}</span>
          {% endif %}
        </div>
        {% if p.statement.informal %}
        <div class="statement">{{ p.statement.informal[:220] }}{% if p.statement.informal | length > 220 %}...{% endif %}</div>
        {% endif %}
      </article>
    </a>
    {% endfor %}
  </div>
</div>
```

`site/app/static/js/explorer.js`

```js
document.addEventListener('DOMContentLoaded', () => {
  const searchInput = document.getElementById('search-input');
  const sortSelect = document.getElementById('sort-select');
  const clearButton = document.getElementById('clear-filters');
  const filterButtons = Array.from(document.querySelectorAll('.filter-btn'));
  const problemList = document.getElementById('problem-list');
  const problemCards = Array.from(document.querySelectorAll('.problem-card'));
  const resultCount = document.getElementById('result-count');
  const activePills = document.getElementById('active-filter-pills');
  const emptyState = document.getElementById('empty-state');

  const state = {
    query: '',
    sort: 'reviewed',
    filters: {
      domain: new Set(),
      status: new Set(),
      type: new Set(),
      special: new Set(),
    },
  };

  hydrateFromUrl();
  wireEvents();
  applyFilters();

  function wireEvents() {
    if (searchInput) {
      searchInput.addEventListener('input', (event) => {
        state.query = event.target.value.toLowerCase().trim();
        applyFilters();
      });
    }

    if (sortSelect) {
      sortSelect.addEventListener('change', (event) => {
        state.sort = event.target.value;
        applyFilters();
      });
    }

    if (clearButton) {
      clearButton.addEventListener('click', () => {
        Object.values(state.filters).forEach((bucket) => bucket.clear());
        state.query = '';
        state.sort = 'reviewed';
        if (searchInput) searchInput.value = '';
        if (sortSelect) sortSelect.value = 'reviewed';
        filterButtons.forEach((button) => button.classList.remove('active'));
        applyFilters();
      });
    }

    filterButtons.forEach((button) => {
      button.addEventListener('click', () => {
        const key = button.dataset.filterKey;
        const value = button.dataset.filterValue;
        const bucket = state.filters[key];
        if (!bucket) return;

        if (bucket.has(value)) {
          bucket.delete(value);
          button.classList.remove('active');
        } else {
          bucket.add(value);
          button.classList.add('active');
        }

        applyFilters();
      });
    });
  }

  function hydrateFromUrl() {
    const params = new URLSearchParams(window.location.search);
    state.query = (params.get('q') || '').toLowerCase().trim();
    state.sort = params.get('sort') || 'reviewed';

    if (searchInput) searchInput.value = params.get('q') || '';
    if (sortSelect) sortSelect.value = state.sort;

    ['domain', 'status', 'type', 'special'].forEach((key) => {
      const raw = params.get(key);
      if (!raw) return;
      raw.split(',').filter(Boolean).forEach((value) => state.filters[key].add(value));
    });

    filterButtons.forEach((button) => {
      const key = button.dataset.filterKey;
      const value = button.dataset.filterValue;
      if (state.filters[key] && state.filters[key].has(value)) {
        button.classList.add('active');
      }
    });
  }

  function syncUrl() {
    const params = new URLSearchParams();
    if (state.query) params.set('q', state.query);
    if (state.sort && state.sort !== 'reviewed') params.set('sort', state.sort);

    Object.entries(state.filters).forEach(([key, bucket]) => {
      if (bucket.size) params.set(key, Array.from(bucket).join(','));
    });

    const next = params.toString() ? `${window.location.pathname}?${params.toString()}` : window.location.pathname;
    window.history.replaceState(null, '', next);
  }

  function matchesSearch(card) {
    if (!state.query) return true;
    const haystack = [
      card.dataset.title,
      card.dataset.statement,
      card.dataset.aliases,
      card.dataset.subdomains,
    ].join(' ').toLowerCase();
    return haystack.includes(state.query);
  }

  function matchesBucket(card, key) {
    const bucket = state.filters[key];
    if (!bucket || bucket.size === 0) return true;

    if (key === 'special') {
      return Array.from(bucket).every((value) => matchesSpecial(card, value));
    }

    const datasetKey = key === 'type' ? 'type' : key;
    return bucket.has(card.dataset[datasetKey] || '');
  }

  function matchesSpecial(card, filterValue) {
    if (filterValue === 'underexplored') {
      return (parseFloat(card.dataset.scoreUnderexplored) || 0) > 0.3 &&
             (parseFloat(card.dataset.scoreImpact) || 0) > 0.5;
    }

    if (filterValue === 'formalizable') {
      return card.dataset.formalizationWanted === 'True' ||
             card.dataset.formalizationAvailable === 'True';
    }

    if (filterValue === 'solver-ready') {
      return card.dataset.solverReady === 'True';
    }

    return true;
  }

  function sortVisibleCards(cards) {
    const sorted = [...cards];
    sorted.sort((left, right) => {
      if (state.sort === 'title') {
        return (left.dataset.title || '').localeCompare(right.dataset.title || '');
      }

      if (state.sort === 'impact') {
        return (parseFloat(right.dataset.scoreImpact) || 0) - (parseFloat(left.dataset.scoreImpact) || 0);
      }

      return (right.dataset.reviewed || '').localeCompare(left.dataset.reviewed || '');
    });

    sorted.forEach((card) => problemList.appendChild(card.parentElement));
  }

  function renderActivePills() {
    const entries = [];
    Object.entries(state.filters).forEach(([key, bucket]) => {
      bucket.forEach((value) => entries.push({ key, value }));
    });

    if (!entries.length && !state.query) {
      activePills.hidden = true;
      activePills.innerHTML = '';
      return;
    }

    activePills.hidden = false;
    activePills.innerHTML = entries.map(({ key, value }) => (
      `<button class="active-pill" data-pill-key="${key}" data-pill-value="${value}" type="button">${key}: ${value}</button>`
    )).join('');

    activePills.querySelectorAll('.active-pill').forEach((pill) => {
      pill.addEventListener('click', () => {
        state.filters[pill.dataset.pillKey].delete(pill.dataset.pillValue);
        filterButtons.forEach((button) => {
          if (
            button.dataset.filterKey === pill.dataset.pillKey &&
            button.dataset.filterValue === pill.dataset.pillValue
          ) {
            button.classList.remove('active');
          }
        });
        applyFilters();
      });
    });
  }

  function applyFilters() {
    const visible = [];

    problemCards.forEach((card) => {
      const show =
        matchesSearch(card) &&
        matchesBucket(card, 'domain') &&
        matchesBucket(card, 'status') &&
        matchesBucket(card, 'type') &&
        matchesBucket(card, 'special');

      card.parentElement.hidden = !show;
      if (show) visible.push(card);
    });

    sortVisibleCards(visible);
    renderActivePills();
    syncUrl();

    if (resultCount) resultCount.textContent = `${visible.length} problem${visible.length !== 1 ? 's' : ''}`;
    if (emptyState) emptyState.hidden = visible.length !== 0;
  }
});
```

`site/app/static/css/style.css`

```css
.explorer-page {
  padding-top: 36px;
}

.page-intro {
  margin-bottom: 18px;
}

.page-intro h1 {
  margin-bottom: 8px;
  font-family: var(--font-display);
  font-size: clamp(2rem, 5vw, 3rem);
}

.page-copy {
  color: var(--text-muted);
  max-width: 68ch;
}

.explorer-toolbar {
  position: sticky;
  top: 92px;
  z-index: 20;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 180px auto;
  gap: 12px;
  margin: 24px 0 14px;
  padding: 14px;
  border: 1px solid var(--border);
  border-radius: 22px;
  background: rgba(8, 17, 29, 0.92);
  backdrop-filter: blur(18px);
}

.search-shell {
  display: block;
}

.search-shell input,
.sort-select {
  width: 100%;
  min-height: 48px;
  padding: 0 16px;
  border: 1px solid var(--border);
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.02);
  color: var(--text);
}

.filters--framed {
  padding: 12px 14px;
  border: 1px solid var(--border);
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.02);
}

.filter-label {
  margin-right: 10px;
  color: var(--text-muted);
  font-size: 13px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.active-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 14px;
}

.active-pill {
  padding: 7px 12px;
  border: 1px solid var(--border);
  border-radius: 999px;
  background: rgba(125, 211, 252, 0.08);
  color: var(--text);
}

.problem-link {
  color: inherit;
  text-decoration: none;
}

.empty-state {
  margin: 20px 0;
  padding: 28px;
  border: 1px dashed var(--border);
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.02);
}

@media (max-width: 960px) {
  .explorer-toolbar {
    grid-template-columns: 1fr;
    top: 72px;
  }
}
```

### P0.3 Rebuild problem detail as a research brief

**Before**

- The page is one long stack of sections.
- Relations show IDs more often than meaningful context.
- The best information is there, but it is not organized around reader intent.

**After**

- The page opens with a crisp summary, a sticky sidebar, and section anchors.
- Related collections and relation titles make the problem feel embedded in the atlas.
- Researchers can scan first and then read deeply.

**Code changes**

`site/build/build.py`

```python
problem_to_collections: dict[str, list[dict]] = {}
for col in collections:
    for entry in col.get("problems", []):
        pid = entry.get("problem_id")
        if not pid:
            continue
        problem_to_collections.setdefault(pid, []).append({
            "title": col.get("title", "Collection"),
            "note": entry.get("note", ""),
        })

template = env.get_template("problem_detail.html")
for problem in problems:
    slug = problem["id"].replace(".", "-")
    page = template.render(
        problem=problem,
        attempts=[a for a in attempts if a.get("problem_id") == problem["id"]],
        problems_by_id=problems_by_id,
        related_collections=problem_to_collections.get(problem["id"], []),
    )
    (problems_out / f"{slug}.html").write_text(page)
```

`site/app/templates/problem_detail.html`

```html
<div class="container problem-page">
  <header class="problem-hero">
    <div class="meta">
      <span class="tag {% if problem.status.label == 'open' %}tag-open{% elif problem.status.label == 'solved' %}tag-solved{% endif %}">
        {{ problem.status.label }}
      </span>
      <span class="tag tag-domain">{{ problem.domain | replace('-', ' ') }}</span>
      {% if problem.problem_type %}
      <span class="tag tag-type">{{ problem.problem_type | replace('_', ' ') }}</span>
      {% endif %}
    </div>
    <h1>{{ problem.title }}</h1>
    {% if problem.why_it_matters %}
    <p class="problem-summary">{{ problem.why_it_matters }}</p>
    {% endif %}
  </header>

  <div class="problem-layout">
    <article class="problem-main">
      <nav class="section-nav" aria-label="Problem sections">
        <a href="#statement">Statement</a>
        <a href="#status">Status</a>
        <a href="#relations">Relations</a>
        <a href="#sources">Sources</a>
        <a href="#attempts">Attempts</a>
      </nav>

      <section id="statement" class="detail-section">
        <h2>Canonical statement</h2>
        <div class="statement-box">{{ problem.statement.canonical }}</div>
      </section>

      {% if problem.relations %}
      <section id="relations" class="detail-section">
        <h2>Relations</h2>
        <div class="relation-grid">
          {% for rel_type, ids in problem.relations.items() %}
          {% if ids %}
          <div class="relation-group">
            <h3>{{ rel_type | replace('_', ' ') | title }}</h3>
            {% for rid in ids %}
            {% set related_problem = problems_by_id.get(rid) %}
            <a href="/problem/{{ rid | replace('.', '-') }}.html" class="relation-card">
              <strong>{{ related_problem.title if related_problem else rid }}</strong>
              <span>{{ rid }}</span>
            </a>
            {% endfor %}
          </div>
          {% endif %}
          {% endfor %}
        </div>
      </section>
      {% endif %}

      {% if problem.sources %}
      <section id="sources" class="detail-section">
        <h2>Sources</h2>
        <div class="source-list">
          {% for src in problem.sources.canonical %}
          <article class="source-card">
            <strong>{{ src.title | default(src.source_id) }}</strong>
            <p class="source-meta">
              {% if src.kind %}{{ src.kind }}{% endif %}
              {% if src.year %} - {{ src.year }}{% endif %}
            </p>
            {% if src.url %}<a href="{{ src.url }}">{{ src.url }}</a>{% endif %}
          </article>
          {% endfor %}
        </div>
      </section>
      {% endif %}

      {% if attempts %}
      <section id="attempts" class="detail-section">
        <h2>Attempts</h2>
        {% for att in attempts %}
        <article class="problem-card">
          <div class="title">{{ att.actor }} ({{ att.actor_type }})</div>
          <div class="meta">
            <span>{{ att.date }}</span>
            <span class="tag {% if att.verification_status == 'verified' %}tag-open{% else %}tag-type{% endif %}">
              {{ att.verification_status }}
            </span>
          </div>
          <p>{{ att.method_summary }}</p>
        </article>
        {% endfor %}
      </section>
      {% endif %}
    </article>

    <aside class="problem-sidebar">
      <div class="sidebar-card">
        <h2>At a glance</h2>
        <dl class="facts-grid">
          <div><dt>Status</dt><dd>{{ problem.status.label }}</dd></div>
          <div><dt>Confidence</dt><dd>{{ problem.status.confidence }}</dd></div>
          <div><dt>Reviewed</dt><dd>{{ problem.status.last_reviewed_at }}</dd></div>
          <div><dt>Formalization</dt><dd>{{ 'Available' if problem.formalization and problem.formalization.available else 'Wanted' if problem.formalization and problem.formalization.wanted else 'None' }}</dd></div>
        </dl>
      </div>

      {% if related_collections %}
      <div class="sidebar-card">
        <h2>Appears in collections</h2>
        <ul class="sidebar-list">
          {% for col in related_collections %}
          <li>
            <a href="/collections.html">{{ col.title }}</a>
            {% if col.note %}<span>{{ col.note }}</span>{% endif %}
          </li>
          {% endfor %}
        </ul>
      </div>
      {% endif %}

      <div class="sidebar-card">
        <h2>Metadata</h2>
        <p><code>{{ problem.id }}</code></p>
        {% if problem.provenance and problem.provenance.schema_version %}
        <p>Schema {{ problem.provenance.schema_version }}</p>
        {% endif %}
      </div>
    </aside>
  </div>
</div>
```

`site/app/static/css/style.css`

```css
.problem-page {
  padding-top: 34px;
}

.problem-hero {
  max-width: 76ch;
  padding-bottom: 24px;
}

.problem-hero h1 {
  margin: 10px 0 14px;
  font-family: var(--font-display);
  font-size: clamp(2.2rem, 5vw, 3.8rem);
  line-height: 1.02;
}

.problem-summary {
  color: var(--text-muted);
  font-size: 18px;
  line-height: 1.7;
}

.problem-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 320px;
  gap: 30px;
  align-items: start;
}

.section-nav {
  position: sticky;
  top: 92px;
  z-index: 12;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 22px;
  padding: 12px;
  border: 1px solid var(--border);
  border-radius: 20px;
  background: rgba(8, 17, 29, 0.9);
}

.section-nav a {
  padding: 8px 12px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.03);
}

.problem-sidebar {
  position: sticky;
  top: 92px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.problem-main {
  min-width: 0;
}

.sidebar-card,
.relation-card,
.source-card {
  border: 1px solid var(--border);
  border-radius: 20px;
  background: var(--bg-card);
}

.sidebar-card {
  padding: 18px;
}

.facts-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.facts-grid dt {
  color: var(--text-muted);
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.facts-grid dd {
  margin-top: 4px;
  font-weight: 700;
}

.relation-grid {
  display: grid;
  gap: 18px;
}

.relation-group h3 {
  margin-bottom: 10px;
}

.relation-card,
.source-card {
  display: block;
  padding: 16px;
}

.relation-card span,
.source-meta,
.sidebar-list span {
  color: var(--text-muted);
  font-size: 14px;
}

.sidebar-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  list-style: none;
}

@media (max-width: 1024px) {
  .problem-layout {
    grid-template-columns: 1fr;
  }

  .problem-sidebar {
    position: static;
  }

  .section-nav {
    top: 72px;
  }
}
```

### P0.4 Replace the graph demo with a usable network explorer

**Before**

- The graph is visually noisy and mechanically weak.
- There is no zoom, no search, and too many labels.
- The current layout makes the page feel unfinished.

**After**

- Users can search, zoom, pan, reset the view, and limit labels.
- The graph becomes an exploratory tool instead of a novelty page.
- On first load it looks intentional rather than chaotic.

**Code changes**

`site/app/templates/graph.html`

```html
<div class="container graph-page">
  <div class="page-intro">
    <p class="eyebrow">Advanced surface</p>
    <h1>Relation graph</h1>
    <p class="page-copy">
      {{ graph_data.nodes | length }} problems connected by {{ graph_data.edges | length }} relations.
      Scroll to zoom, drag the background to pan, and click a node to open the problem.
    </p>
  </div>

  <div class="graph-toolbar">
    <input id="graph-search" type="search" placeholder="Find a problem or domain">

    <div class="graph-chip-row" id="graph-domain-filters">
      <button class="filter-btn active" data-domain="all">All</button>
      <button class="filter-btn" data-domain="mathematics">Mathematics</button>
      <button class="filter-btn" data-domain="theoretical-cs">Theoretical CS</button>
      <button class="filter-btn" data-domain="mathematical-physics">Math Physics</button>
    </div>

    <div class="graph-actions">
      <label for="graph-label-density">Labels</label>
      <input id="graph-label-density" type="range" min="10" max="120" value="40">
      <button id="graph-reset" class="button button--ghost" type="button">Reset view</button>
    </div>
  </div>

  <div id="graph-container">
    <canvas id="graph-canvas"></canvas>
    <div id="graph-tooltip">
      <div class="tip-title"></div>
      <div class="tip-domain"></div>
    </div>
    <div id="graph-legend">
      <div class="legend-item"><div class="legend-dot" style="background: #58a6ff;"></div><span>Mathematics</span></div>
      <div class="legend-item"><div class="legend-dot" style="background: #3fb950;"></div><span>Theoretical CS</span></div>
      <div class="legend-item"><div class="legend-dot" style="background: #d29922;"></div><span>Math Physics</span></div>
      <div class="legend-item"><div class="legend-dot" style="background: #bc8cff;"></div><span>Other</span></div>
    </div>
  </div>
</div>
```

`site/app/static/css/style.css`

```css
.graph-page {
  padding-top: 34px;
}

.graph-toolbar {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto auto;
  gap: 12px;
  align-items: center;
  margin-bottom: 16px;
}

.graph-toolbar input[type="search"] {
  min-height: 48px;
  padding: 0 16px;
  border: 1px solid var(--border);
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.02);
  color: var(--text);
}

.graph-chip-row,
.graph-actions {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
}

#graph-container {
  height: min(72vh, 860px);
  min-height: 560px;
}

@media (max-width: 960px) {
  .graph-toolbar {
    grid-template-columns: 1fr;
  }

  #graph-container {
    min-height: 460px;
  }
}
```

`site/app/static/js/graph.js`

```js
var camera = { x: 0, y: 0, scale: 1 };
var activeDomain = 'all';
var labelLimit = 40;
var panning = false;
var panStart = null;

var searchInput = document.getElementById('graph-search');
var labelDensityInput = document.getElementById('graph-label-density');
var resetButton = document.getElementById('graph-reset');
var domainButtons = Array.from(document.querySelectorAll('[data-domain]'));

function toScreen(node) {
  return {
    x: (node.x + camera.x) * camera.scale,
    y: (node.y + camera.y) * camera.scale
  };
}

function toWorld(point) {
  return {
    x: (point.x / camera.scale) - camera.x,
    y: (point.y / camera.scale) - camera.y
  };
}

function nodeVisible(node) {
  if (activeDomain !== 'all' && node.domain !== activeDomain) return false;
  if (searchInput && searchInput.value.trim()) {
    var q = searchInput.value.trim().toLowerCase();
    var haystack = [node.id, node.title, node.domain].join(' ').toLowerCase();
    return haystack.includes(q);
  }
  return true;
}

function getNodeAtScreen(mx, my) {
  for (var i = nodes.length - 1; i >= 0; i--) {
    if (!nodeVisible(nodes[i])) continue;
    var point = toScreen(nodes[i]);
    var dx = mx - point.x;
    var dy = my - point.y;
    if (dx * dx + dy * dy <= Math.pow((NODE_RADIUS + 6) * camera.scale, 2)) {
      return nodes[i];
    }
  }
  return null;
}

canvas.addEventListener('wheel', function(e) {
  e.preventDefault();
  var mouse = getMousePos(e);
  var worldBefore = toWorld(mouse);
  camera.scale = Math.max(0.45, Math.min(2.5, camera.scale * (e.deltaY < 0 ? 1.08 : 0.92)));
  camera.x = mouse.x / camera.scale - worldBefore.x;
  camera.y = mouse.y / camera.scale - worldBefore.y;
}, { passive: false });

canvas.addEventListener('mousedown', function(e) {
  var pos = getMousePos(e);
  var node = getNodeAtScreen(pos.x, pos.y);
  if (node) {
    dragging = node;
    offsetX = pos.x - toScreen(node).x;
    offsetY = pos.y - toScreen(node).y;
    return;
  }

  panning = true;
  panStart = { x: pos.x, y: pos.y, cameraX: camera.x, cameraY: camera.y };
});

function onMouseMove(e) {
  var pos = getMousePos(e);

  if (panning && panStart) {
    camera.x = panStart.cameraX + (pos.x - panStart.x) / camera.scale;
    camera.y = panStart.cameraY + (pos.y - panStart.y) / camera.scale;
    tooltip.style.display = 'none';
    return;
  }

  if (dragging) {
    var world = toWorld({ x: pos.x - offsetX, y: pos.y - offsetY });
    dragging.x = world.x;
    dragging.y = world.y;
  }

  var node = getNodeAtScreen(pos.x, pos.y);
  hovering = node;
  canvas.style.cursor = node ? 'pointer' : 'grab';

  if (node) {
    tooltip.style.display = 'block';
    tooltip.querySelector('.tip-title').textContent = node.title;
    tooltip.querySelector('.tip-domain').textContent = node.domain.replace(/-/g, ' ');
    tooltip.style.left = (pos.x + 16) + 'px';
    tooltip.style.top = (pos.y + 16) + 'px';
  } else {
    tooltip.style.display = 'none';
  }
}

function onMouseUp() {
  dragging = null;
  panning = false;
  panStart = null;
}

if (searchInput) searchInput.addEventListener('input', draw);
if (labelDensityInput) {
  labelDensityInput.addEventListener('input', function() {
    labelLimit = parseInt(this.value, 10) || 40;
  });
}
if (resetButton) {
  resetButton.addEventListener('click', function() {
    camera = { x: 0, y: 0, scale: 1 };
  });
}
domainButtons.forEach(function(button) {
  button.addEventListener('click', function() {
    domainButtons.forEach(function(other) { other.classList.remove('active'); });
    button.classList.add('active');
    activeDomain = button.dataset.domain;
  });
});

function draw() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  var visibleNodes = nodes.filter(nodeVisible);

  edges.forEach(function(e) {
    if (!nodeVisible(e.source) || !nodeVisible(e.target)) return;
    var source = toScreen(e.source);
    var target = toScreen(e.target);
    ctx.beginPath();
    ctx.strokeStyle = EDGE_COLOR;
    ctx.moveTo(source.x, source.y);
    ctx.lineTo(target.x, target.y);
    ctx.stroke();
  });

  visibleNodes.forEach(function(n) {
    var point = toScreen(n);
    var radius = n === hovering ? NODE_RADIUS + 3 : NODE_RADIUS;
    ctx.beginPath();
    ctx.arc(point.x, point.y, radius, 0, Math.PI * 2);
    ctx.fillStyle = n.color;
    ctx.fill();
  });

  visibleNodes
    .slice()
    .sort(function(a, b) {
      return (b === hovering ? 1 : 0) - (a === hovering ? 1 : 0);
    })
    .slice(0, labelLimit)
    .forEach(function(n) {
      var point = toScreen(n);
      ctx.fillStyle = 'rgba(236, 243, 255, 0.85)';
      ctx.font = LABEL_FONT;
      ctx.textAlign = 'center';
      ctx.fillText(
        n.title.length > 24 ? n.title.slice(0, 22) + '..' : n.title,
        point.x,
        point.y + NODE_RADIUS + 12
      );
    });
}
```

## Before / after summary

| Area | Before | After |
| --- | --- | --- |
| Site shell | Competent but generic dark header/footer | Distinct branded shell, intentional mobile nav, stronger trust and contribution framing |
| Home page | Stats-first, light on narrative | Thesis-first, curated, and immediately legible for new visitors |
| Problem explorer | Functional search with basic chips | Sticky, sortable, multi-select explorer with clear state and better mobile behavior |
| Problem detail | Long schema-like scroll | Scan-first research brief with sidebar context, anchors, and richer relations |
| Graph | Unusable force graph demo | Searchable, zoomable, filterable network explorer |

## Recommendations for reaching star-worthy quality

- Pick a visual identity and commit to it. Right now the site borrows too much from GitHub dark mode. A star-worthy site needs its own tone.
- Make the first screen tell a story. "Open problems for researchers, agents, and theorem provers" is strong, but it needs sharper editorial delivery and trust cues.
- Treat the explorer and detail page as the main product, and treat Radar, Attempts, and Graph as polished secondary surfaces that inherit the same design language.
- Reduce inline CSS and inline page scripts aggressively. A better design system will be much easier to maintain if styles and behavior live in reusable primitives.
- Add visible freshness signals: latest review date, problem counts by domain, contribution link, and API access should all feel first-class.
- Make relation browsing more human. Show titles, not only IDs. Show collection membership. Show why two problems are related.
- Add math-aware rendering over time. Even if the content is mostly prose today, the site will feel more authoritative once formulas and citations render beautifully.
- Do not ship the current graph as a marquee page. Either improve it to the standard above or demote it until it is genuinely useful.

## Final verdict

The project has the substance required for a very good site. The next step is not more pages. It is stronger product design on the pages that already exist.

If I had to sequence the work, I would do it in this order:

1. Site shell and home page
2. Problem explorer
3. Problem detail
4. Graph
5. Radar and Attempts unification

That order gives OpenProblemAtlas the fastest path from "promising dataset" to "site people star, share, and come back to."
