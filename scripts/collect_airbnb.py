"""Download Inside Airbnb listings + reviews for a set of vacation-style cities."""
import pathlib
import requests

BASE = "https://data.insideairbnb.com/united-states"
CITIES = {  # name: (path, snapshot date)
    "austin": ("tx/austin", "2026-09-17"),
    "san-diego": ("ca/san-diego", "2026-09-20"),
    "hawaii": ("hi/hawaii", "2026-09-17"),
    "asheville": ("nc/asheville", "2026-09-19"),
    "new-orleans": ("la/new-orleans", "2026-09-16"),
    "bozeman": ("mt/bozeman", "2026-09-16"),
    "broward-county": ("fl/broward-county", "2026-09-22"),
}
OUT = pathlib.Path(__file__).resolve().parent.parent / "data" / "raw"


def fetch(url, dest):
    if dest.exists():
        return
    with requests.get(url, stream=True, timeout=120) as r:
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_content(1 << 20):
                f.write(chunk)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for city, (path, date) in CITIES.items():
        for kind in ("listings", "reviews"):
            dest = OUT / f"{city}_{kind}.csv.gz"
            print("fetching", dest.name, flush=True)
            fetch(f"{BASE}/{path}/{date}/data/{kind}.csv.gz", dest)
