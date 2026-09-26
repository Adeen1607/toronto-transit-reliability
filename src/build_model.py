"""Normalize TTC bus-delay files and build reporting scorecards."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


REQUIRED = {"date", "route", "incident", "min_delay", "min_gap"}


def normalize_columns(frame: pd.DataFrame) -> pd.DataFrame:
    data = frame.copy()
    data.columns = [
        str(column).strip().lower().replace(" ", "_").replace("-", "_")
        for column in data.columns
    ]
    aliases = {
        "delay": "min_delay",
        "delay_min": "min_delay",
        "gap": "min_gap",
        "gap_min": "min_gap",
    }
    return data.rename(columns={key: value for key, value in aliases.items() if key in data})


def read_resource(path: Path) -> list[pd.DataFrame]:
    if path.suffix.lower() == ".csv":
        return [pd.read_csv(path)]
    if path.suffix.lower() in {".xls", ".xlsx"}:
        sheets = pd.read_excel(path, sheet_name=None)
        return list(sheets.values())
    return []


def load_events(input_dir: Path) -> pd.DataFrame:
    frames = []
    for path in sorted(input_dir.iterdir()):
        for sheet in read_resource(path):
            normalized = normalize_columns(sheet)
            if REQUIRED.issubset(normalized.columns):
                normalized["source_file"] = path.name
                frames.append(normalized)

    if not frames:
        raise ValueError("No source table contained the required TTC delay fields.")

    events = pd.concat(frames, ignore_index=True)
    events["date"] = pd.to_datetime(events["date"], errors="coerce")
    events["min_delay"] = pd.to_numeric(events["min_delay"], errors="coerce")
    events["min_gap"] = pd.to_numeric(events["min_gap"], errors="coerce")
    events["route"] = events["route"].astype("string").str.strip()
    events["incident"] = events["incident"].astype("string").str.strip()

    if "time" in events:
        parsed_time = pd.to_datetime(events["time"].astype("string"), errors="coerce")
        events["event_hour"] = parsed_time.dt.hour
    else:
        events["event_hour"] = pd.NA

    events["weekday"] = events["date"].dt.day_name()
    events["year_month"] = events["date"].dt.to_period("M").astype("string")
    events["has_recorded_delay"] = events["min_delay"].gt(0)
    events["severe_delay"] = events["min_delay"].ge(20)

    events = events.loc[
        events["date"].notna()
        & events["min_delay"].ge(0)
        & events["min_gap"].ge(0)
        & events["route"].notna()
    ].copy()
    events.insert(0, "delay_event_id", range(1, len(events) + 1))
    return events


def summarize(events: pd.DataFrame, dimensions: list[str]) -> pd.DataFrame:
    result = (
        events.groupby(dimensions, dropna=False)
        .agg(
            delay_events=("delay_event_id", "count"),
            recorded_delay_events=("has_recorded_delay", "sum"),
            severe_delay_events=("severe_delay", "sum"),
            total_delay_minutes=("min_delay", "sum"),
            average_delay_minutes=("min_delay", "mean"),
            total_gap_minutes=("min_gap", "sum"),
        )
        .reset_index()
    )
    result["severe_event_rate"] = (
        result["severe_delay_events"] / result["delay_events"]
    )
    return result.sort_values("total_delay_minutes", ascending=False)


def build_model(input_dir: Path, output_dir: Path) -> None:
    events = load_events(input_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    outputs = {
        "fact_delay_events.csv": events,
        "monthly_reliability.csv": summarize(events, ["year_month"]),
        "route_scorecard.csv": summarize(events, ["route"]),
        "incident_scorecard.csv": summarize(events, ["incident"]),
        "weekday_scorecard.csv": summarize(events, ["weekday"]),
        "hourly_scorecard.csv": summarize(events, ["event_hour"]),
    }
    if "location" in events.columns:
        outputs["location_scorecard.csv"] = summarize(events, ["location"])

    for filename, table in outputs.items():
        table.to_csv(output_dir / filename, index=False)

    print(f"Wrote {len(events):,} delay events to {output_dir}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build TTC reliability tables.")
    parser.add_argument("--input-dir", type=Path, default=Path("data/raw"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/processed"))
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    build_model(arguments.input_dir, arguments.output_dir)
