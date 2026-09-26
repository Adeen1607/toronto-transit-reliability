# Toronto Transit Reliability Analytics

A local public-data BI project for measuring TTC bus delay frequency, delay minutes, service gaps, incident causes, route concentration, and time-of-day patterns.

## Business questions

- Which routes, incidents, locations, and periods account for the most delay minutes?
- How do delay frequency and severity differ?
- When are service gaps most common?
- Which routes show persistent problems rather than isolated events?
- How should operations teams prioritize routes using both impact and recurrence?

## Data source

The project uses the City of Toronto's official [TTC Bus Delay Data](https://open.toronto.ca/dataset/ttc-bus-delay-data/) package. The download script queries Toronto Open Data's catalogue API and retrieves all published tabular resources.

## Deliverables

- catalogue-driven official data download;
- multi-file schema normalization;
- event-level delay fact table;
- monthly, route, incident, weekday, and hourly scorecards;
- Power BI KPI measures;
- transparent treatment of zero-minute and missing delay records.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/download_data.py
python src/build_model.py
```

## Dashboard pages

1. Network reliability overview
2. Route impact and recurrence
3. Incident causes
4. Time-of-day and weekday patterns
5. Delay locations
6. Data quality and coverage

## Interpretation

A recorded delay event is not the same as passenger delay. The source does not provide ridership exposure for every event, so total minutes and event counts are operational indicators rather than estimates of total customer time lost. Reporting periods and fields can change across source files.
