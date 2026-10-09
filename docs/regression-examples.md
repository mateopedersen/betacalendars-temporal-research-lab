# Regression examples

These short examples verify calendar boundaries without querying an API. They are examples to adapt, not universal time-zone policy.

## Python

```python
from datetime import date

d = date.fromisoformat("2027-01-01")
iso_year, iso_week, iso_weekday = d.isocalendar()
assert (iso_year, iso_week, iso_weekday) == (2026, 53, 5)
```

## JavaScript (Temporal)

Run only in a runtime that supports `Temporal.PlainDate`, or install a tested Temporal polyfill in your own project.

```js
const d = Temporal.PlainDate.from("2027-01-01");
console.assert(d.year === 2027);
console.assert(d.yearOfWeek === 2026);
console.assert(d.weekOfYear === 53);
console.assert(d.dayOfWeek === 5);
```

## PostgreSQL

```sql
SELECT
  DATE '2027-01-01' AS gregorian_date,
  EXTRACT(YEAR FROM DATE '2027-01-01')::int AS calendar_year,
  EXTRACT(ISOYEAR FROM DATE '2027-01-01')::int AS iso_week_year,
  EXTRACT(WEEK FROM DATE '2027-01-01')::int AS iso_week;
```

Expected values are `2027-01-01`, `2027`, `2026`, and `53`. Use `ISOYEAR` together with `WEEK`; do not combine Gregorian `YEAR` with the ISO week number. For timestamp inputs, choose the intended time zone before converting the instant to a local date.
