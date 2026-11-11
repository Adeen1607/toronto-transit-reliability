"""Downloader regression tests using fake catalogue and file responses."""

from src import download_data


class FakeResponse:
    def __init__(self, payload=None, content=b""):
        self.payload = payload
        self.content = content

    def raise_for_status(self):
        pass

    def json(self):
        return self.payload

    def iter_content(self, chunk_size):
        yield self.content

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def test_duplicate_resource_names_are_not_overwritten(monkeypatch, tmp_path):
    catalogue = {"success": True, "result": {"resources": [
        {"name": "Bus Delay", "format": "CSV", "url": "https://example.com/a.csv"},
        {"name": "Bus Delay", "format": "CSV", "url": "https://example.com/b.csv"},
    ]}}

    def fake_get(url, **kwargs):
        if url == download_data.API_URL:
            return FakeResponse(payload=catalogue)
        return FakeResponse(content=b"first" if url.endswith("a.csv") else b"second")

    monkeypatch.setattr(download_data.requests, "get", fake_get)
    paths = download_data.download(tmp_path)
    assert [path.name for path in paths] == ["Bus_Delay.csv", "Bus_Delay_2.csv"]
    assert [path.read_bytes() for path in paths] == [b"first", b"second"]


def test_url_extension_uses_catalogue_format_when_not_tabular(monkeypatch, tmp_path):
    catalogue = {"success": True, "result": {"resources": [
        {"name": "2024 delays", "format": "CSV", "url": "https://example.com/export.zip"},
    ]}}

    def fake_get(url, **kwargs):
        if url == download_data.API_URL:
            return FakeResponse(payload=catalogue)
        return FakeResponse(content=b"date,route\n2024-01-01,1\n")

    monkeypatch.setattr(download_data.requests, "get", fake_get)
    paths = download_data.download(tmp_path)
    assert paths[0].name == "2024_delays.csv"
    assert paths[0].read_text().startswith("date,route")
