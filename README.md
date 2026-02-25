# Google Places (New) → Beer Sheva Amenities

Fetches Google Places (New) Nearby Search for Beer Sheva, Israel and visualizes the search area on a map.

## What it does

- **fetch_places.py** — Runs Nearby Search per place type (restaurant, cafe, pharmacy, etc.), paginates, deduplicates by `place_id`, and writes CSV + JSON to `output/`
- **visualize_area.py** — Builds a Folium map of the search area; overlays places if `output/amenities_beer_sheva.json` exists
- **convert_to_geojson.py** — Converts `output/amenities_beer_sheva.json` to WGS84 GeoJSON `FeatureCollection` at `output/amenities_beer_sheva.geojson`

## Setup

1. **API key**
   - Create one at [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
   - Enable **Places API (New)** for the project (`places.googleapis.com`)
   - Restrict the key to Places API (New) and your IP

2. **Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your key
   ```

## Run

```bash
python fetch_places.py
python visualize_area.py
python convert_to_geojson.py
```

Outputs: `output/amenities_beer_sheva.csv`, `output/amenities_beer_sheva.json`, `output/amenities_beer_sheva.geojson`, `output/search_area.html`

## Cost

Places API (New) Nearby Search is billed per request.

- **Free tier**: The first **10,000 requests per month are free**.
- **After free tier**: Pricing is per 1K requests with volume discounts (see Google Maps Platform pricing page for current ILS rates).
- One full run of this script does roughly `(place types) × (1–3 requests per type)`, so edit `PLACE_TYPES` in `fetch_places.py` to control usage.
