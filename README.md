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


## Rebuild the reading edition

```bash
python -m pip install -r requirements-research.txt
python scripts/build_research_site.py
```

This renders saved notebook outputs without rerunning model training or external APIs. To refresh findings, run the analysis commands above first, update `reports/research-findings.md`, and rebuild.

<!-- research-edition:start -->
## Research edition

[Research report and final visual results](research/report.md) · [Browser-ready notebook catalogue](research/notebooks.html)

Fresh execution on 11 October 2026 using the **2024 workbook only**. After the pipeline eligibility filters, **59,021 events** remain, totaling **1,263,332 recorded vehicle-delay minutes**. The leading incident category by minutes is **Diversion**. The values measure recorded incidents, not passenger minutes or delay per scheduled trip.

| Measure | Value |
|---|---:|
| events | 59021 |
| recorded delay minutes | 1263332.0000 |
| source window | 2024 |



The `research/` folder contains a professional static reading edition. The Pages workflow deploys it after GitHub Pages is enabled with **GitHub Actions** as the publishing source. Intended URL: `https://adeen1607.github.io/toronto-transit-reliability/`. Deployment status must be checked in Actions before treating that address as live.

<!-- research-edition:end -->
