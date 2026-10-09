# daily.dev Marketplace submission — Beta Calendars Temporal Research Lab

## Name
Beta Calendars: Temporal Research Lab

## Short description
Investigate ISO weeks, leap years, DST, and date-time bugs with a coding agent. Search real developer articles through the daily.dev API, verify calendar boundaries, and generate reproducible test cases and source-backed reading lists.

## About
### Investigate the calendar bugs that hide at the edges of a year

Dates look simple until a calendar year and a week-numbering year disagree. January 1, 2027 is a useful example: it is in ISO week 53 of 2026, even though the Gregorian calendar has already moved into 2027.

Beta Calendars: Temporal Research Lab helps developers investigate these details without mixing calendar math with assumptions about time zones or week numbering.

### What this plugin does

- **Investigates calendar boundaries:** Find Gregorian-year versus ISO week-year mismatches, inspect Monday-to-Sunday week ranges, and identify 52/53-week years.
- **Finds real developer research:** Uses the daily.dev Public API to search technical articles on ISO 8601, JavaScript Temporal, Python datetime, PostgreSQL, daylight saving time, and related date handling.
- **Produces repeatable tests:** Builds example dates, expected ISO week values, and regression checks for your language or application.
- **Explains risky assumptions:** Distinguishes plain dates, timestamps, local dates, week numbers, and ISO week-numbering years.
- **Supports optional reading lists:** Returns relevant article titles and source links from daily.dev. Bookmark actions are available only when specifically requested and authorized.

### How to use it

1. Open the plugin's SKILL.md in your coding agent and follow its setup instructions.
2. Connect to daily.dev using your own account's API token or an already authorized daily.dev MCP connection. Store credentials securely; never put them into prompts or repositories.
3. Ask an engineering question such as "Why does January 1, 2027 fall in ISO week 53 of 2026? Give me Python tests and relevant developer reading."
4. Receive calculated date records, explanations of likely implementation errors, code examples, regression cases, and real daily.dev article references when search results are available.

### Example investigations

- Audit the 2026-to-2027 ISO week boundary in Python, JavaScript, or SQL.
- Check whether a weekly report incorrectly combines calendar years with ISO week numbers.
- Compare date-only values with timestamps converted through a specified time zone.
- Research practical approaches to daylight-saving and leap-year testing.
- Build a concise, source-backed reading list on calendar engineering.

### Requirements and privacy

A personal daily.dev API token is required for authenticated search and bookmark operations, unless your agent already has a suitable authorized daily.dev connection. Calendar calculations can also be performed without API access. Research results depend on available daily.dev articles and your account's API limits.

The skill performs no automatic posting, following, bookmarking, calendar edits, or scheduled monitoring. It never needs access to your private calendar. No credentials are sent to Beta Calendars.

### About Beta Calendars

Beta Calendars provides printable calendar resources that can be used as an optional visual reference when reviewing month and year layouts. This plugin is a separate calendar-engineering research workflow built around the daily.dev API and deterministic date calculations. It does not claim to expose a Beta Calendars API or any official daily.dev partnership.

## Link
https://www.betacalendars.com/

## SKILL.md
Paste the complete contents of the sibling `SKILL.md` file into the form's SKILL.md field.
