"""Generate polished xy charts of Chadstone parking occupancy data.

Each chart is exported as a self-contained HTML file under notebooks/.
"""
from __future__ import annotations

import os
from pathlib import Path

import polars as pl
import xy

# Override with CHARTS_DATA_URL (e.g. "data/parking.csv") to generate from local data.
DATA_URL = os.environ.get(
    "CHARTS_DATA_URL",
    "https://github.com/jay-stein/chaddy-parking-scraper/blob/master/data/parking.csv?raw=true",
)
OUT = Path("charts")

_GRID = "var(--grid, #e4e4e7)"
_SURFACE = "var(--surface, #ffffff)"
_TEXT = "var(--text, #52525b)"
_DARK_GRID = "var(--grid-dark, #27272a)"
_DARK_SURFACE = "var(--surface-dark, #09090b)"
_DARK_TEXT = "var(--text-dark, #d4d4d8)"

_PALETTE = ["#7c3aed", "#0ea5e9", "#10b981", "#f59e0b", "#ef4444"]

_TIP = {
    "background": "#ffffff",
    "color": "#1e293b",
    "border": "1px solid #e2e8f0",
    "border-radius": 10,
    "box-shadow": "0 4px 16px rgba(0,0,0,0.10)",
    "padding": "10px 14px",
    "font-size": 14,
}

_TIP_SLOTS = {
    "tooltip_title": {
        "font-weight": 600,
        "font-size": 13,
        "color": "#64748b",
        "margin-bottom": 6,
        "padding-bottom": 5,
        "border-bottom": "1px solid #e2e8f0",
    },
    "tooltip_row": {
        "display": "grid",
        "grid-template-columns": "6rem 1fr",
        "gap": 8,
        "padding": "2px 0",
        "font-size": 14,
    },
    "tooltip_label": {"color": "#64748b"},
    "tooltip_value": {"font-weight": 600, "text-align": "right", "color": "#1e293b"},
}

_CHART_CLASS = (
    f"bg-[{_SURFACE}] [{_SURFACE[4:-1]}:{_SURFACE[4:-1]}] "
    f"[{_GRID[4:-1]}:{_GRID[4:-1]}] [{_TEXT[4:-1]}:{_TEXT[4:-1]}] "
    f"dark:bg-[{_DARK_SURFACE}] "
    f"dark:[{_DARK_SURFACE[4:-1]}:{_DARK_SURFACE[4:-1]}] "
    f"dark:[{_DARK_GRID[4:-1]}:{_DARK_GRID[4:-1]}] "
    f"dark:[{_DARK_TEXT[4:-1]}:{_DARK_TEXT[4:-1]}]"
)

QUIET_X = xy.x_axis(
    show=False,
    grid=False,
)
QUIET_Y = xy.y_axis(
    show=False,
    grid=True,
    style={"grid_color": _GRID, "grid_width": 1, "grid_opacity": 0.6},
)


def _quiet_axis_style() -> dict:
    return {
        "axis_width": 0,
        "axis_color": "#00000000",
        "tick_width": 0,
        "tick_color": "#00000000",
        "tick_label_color": "#00000000",
        "label_color": "#00000000",
        "grid_opacity": 0,
    }


def _to_html(chart: xy.Chart, name: str) -> Path:
    path = OUT / f"{name}.html"
    path.write_text(chart.to_html(), encoding="utf-8")
    print(f"  -> {path} ({path.stat().st_size} bytes)")
    return path


def load_data() -> pl.DataFrame:
    return pl.read_csv(DATA_URL).with_columns(
        pl.col("retrieved_at").str.strptime(pl.Datetime, "%Y-%m-%d %H:%M:%S")
    )


