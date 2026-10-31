# Vacation Finder — Checkpoint 1: Data
Dinidu Samaranayake and Oliver Hankins

## Data collected so far

| Source | How collected | Size |
|---|---|---|
| Inside Airbnb (listings + reviews), 7 vacation-oriented regions: Austin, San Diego, Hawaii, Asheville, New Orleans, Bozeman, Broward Co. (FL); Sept 2026 snapshots | Downloaded via Python script (`scripts/collect_airbnb.py`) | 91,483 listings; 4.87M reviews; 215M review words |
| Open-Meteo Historical Weather API | Python script queries daily mean temperature (2025) at each region's listing centroid, aggregated to monthly averages | 7 regions x 12 months |
| *Planned:* TripAdvisor Hotel & Resort Reviews (Kaggle), Nominatim geocoding / driving distance | Next checkpoint | — |

Each listing has a free-text description, an amenities list, latitude/longitude, nightly price, and a review rating. 99.9% of listings have a description, 90.1% have a price, and 72,824 (80%) have at least one review. Median nightly price is about $288 (Hawaii is the most expensive region, New Orleans the cheapest).

## Key characteristics (see figure)

[INSERT figures/checkpoint1.png]

- **(a) Reviews are short.** The median review is 31 words, and the distribution is heavily right-skewed. A single review rarely carries enough text to match a long natural-language query, so we will aggregate reviews and the description into one document per listing/destination before indexing with BM25.
- **(b) Review counts are long-tailed.** Many listings have only 1–3 reviews while others have over 1,000. We will normalize document length (BM25 `b` parameter) and cap or weight by review count so heavily reviewed listings do not dominate.
- **(c) Prices vary widely by region.** Price differs by region and has a long tail, so price caps ("under $150/night") will be a metadata filter/multiplier in the hybrid ranker, not part of text matching.
- **(d) Atmosphere language appears in the reviews.** In a 350k-review sample, "quiet" (10%), "beach" (10%), "cozy" (6%) and "family" (5%) are common, while "nightlife," "romantic," and "crowded" are rare. This supports our atmosphere lexicon and query expansion, and shows that rare terms need semantic (embedding) matching to be found.

## Data processing
Reviews were joined to listings by listing ID and regions were tagged. Prices were parsed from strings to numeric values, and missing review text was treated as empty. Reviews are kept in all languages for now, and we plan to filter to English before computing embeddings. Next steps: add the TripAdvisor data, geocode destinations with Nominatim, build the aggregated destination corpus, and begin the BM25 baseline for Checkpoint 2.

Code and scripts: github.com/<your-repo>
