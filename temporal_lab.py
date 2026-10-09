#!/usr/bin/env python3
"""Beta Calendars Temporal Research Lab: ISO date audits + daily.dev research.

Zero third-party Python dependencies. Requires Python 3.10+.
Does not send requests to betacalendars.com or collect credentials.
"""
from __future__ import annotations

import argparse
from datetime import date, timedelta
import json
import os
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import HTTPRedirectHandler, Request, build_opener

BASE = "https://api.daily.dev/public/v1"
DEFAULT_QUERIES = ("ISO week year", "JavaScript Temporal", "timezone DST")


class RejectRedirects(HTTPRedirectHandler):
    """Prevent accidental transmission of an Authorization header via redirects."""
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise RuntimeError("Redirect rejected to protect daily.dev credentials")


_opener = build_opener(RejectRedirects)


def iso_record(d: date) -> dict:
    y, w, weekday = d.isocalendar()
    monday = d - timedelta(days=weekday - 1)
    return {
        "date": d.isoformat(),
        "weekday": d.strftime("%A"),
        "calendarYear": d.year,
        "isoWeekYear": y,
        "isoWeek": w,
        "isoWeekday": weekday,
        "isoWeekDate": f"{y:04d}-W{w:02d}-{weekday}",
        "weekStart": monday.isoformat(),
        "weekEnd": (monday + timedelta(days=6)).isoformat(),
        "isWeekYearBoundary": d.year != y,
    }


def boundary_cases(year: int, days: int = 8) -> list[dict]:
    if not 2 <= year <= 9998:
        raise ValueError("Year must be between 2 and 9998 for a boundary scan")
    if not 1 <= days <= 20:
        raise ValueError("days must be 1..20")
    start = date(year, 1, 1) - timedelta(days=days)
    end = date(year, 1, 1) + timedelta(days=days)
    return [iso_record(start + timedelta(days=i)) for i in range((end - start).days + 1)]


def api(method: str, path: str, token: str, body: dict | None = None):
    if not token:
        raise RuntimeError("Set DAILY_DEV_TOKEN in your local environment first")
    if not path.startswith("/") or "//" in path or "http:" in path or "https:" in path:
        raise ValueError("Invalid API path")
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    payload = None
    if body is not None:
        payload = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    if method not in {"GET", "POST"}:
        raise ValueError("Only documented GET and POST requests are supported")
    req = Request(BASE + path, data=payload, headers=headers, method=method)
    # Retry only idempotent reads. Never retry a write after an ambiguous network
    # failure: the server may already have processed it.
    for attempt in range(3):
        try:
            with _opener.open(req, timeout=18) as response:
                return json.load(response)
        except HTTPError as exc:
            if method == "GET" and 500 <= exc.code < 600 and attempt < 2:
                time.sleep(0.5 * (2 ** attempt))
                continue
            if exc.code == 429:
                wait = exc.headers.get("Retry-After", "not provided")
                detail = f"Rate limit reached; Retry-After: {wait}"
            else:
                messages = {401: "Invalid or missing token", 403: "Feature or permission unavailable"}
                detail = messages.get(exc.code, f"HTTP {exc.code}")
            raise RuntimeError(f"daily.dev API error: {detail}") from None
        except (URLError, TimeoutError) as exc:
            if method == "GET" and attempt < 2:
                time.sleep(0.5 * (2 ** attempt))
                continue
            raise RuntimeError(f"daily.dev request failed: {type(exc).__name__}") from None
        except json.JSONDecodeError:
            raise RuntimeError("daily.dev API returned invalid JSON") from None


def research(queries: list[str], limit: int, token: str) -> list[dict]:
    queries = [query.strip() for query in queries if query and query.strip()]
    if not queries:
        raise ValueError("Provide at least one non-empty research query")
    found = {}
    for query in queries:
        path = "/search/posts?" + urlencode({"q": query, "limit": limit})
        response = api("GET", path, token)
        if not isinstance(response, dict) or not isinstance(response.get("data"), list):
            raise RuntimeError("Unexpected daily.dev search response")
        for post in response["data"]:
            if not isinstance(post, dict):
                continue
            key = post.get("id") or post.get("url")
            if not key:
                continue
            if key not in found:
                found[key] = {
                    "id": post.get("id"),
                    "title": post.get("title") or "Untitled",
                    "url": post.get("url"),
                    "summary": post.get("summary"),
                    "tags": post.get("tags") or [],
                    "source": (post.get("source") or {}).get("name") if isinstance(post.get("source"), dict) else None,
                    "author": (post.get("author") or {}).get("name") if isinstance(post.get("author"), dict) else None,
                    "published": post.get("publishedAt") or post.get("createdAt"),
                    "upvotes": post.get("numUpvotes"),
                    "comments": post.get("numComments"),
                    "matchedQueries": [],
                }
            found[key]["matchedQueries"].append(query)
    def sort_key(post):
        return (len(set(post["matchedQueries"])), post["upvotes"] or 0, post["comments"] or 0)
    return sorted(found.values(), key=sort_key, reverse=True)