def chart1_occupancy_over_time(df: pl.DataFrame) -> xy.Chart:
    """Line chart: all 5 car parks on one plot, clean palette."""
    car_parks = df["car_park"].unique().sort().to_list()
    cp_names = [f"Car Park {cp}" for cp in car_parks]

    lines = []
    for i, cp in enumerate(car_parks):
        sub = df.filter(pl.col("car_park") == cp).sort("retrieved_at")
        lines.append(
            xy.line(
                sub["retrieved_at"],
                sub["occupied"],
                name=cp_names[i],
                color=_PALETTE[i],
                width=2,
                curve="linear",
            )
        )

    return xy.line_chart(
        *lines,
        xy.legend(
            loc="upper left",
            ncols=3,
            style={"background": "transparent", "border": 0, "box-shadow": "none"},
        ),
        xy.tooltip(
            fields=cp_names,
            title="{x:%d %b %Y %H:%M}",
            format={name: ",.0f" for name in cp_names},
            style=_TIP,
        ),
        xy.theme(
            plot_background=_SURFACE,
            grid_color=_GRID,
            text_color=_TEXT,
        ),
        xy.x_axis(
            style=_quiet_axis_style() | {"grid_opacity": 0},
        ),
        xy.y_axis(
            style={
                "axis_width": 0,
                "axis_color": "#00000000",
                "tick_width": 0,
                "tick_color": "#00000000",
                "tick_label_color": "#00000000",
                "label_color": "#00000000",
                "grid_color": _GRID,
                "grid_width": 1,
                "grid_opacity": 0.6,
            },
        ),
        styles={
            "legend_item": {"gap": 6, "padding": 0},
            "legend_swatch": {"width": 22, "height": 3, "border-radius": 999},
            **_TIP_SLOTS,
        },
        class_name=_CHART_CLASS,
        width="100%",
        height=420,
        padding=(48, 24, 32, 48),
    )


def chart2_carpark_b_area(df: pl.DataFrame) -> xy.Chart:
    """Area chart: Car Park B with smooth gradient, hline annotation for capacity."""
    sub = df.filter(pl.col("car_park") == "B").sort("retrieved_at")
    return xy.area_chart(
        xy.area(
            sub["retrieved_at"],
            sub["occupied"],
            name="Car Park B",
            color="#7c3aed",
            fill="linear-gradient(#7c3aed4d 5%, #7c3aed00 95%)",
            opacity=1,
            curve="smooth",
            line_width=2.5,
        ),
        xy.hline(
            1080,
            text="Max capacity",
            color="#ef4444",
            width=1.5,
            style={
                "label_color": "#ef4444",
                "background_color": "#ef44441a",
                "padding": "2px 6px",
                "border-radius": 4,
            },
        ),
        xy.legend(show=False),
        xy.tooltip(
            title="{x:%d %b %Y %H:%M}",
            format={"y": ",.0f"},
            style=_TIP,
        ),
        xy.theme(plot_background=_SURFACE, grid_color=_GRID, text_color=_TEXT),
        xy.x_axis(
            show=False,
            grid=False,
        ),
        xy.y_axis(
            show=False,
            grid=True,
            style={"grid_color": _GRID, "grid_width": 1, "grid_opacity": 0.6},
        ),
        styles=_TIP_SLOTS,
        class_name=_CHART_CLASS,
        width="100%",
        height=420,
        padding=(24, 48, 32, 24),
    )


def chart3_peak_hour_bars(df: pl.DataFrame) -> xy.Chart:
    """Column chart: average occupancy by hour of day for each car park."""
    df_hour = df.with_columns(pl.col("retrieved_at").dt.hour().alias("hour"))
    avg = (
        df_hour.group_by(["hour", "car_park"])
        .agg(pl.mean("occupied").alias("avg_occupied"))
        .sort(["hour", "car_park"])
    )
    hours = sorted(avg["hour"].unique().to_list())
    car_parks = sorted(avg["car_park"].unique().to_list())
    hour_centers = list(range(len(hours)))
    n_cps = len(car_parks)
    bar_width = 0.16
    offsets = [
        bar_width * (i - (n_cps - 1) / 2) for i in range(n_cps)
    ]

    columns = []
    for cp_i, cp in enumerate(car_parks):
        vals = [
            avg.filter(pl.col("hour") == h, pl.col("car_park") == cp)["avg_occupied"][0]
            if avg.filter(pl.col("hour") == h, pl.col("car_park") == cp).height > 0
            else 0
            for h in hours
        ]
        x_positions = [c + offsets[cp_i] for c in hour_centers]
        columns.append(
            xy.column(
                x_positions,
                vals,
                name=f"Car Park {cp}",
                color=_PALETTE[cp_i],
                width=0.14,
                opacity=1,
                corner_radius=3,
                stroke_width=0,
            )
        )

    return xy.column_chart(
        *columns,
        xy.legend(
            loc="upper left",
            ncols=5,
            style={"background": "transparent", "border": 0, "box-shadow": "none"},
        ),
        xy.tooltip(
            title="Hour {x}:00",
            format={"y": ",.0f"},
            style=_TIP,
        ),
        xy.theme(plot_background=_SURFACE, grid_color=_GRID, text_color=_TEXT),
        xy.x_axis(
            domain=(-0.6, len(hours) - 0.4),
            tick_values=hour_centers,
            tick_labels=[f"{h:02d}:00" for h in hours],
            style=_quiet_axis_style(),
        ),
        xy.y_axis(
            show=False,
            grid=True,
            style={"grid_color": _GRID, "grid_width": 1, "grid_opacity": 0.6},
        ),
        styles={
            "legend_item": {"gap": 4, "padding": 0, "font-size": 11},
            "legend_swatch": {"width": 10, "height": 10, "border-radius": 2},
            **_TIP_SLOTS,
        },
        class_name=_CHART_CLASS,
        width="100%",
        height=420,
        padding=(46, 24, 40, 48),
    )


