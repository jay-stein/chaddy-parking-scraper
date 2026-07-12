# Chadstone Parking Scraper

Historical parking occupancy and traffic forecast data for [Chadstone Shopping Centre](https://www.chadstone.com.au/), Melbourne's premier retail destination.

Collected every **30 minutes** via GitHub Actions cron and committed to this repository for public analysis.

## Data

### `data/parking.csv`

Live occupancy snapshot for each public car park (A–F, excluding D which is private).

| Column | Description |
|---|---|
| `retrieved_at` | Timestamp of the scrape (AEST) |
| `car_park` | Car park letter (A, B, C, E, F) |
| `occupied` | Number of occupied spaces at that moment |
| `vacant` | Number of vacant spaces at that moment |
| `total_occupied` | Total occupied across all car parks |
| `total_vacant` | Total vacant across all car parks |

### `data/traffic.csv`

7-day hourly traffic forecast, refreshed each scrape.

| Column | Description |
|---|---|
| `retrieved_at` | Timestamp of the scrape (AEST) |
| `datestamp` | Forecast date (YYYY-MM-DD) |
| `hour` | Hour of day (0–23) |
| `occupancy` | Forecast occupancy ratio (0.0–1.0+, can exceed 1.0 on peak days) |
| `alert_level` | GREEN / YELLOW / RED |

## Analysis

Recommended tools: [Pandas](https://pandas.pydata.org/) or [Polars](https://pola.rs/).

```python
import polars as pl

parking = pl.read_csv("data/parking.csv")
traffic = pl.read_csv("data/traffic.csv")

# Busiest car park by hour
parking.group_by("car_park").agg(
    pl.mean("occupied").alias("avg_occupied")
).sort("avg_occupied", descending=True)

# Peak traffic forecast this week
traffic.filter(pl.col("alert_level") == "RED").group_by("datestamp").agg(
    pl.count().alias("red_hours")
)
```

## How It Works

- **Source**: Chadstone's public API at `chadstone.com.au/api/parking` and `/api/traffic`
- **Schedule**: GitHub Actions cron `*/30 * * * *` (every 30 minutes)
- **Tool**: Python script using `curl` to bypass TLS fingerprinting blocks
- **Storage**: Data committed directly to this repo (CSV format)

## Car Park Reference

| Letter | Name |
|---|---|
| A | David Jones (5 levels) |
| B | Social Quarter / HOYTS / Legoland |
| C | Market Pavilion / Coles / ALDI |
| D | Commercial Private Parking |
| E | Open Air 2h Free: Market Pavilion, Dining, Fresh Food |
| F | Myer (2 levels) |

## License

MIT — use the data however you like.