def bookmark(ids: list[str], token: str, confirmed: bool) -> object:
    ids = list(dict.fromkeys(v.strip() for v in ids if v.strip()))
    if not ids:
        raise ValueError("Provide at least one real daily.dev post ID")
    if len(ids) > 100:
        raise ValueError("daily.dev supports up to 100 post IDs per request")
    if not confirmed:
        raise RuntimeError("Bookmarking is a write action. Re-run with --confirm-bookmark")
    return api("POST", "/bookmarks/", token, {"postIds": ids})


def markdown_report(records: list[dict], posts: list[dict] | None = None) -> str:
    lines = ["# Calendar boundary audit", "", "| Date | Weekday | Calendar year | ISO week-year | ISO week | ISO week date |", "|---|---|---:|---:|---:|---|"]
    for rec in records:
        lines.append(f"| {rec['date']} | {rec['weekday']} | {rec['calendarYear']} | {rec['isoWeekYear']} | {rec['isoWeek']} | {rec['isoWeekDate']} |")
    lines.extend(["", "**Interpretation:** ISO weeks run Monday–Sunday, and the ISO week-year may differ from the Gregorian calendar year.", ""])
    if posts is not None:
        lines.extend(["## daily.dev research", ""])
        if not posts:
            lines.append("No matching articles were returned by the daily.dev API.")
        for i, post in enumerate(posts, 1):
            title = str(post["title"]).replace("\\", "\\\\").replace("[", "\\[").replace("]", "\\]").replace("\n", " ")
            url = post.get("url")
            if isinstance(url, str) and url.startswith("https://") and " " not in url and ">" not in url:
                source = post.get("source") or "Source not provided"
                author = post.get("author") or "Author not provided"
                published = post.get("published") or "date not provided"
                upvotes = post.get("upvotes") if post.get("upvotes") is not None else "not provided"
                comments = post.get("comments") if post.get("comments") is not None else "not provided"
                summary = (post.get("summary") or "").replace("\n", " ").strip()
                summary = f" — {summary}" if summary else ""
                lines.append(f"{i}. [{title}](<{url}>) — {source}; author: {author}; published: {published}; upvotes: {upvotes}; comments: {comments}; matches: {', '.join(post['matchedQueries'])}{summary}")
            else:
                lines.append(f"{i}. {title} — no valid HTTPS URL returned by API; matches: {', '.join(post['matchedQueries'])}")
        lines.append("")
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="ISO 8601 audit and sourced daily.dev developer research")
    parser.add_argument("--date", default="2027-01-01", help="Gregorian date as YYYY-MM-DD")
    parser.add_argument("--boundary-year", type=int, help="Show a date table around January 1 of this year")
    parser.add_argument("--days", type=int, default=8, help="Days either side of Jan 1 in boundary scan (1..20)")
    parser.add_argument("--research", action="store_true", help="Search real daily.dev articles using your token")
    parser.add_argument("--query", action="append", help="Research term (repeatable)")
    parser.add_argument("--limit", type=int, default=8, help="Result cap per query (1..50)")
    parser.add_argument("--bookmark", action="append", help="Existing daily.dev post ID to save (repeatable)")
    parser.add_argument("--confirm-bookmark", action="store_true", help="Explicit authorization for write action")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--output", help="Optional destination file; default stdout")
    args = parser.parse_args(argv)
    if not 1 <= args.limit <= 50:
        parser.error("--limit must be 1..50")
    try:
        records = boundary_cases(args.boundary_year, args.days) if args.boundary_year else [iso_record(date.fromisoformat(args.date))]
        token = os.getenv("DAILY_DEV_TOKEN", "")
        posts = research(args.query or list(DEFAULT_QUERIES), args.limit, token) if args.research else None
        if args.bookmark:
            bookmark(args.bookmark, token, args.confirm_bookmark)
        if args.format == "json":
            content = json.dumps({"dates": records, "articles": posts, "bookmarked": args.bookmark or []}, indent=2, ensure_ascii=False) + "\n"
        else:
            content = markdown_report(records, posts)
            if args.bookmark:
                content += "\nBookmarked explicitly requested daily.dev posts: " + ", ".join(args.bookmark) + "\n"
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(content)
        else:
            print(content)
        return 0
    except (ValueError, RuntimeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