def chart4_horizontal_bars(df: pl.DataFrame) -> xy.Chart:
    """Bar chart: average occupancy and vacancy per car park."""
    agg = df.group_by("car_park").agg(
        pl.mean("occupied").round(0).cast(pl.Int64).alias("avg_occupied"),
        pl.mean("vacant").round(0).cast(pl.Int64).alias("avg_vacant"),
    ).sort("car_park")

    bars_occ = [
        xy.bar(
            x=[row["car_park"]],
            y=[row["avg_occupied"]],
            name="Occupied",
            orientation="horizontal",
            color="#7c3aed",
            corner_radius=5,
        )
        for row in agg.iter_rows(named=True)
    ]
    bars_vac = [
        xy.bar(
            x=[row["car_park"]],
            y=[row["avg_vacant"]],
            name="Vacant",
            orientation="horizontal",
            color="#0ea5e9",
            corner_radius=5,
        )
        for row in agg.iter_rows(named=True)
    ]

    return xy.bar_chart(
        *bars_occ,
        *bars_vac,
        xy.legend(
            loc="upper right",
            style={"background": "transparent", "border": 0, "box-shadow": "none"},
        ),
        xy.tooltip(
            title="Car Park {x}",
            format={"y": ",.0f"},
            style=_TIP,
        ),
        xy.theme(plot_background=_SURFACE, grid_color=_GRID, text_color=_TEXT),
        xy.x_axis(
            show=False,
            grid=True,
            style={"grid_color": _GRID, "grid_width": 1, "grid_opacity": 0.6},
        ),
        xy.y_axis(
            style=_quiet_axis_style(),
        ),
        styles={
            "legend_item": {"gap": 8, "padding": 0},
            "legend_swatch": {"width": 12, "height": 12, "border-radius": 3},
            **_TIP_SLOTS,
        },
        class_name=_CHART_CLASS,
        width="100%",
        height=360,
        padding=(24, 24, 32, 24),
    )


def chart5_weekday_weekend_lines(df: pl.DataFrame) -> xy.Chart:
    """Line chart: total occupancy split by weekday vs weekend."""
    df_ts = df.with_columns(
        pl.col("retrieved_at").dt.weekday().alias("dow"),
        pl.col("retrieved_at").dt.hour().alias("hour"),
    )
    df_ts = df_ts.with_columns(
        pl.when(pl.col("dow") < 6)
        .then(pl.lit("Weekday"))
        .otherwise(pl.lit("Weekend"))
        .alias("day_type")
    )
    agg = (
        df_ts.group_by(["day_type", "hour"])
        .agg(pl.mean("occupied").alias("avg_occupied"))
        .sort(["day_type", "hour"])
    )
    weekday = agg.filter(pl.col("day_type") == "Weekday")
    weekend = agg.filter(pl.col("day_type") == "Weekend")

    return xy.line_chart(
        xy.line(
            weekday["hour"],
            weekday["avg_occupied"],
            name="Weekday",
            color="#7c3aed",
            width=3,
            curve="smooth",
        ),
        xy.line(
            weekend["hour"],
            weekend["avg_occupied"],
            name="Weekend",
            color="#f59e0b",
            width=3,
            curve="smooth",
        ),
        xy.legend(
            loc="upper right",
            style={"background": "transparent", "border": 0, "box-shadow": "none"},
        ),
        xy.tooltip(
            title="Hour {x}:00",
            format={"y": ",.0f"},
            style=_TIP,
        ),
        xy.theme(plot_background=_SURFACE, grid_color=_GRID, text_color=_TEXT),
        xy.x_axis(
            domain=(0, 23),
            tick_values=list(range(0, 24, 4)),
            tick_labels=[f"{h:02d}:00" for h in range(0, 24, 4)],
            style=_quiet_axis_style(),
        ),
        xy.y_axis(
            show=False,
            grid=True,
            style={"grid_color": _GRID, "grid_width": 1, "grid_opacity": 0.6},
        ),
        styles={
            "legend_swatch": {"width": 28, "height": 3, "border-radius": 999},
            "legend_item": {"gap": 8, "padding": 0},
            **_TIP_SLOTS,
        },
        class_name=_CHART_CLASS,
        width="100%",
        height=420,
        padding=(48, 24, 32, 48),
    )


