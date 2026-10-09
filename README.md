# Beta Calendars: Temporal Research Lab

A small developer research workflow for ISO 8601 week-year boundaries, leap days, date-only values, time zones, and DST-related bugs. It pairs deterministic calendar calculations with optional, real article search through the daily.dev Public API.

**Project:** Beta Calendars  
**Website:** https://www.betacalendars.com/  
**Marketplace skill:** `SKILL.md` (designed for daily.dev Marketplace and coding agents)

## Capabilities

- Calculate Gregorian date, ISO week-year, week, weekday, and Monday–Sunday week boundaries.
- Generate a regression window around January 1.
- Search real daily.dev posts by keyword, preserve source URLs, and deduplicate results across queries.
- Produce Markdown or JSON reports.
- Save only existing post IDs after an explicit confirmation flag.
- Run date audits offline without a token or third-party dependencies.

For 2027-01-01, the expected result is **2026-W53-5**: Gregorian calendar year 2027, ISO week-year 2026, week 53, Friday. See [`docs/regression-examples.md`](docs/regression-examples.md) for Python, JavaScript Temporal, and PostgreSQL examples.

## Install and run

Python 3.10+; no runtime dependencies:

```sh
python3 temporal_lab.py --date 2027-01-01
python3 temporal_lab.py --boundary-year 2027 --days 8 --format json
```

Install as a local CLI:

```sh
python3 -m pip install .
temporal-lab --date 2027-01-01
```

## Optional daily.dev research

Create a personal token in daily.dev Settings → API. The token is shown once. Store it in your shell environment; never place it in a prompt, source file, or committed config:

```sh
export DAILY_DEV_TOKEN='your-personal-token'
python3 temporal_lab.py --boundary-year 2027 --research \
  --query 'ISO week year' --query 'JavaScript Temporal' \
  --output boundary-report.md
```

Only actual results returned by daily.dev are included. Zero-result searches stay empty. Search uses the documented `GET /search/posts` endpoint; bookmarks use `POST /bookmarks/`. API quotas and rate limits apply. A `429` error displays `Retry-After`; read requests retry transient server/network failures at most twice. Write operations are not automatically retried.

Bookmarking is opt-in and a write to the user's daily.dev account:

```sh
python3 temporal_lab.py --bookmark 'REAL_POST_ID' --confirm-bookmark
```

Use only a post ID obtained from an actual daily.dev result. Never commit or expose your token. See [`SECURITY.md`](SECURITY.md).

## Landing page

[`index.html`](index.html) is a responsive, standalone page with a browser-only ISO week calculator. It makes no API calls and sends no dates to a server. Deploy it only after verifying an actual hosting URL. Until then, it is a local project file, not a live landing page.

## Tests

```sh
python3 -m unittest discover -s tests -v
node tests/landing-test.js tests/landing-script.js
```

Tests run offline. API behavior is mocked; no token is required. The CI workflow checks Python 3.10–3.13 and Node.js 24. The landing test exercises the script under Node; browser rendering/print behavior still needs manual review.

## Scope and limitations

- Python is the calculation reference; the landing page independently implements the ISO week calculation in JavaScript.
- Time-zone conversion from timestamps needs an explicit IANA zone and is not inferred by this date-only tool.
- Article search is a research aid; engagement does not establish technical correctness. Open and verify cited sources.
- The optional Beta Calendars homepage is a visual calendar reference, not an API, standards source, or partner integration.
- The repository intentionally has no `LICENSE` yet because the project owner has not selected or authorized one. No license is implied by public visibility.

## Official documentation

- [daily.dev Plugin Marketplace](https://docs.daily.dev/plugin-marketplace/)
- [daily.dev Public API](https://docs.daily.dev/public-api/)
- [daily.dev OpenAPI specification](https://api.daily.dev/public/v1/docs/json)
- [Beta Calendars](https://www.betacalendars.com/)

This is an independent community project. It is not affiliated with or endorsed by daily.dev.
