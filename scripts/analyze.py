"""Compute dataset stats and make Checkpoint 1 figures."""
import json
import pathlib
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests

ROOT = pathlib.Path(__file__).resolve().parent.parent
RAW, FIG = ROOT / "data" / "raw", ROOT / "figures"
FIG.mkdir(exist_ok=True)
CITIES = sorted(p.name.replace("_listings.csv.gz", "") for p in RAW.glob("*_listings.csv.gz"))

listings, review_stats = [], []
for c in CITIES:
    df = pd.read_csv(RAW / f"{c}_listings.csv.gz", usecols=[
        "id", "latitude", "longitude", "price", "number_of_reviews", "review_scores_rating",
        "description", "amenities", "property_type"])
    df["city"] = c
    df["price"] = pd.to_numeric(df["price"].astype(str).str.replace(r"[$,]", "", regex=True), errors="coerce")
    listings.append(df)
    rv = pd.read_csv(RAW / f"{c}_reviews.csv.gz", usecols=["listing_id", "comments"])
    rv["comments"] = rv["comments"].fillna("").astype(str)
    rv["words"] = rv["comments"].str.split().str.len()
    review_stats.append(rv.assign(city=c)[["city", "listing_id", "words"]])
    print(c, len(df), len(rv), flush=True)
L = pd.concat(listings, ignore_index=True)
R = pd.concat(review_stats, ignore_index=True)

# Open-Meteo monthly weather at each city's listing centroid (API collection)
weather = {}
for c in CITIES:
    g = L[L.city == c]
    try:
        r = requests.get("https://archive-api.open-meteo.com/v1/archive", timeout=60, params={
            "latitude": g.latitude.median(), "longitude": g.longitude.median(),
            "start_date": "2025-01-01", "end_date": "2025-12-31",
            "daily": "temperature_2m_mean", "temperature_unit": "fahrenheit", "timezone": "auto"})
        d = pd.DataFrame(r.json()["daily"])
        d["m"] = pd.to_datetime(d["time"]).dt.month
        weather[c] = d.groupby("m")["temperature_2m_mean"].mean().round(1).tolist()
    except Exception as e:  # noqa
        print("weather failed", c, e)
(ROOT / "data" / "weather_monthly_f.json").write_text(json.dumps(weather))

# Summary stats
price = L.price[(L.price > 0) & (L.price < 2000)]
stats = {
    "cities": len(CITIES), "listings": len(L), "reviews": len(R),
    "total_review_words": int(R.words.sum()), "median_review_words": float(R.words.median()),
    "listings_with_reviews": int((L.number_of_reviews > 0).sum()),
    "listings_with_description_pct": round(100 * L.description.notna().mean(), 1),
    "listings_with_price_pct": round(100 * L.price.notna().mean(), 1),
    "median_price": float(price.median()), "weather_cities": len(weather),
    "per_city": {c: {"listings": int((L.city == c).sum()), "reviews": int((R.city == c).sum()),
                     "median_price": float(L[(L.city == c) & (L.price > 0)].price.median())} for c in CITIES},
}
(ROOT / "data" / "stats.json").write_text(json.dumps(stats, indent=2))
print(json.dumps(stats, indent=2))

# Atmosphere-term frequency (preview of the lexicon idea)
terms = ["walkable", "quiet", "cozy", "family", "nightlife", "beach", "hiking", "view", "peaceful", "romantic", "crowded", "noisy"]
sample = pd.concat([pd.read_csv(RAW / f"{c}_reviews.csv.gz", usecols=["comments"], nrows=50000) for c in CITIES])
txt = sample.comments.fillna("").str.lower()
term_pct = {t: 100 * txt.str.contains(r"\b" + t).mean() for t in terms}

plt.rcParams.update({"font.size": 8})
fig, ax = plt.subplots(2, 2, figsize=(7.5, 5.4))
# (a) review length
ax[0, 0].hist(R.words.clip(upper=300), bins=60, color="#3b6ea5")
ax[0, 0].axvline(R.words.median(), color="k", ls="--", lw=1)
ax[0, 0].set(title=f"(a) Review length (median {R.words.median():.0f} words)", xlabel="words (clipped at 300)", ylabel="reviews")
# (b) reviews per listing
rpl = R.groupby(["city", "listing_id"]).size()
ax[0, 1].hist(np.log10(rpl), bins=40, color="#c97b3a")
ax[0, 1].set(title="(b) Reviews per listing (long tail)", xlabel="log10(reviews per listing)", ylabel="listings")
# (c) price per city
data = [L[(L.city == c) & (L.price > 0) & (L.price < 1500)].price for c in CITIES]
ax[1, 0].boxplot(data, tick_labels=[c.replace("-county", "").replace("new-orleans", "NOLA") for c in CITIES], showfliers=False)
ax[1, 0].set(title="(c) Nightly price by city ($)", ylabel="USD")
ax[1, 0].tick_params(axis="x", rotation=40)
# (d) atmosphere terms
ts = sorted(term_pct.items(), key=lambda x: x[1])
ax[1, 1].barh([t for t, _ in ts], [v for _, v in ts], color="#5a9e6f")
ax[1, 1].set(title="(d) Atmosphere terms in reviews", xlabel="% of reviews")
plt.tight_layout()
plt.savefig(FIG / "checkpoint1.png", dpi=200)

# Weather figure (optional extra)
if weather:
    plt.figure(figsize=(4, 2.6))
    for c, v in weather.items():
        plt.plot(range(1, 13), v, label=c)
    plt.legend(fontsize=5); plt.xlabel("month"); plt.ylabel("mean temp (F)"); plt.title("Open-Meteo seasonal temperature")
    plt.tight_layout(); plt.savefig(FIG / "weather.png", dpi=200)