def chart6_occupancy_vs_total_combo(df: pl.DataFrame) -> xy.Chart:
    """Combo chart: Car Park A columns with a site-wide total line overlay."""
    sub = df.filter(pl.col("car_park") == "A").sort("retrieved_at")
    return xy.chart(
        xy.column(
            sub["retrieved_at"],
            sub["occupied"],
            name="Car Park A",
            color="#7c3aed",
            corner_radius=0,
            stroke_width=0,
            opacity=0.6,
        ),
        xy.line(
            sub["retrieved_at"],
            sub["total_occupied"],
            name="All Car Parks",
            color="#ef4444",
            width=2.5,
            curve="linear",
        ),
        xy.legend(
            loc="upper left",
            style={"background": "transparent", "border": 0, "box-shadow": "none"},
        ),
        xy.tooltip(
            title="{x:%d %b %Y %H:%M}",
            format={"y": ",.0f"},
            style=_TIP,
        ),
        xy.theme(plot_background=_SURFACE, grid_color=_GRID, text_color=_TEXT),
        xy.x_axis(
            show=False,
            grid=False,
        ),
        xy.y_axis(
            show=False,
            grid=True,
            style={"grid_color": _GRID, "grid_width": 1, "grid_opacity": 0.6},
        ),
        styles={
            "legend_swatch": {"width": 16, "height": 16, "border-radius": 3},
            "legend_item": {"gap": 8, "padding": 0},
            **_TIP_SLOTS,
        },
        class_name=_CHART_CLASS,
        width="100%",
        height=420,
        padding=(48, 24, 32, 48),
    )


def chart7_utilization_heatmap(df: pl.DataFrame) -> xy.Chart:
    """Stem chart: peak occupancy per car park with callout for the winner."""
    agg = (
        df.group_by("car_park")
        .agg(pl.max("occupied").alias("peak"))
        .sort("car_park")
    )
    car_parks = agg["car_park"].to_list()
    peaks = agg["peak"].to_list()
    peak_max = max(peaks)
    max_cp = car_parks[peaks.index(peak_max)]
    positions = list(range(len(car_parks)))

    return xy.stem_chart(
        xy.stem(
            positions,
            peaks,
            name="Peak occupied",
            color="#7c3aed",
            width=2,
            marker_size=10,
        ),
        xy.callout(
            positions[car_parks.index(max_cp)],
            peak_max,
            f"Most busy: {max_cp}",
            dx=16,
            dy=-24,
            anchor="start",
            color="#7c3aed",
            width=1.5,
            style={
                "label_color": "#7c3aed",
                "background": "#7c3aed1a",
                "border": "1px solid #7c3aed66",
                "border-radius": 6,
                "padding": "3px 8px",
            },
        ),
        xy.legend(show=False),
        xy.tooltip(
            title="Car Park {x}",
            format={"y": ",.0f"},
            style=_TIP,
        ),
        xy.theme(plot_background=_SURFACE, grid_color=_GRID, text_color=_TEXT),
        xy.x_axis(
            domain=(-0.4, len(car_parks) - 0.6),
            tick_values=positions,
            tick_labels=car_parks,
            show=False,
            text=True,
        ),
        xy.y_axis(
            show=False,
            grid=True,
            style={"grid_color": _GRID, "grid_width": 1, "grid_opacity": 0.6},
        ),
        styles=_TIP_SLOTS,
        class_name=_CHART_CLASS,
        width="100%",
        height=400,
        padding=(24, 48, 32, 48),
    )


