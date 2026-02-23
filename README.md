# Google Places → Beer Sheva Amenities

Fetches Google Places (Legacy) Nearby Search for Beer Sheva, Israel and visualizes the search area on a map.

## What it does

- **fetch_places.py** — Runs Nearby Search per place type (restaurant, cafe, pharmacy, etc.), paginates, deduplicates by `place_id`, and writes CSV + JSON to `output/`
- **visualize_area.py** — Builds a Folium map of the search area; overlays places if `output/amenities_beer_sheva.json` exists

## Setup

1. **API key**
   - Create one at [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
   - Enable **Places API** (Legacy) for the project
   - Restrict the key to Places API and your IP

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
```

Outputs: `output/amenities_beer_sheva.csv`, `output/amenities_beer_sheva.json`, `output/search_area.html`

## Cost

Places API (Legacy) is billed per request. One run does roughly `(place types) × (1–3 requests per type)`. Edit `PLACE_TYPES` in `fetch_places.py` to reduce scope.
