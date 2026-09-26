"""Download TTC bus-delay resources from Toronto Open Data."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from urllib.parse import urlparse

import requests


API_URL = (
    "https://ckan0.cf.opendata.inter.prod-toronto.ca/api/3/action/"
    "package_show?id=ttc-bus-delay-data"
)
TABULAR_FORMATS = {"CSV", "XLS", "XLSX"}


def safe_name(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("_")
    return cleaned or "resource"


def download(destination: Path) -> list[Path]:
    destination.mkdir(parents=True, exist_ok=True)
    response = requests.get(API_URL, timeout=60)
    response.raise_for_status()
    payload = response.json()
    if not payload.get("success"):
        raise ValueError("Toronto Open Data catalogue request was unsuccessful.")

    downloaded = []
    for number, resource in enumerate(payload["result"]["resources"], start=1):
        resource_format = str(resource.get("format", "")).upper()
        if resource_format not in TABULAR_FORMATS:
            continue

        url = resource["url"]
        suffix = Path(urlparse(url).path).suffix or f".{resource_format.lower()}"
        name = safe_name(resource.get("name") or f"ttc_bus_delay_{number}")
        target = destination / f"{name}{suffix}"

        with requests.get(url, stream=True, timeout=180) as file_response:
            file_response.raise_for_status()
            with target.open("wb") as handle:
                for chunk in file_response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        handle.write(chunk)
        downloaded.append(target)
        print(f"Downloaded {target.name}")

    if not downloaded:
        raise ValueError("No CSV or Excel resources were found in the data package.")
    return downloaded


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download TTC bus-delay data.")
    parser.add_argument("--destination", type=Path, default=Path("data/raw"))
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    download(arguments.destination)