def chart8_box_distribution(df: pl.DataFrame) -> xy.Chart:
    """Box chart: occupancy distribution per car park showing spread and outliers."""
    car_parks = df["car_park"].unique().sort().to_list()
    x_vals = [cp for cp in car_parks for _ in range(1)]
    boxes = []
    for cal_i, cp in enumerate(car_parks):
        vals = df.filter(pl.col("car_park") == cp)["occupied"].to_list()
        boxes.append(
            xy.box(
                values=vals,
                x=[cal_i] * len(vals),
                name=f"Car Park {cp}",
                color=_PALETTE[cal_i],
                width=0.36,
            )
        )

    return xy.box_chart(
        *boxes,
        xy.legend(show=False),
        xy.tooltip(
            fields=["min", "q1", "median", "q3", "max"],
            title="Car Park {x} distribution",
            labels={
                "min": "Min",
                "q1": "Q1",
                "median": "Median",
                "q3": "Q3",
                "max": "Max",
            },
            format={f: ",.0f" for f in ["min", "q1", "median", "q3", "max"]},
            style=_TIP,
        ),
        xy.theme(plot_background=_SURFACE, grid_color=_GRID, text_color=_TEXT),
        xy.x_axis(
            domain=(-0.5, len(car_parks) - 0.5),
            tick_values=list(range(len(car_parks))),
            tick_labels=car_parks,
            show=False,
            text=True,
        ),
        xy.y_axis(
            show=False,
            grid=True,
            style={"grid_color": _GRID, "grid_width": 1, "grid_opacity": 0.6},
        ),
        styles=_TIP_SLOTS,
        class_name=_CHART_CLASS,
        width="100%",
        height=420,
        padding=(24, 48, 32, 48),
    )


def chart9_scatter_correlation(df: pl.DataFrame) -> xy.Chart:
    """Scatter chart: occupied vs total_occupied per record, bubble by vacancy."""
    sample = df.group_by("retrieved_at").agg(
        pl.first("total_occupied"),
        pl.sum("occupied").alias("sum_occupied"),
        pl.sum("vacant").alias("sum_vacant"),
    ).with_columns(
        pl.col("sum_vacant").truediv(pl.col("sum_vacant") + pl.col("sum_occupied")).alias("vacancy_pct"),
        pl.col("retrieved_at").dt.weekday().alias("dow"),
    )
    sample = sample.with_columns(
        pl.when(pl.col("dow") < 6)
        .then(pl.lit("Weekday"))
        .otherwise(pl.lit("Weekend"))
        .alias("day_type")
    )

    weekday = sample.filter(pl.col("day_type") == "Weekday")
    weekend = sample.filter(pl.col("day_type") == "Weekend")

    return xy.scatter_chart(
        xy.scatter(
            weekday["total_occupied"],
            weekday["vacancy_pct"],
            name="Weekday",
            color="#7c3aed",
            size=4,
            opacity=0.55,
            density=False,
            stroke="#7c3aed",
            stroke_width=0.5,
        ),
        xy.scatter(
            weekend["total_occupied"],
            weekend["vacancy_pct"],
            name="Weekend",
            color="#f59e0b",
            size=4,
            opacity=0.55,
            density=False,
            stroke="#f59e0b",
            stroke_width=0.5,
        ),
        xy.legend(
            loc="upper right",
            style={"background": "transparent", "border": 0, "box-shadow": "none"},
        ),
        xy.tooltip(
            title="{x:,.0f} cars occupied",
            format={"y": ".1%"},
            labels={"y": "Vacancy rate"},
            style=_TIP,
        ),
        xy.theme(plot_background=_SURFACE, grid_color=_GRID, text_color=_TEXT),
        xy.x_axis(
            show=False,
            grid=True,
            style={"grid_color": _GRID, "grid_width": 1, "grid_opacity": 0.6},
        ),
        xy.y_axis(
            show=False,
            grid=True,
            style={"grid_color": _GRID, "grid_width": 1, "grid_opacity": 0.6},
        ),
        styles={
            "legend_swatch": {"width": 12, "height": 12, "border-radius": 999},
            "legend_item": {"gap": 8, "padding": 0},
            **_TIP_SLOTS,
        },
        class_name=_CHART_CLASS,
        width="100%",
        height=420,
        padding=(24, 24, 32, 48),
    )


def chart10_heatmap_hour_day(df: pl.DataFrame) -> xy.Chart:
    """Heatmap: average occupancy by hour of day × day of week."""
    df_map = df.with_columns(
        pl.col("retrieved_at").dt.hour().alias("hour"),
        pl.col("retrieved_at").dt.weekday().alias("dow"),
    )
    dow_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    # Pivot: rows = dow, cols = hour, values = mean occupied
    agg = df_map.group_by(["dow", "hour"]).agg(
        pl.mean("occupied").alias("avg_occupied")
    ).sort(["dow", "hour"])

    matrix = []
    for d in range(1, 8):
        row = []
        for h in range(24):
            v = agg.filter(pl.col("dow") == d, pl.col("hour") == h)
            row.append(v["avg_occupied"][0] if v.height else 0)
        matrix.append(row)

    return xy.heatmap_chart(
        xy.heatmap(
            z=matrix,
            name="Avg occupied",
            colormap=[
                (0.0, "#f8edff"),
                (0.33, "#c4b5fd"),
                (0.66, "#8b5cf6"),
                (1.0, "#4c1d95"),
            ],
            opacity=0.94,
        ),
        xy.colorbar(
            title="Cars",
            orientation="horizontal",
            ticks=[200, 600, 1000, 1400, 1800, 2200, 2600],
            style={
                "background": _SURFACE,
                "color": "#4b5563",
                "border": "1px solid #e5e7eb",
                "border-radius": 8,
                "padding": "8px 10px",
            },
        ),
        xy.tooltip(
            fields=["y"],
            title="{x:,.0f} cars (mean)",
            style=_TIP,
        ),
        xy.theme(plot_background=_SURFACE, grid_color=_GRID, text_color=_TEXT),
        xy.x_axis(
            show=False,
            ticks=False,
            grid=False,
            text=False,
        ),
        xy.y_axis(
            show=False,
            ticks=False,
            grid=False,
            text=False,
        ),
        styles={
            "colorbar_bar": {"border-radius": 6},
            "colorbar_tick": {"font-size": 11},
            "colorbar_title": {"font-weight": 600},
            **_TIP_SLOTS,
        },
        class_name=_CHART_CLASS,
        width="100%",
        height=400,
        padding=(24, 24, 56, 24),
    )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    print("Loading data ...")
    df = load_data()
    print(f"  {df.shape[0]} rows, {df['car_park'].n_unique()} car parks")
    print(f"  {df['retrieved_at'].min()}  ->  {df['retrieved_at'].max()}\n")

    print("1. All car parks over time")
    _to_html(chart1_occupancy_over_time(df), "chart1_lines")

    print("2. Car Park B area + capacity line")
    _to_html(chart2_carpark_b_area(df), "chart2_area_b")

    print("3. Average occupancy by hour")
    _to_html(chart3_peak_hour_bars(df), "chart3_hourly")

    print("4. Average occupied vs vacant")
    _to_html(chart4_horizontal_bars(df), "chart4_avg_bars")

    print("5. Weekday vs weekend")
    _to_html(chart5_weekday_weekend_lines(df), "chart5_weekday")

    print("6. Car Park A vs all")
    _to_html(chart6_occupancy_vs_total_combo(df), "chart6_combo")

    print("7. Peak occupancy per car park")
    _to_html(chart7_utilization_heatmap(df), "chart7_peaks")

    print("8. Occupancy distribution per car park (box plot)")
    _to_html(chart8_box_distribution(df), "chart8_box")

    print("9. Occupancy vs vacancy correlation (scatter)")
    _to_html(chart9_scatter_correlation(df), "chart9_scatter")

    print("10. Occupancy heatmap by hour x day of week")
    _to_html(chart10_heatmap_hour_day(df), "chart10_heatmap")

    print(f"\nDone -- {len(list(OUT.glob('chart*.html')))} HTML files in {OUT}/")


if __name__ == "__main__":
    main()
