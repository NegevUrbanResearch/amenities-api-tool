Google Places → Beer Sheva amenities dataset
============================================

What this does
--------------
fetch_places.py calls the Google Places API (Legacy) Nearby Search for Beer Sheva, Israel.
It runs one search per place type (restaurant, cafe, pharmacy, etc.), paginates where
possible, deduplicates by place_id, and writes:
  - amenities_beer_sheva.csv
  - amenities_beer_sheva.json

Setup
-----
1. Get a Google Cloud API key:
   - Go to https://console.cloud.google.com/apis/credentials
   - Create an API key (or use existing).
   - Enable "Places API" for the project (Legacy; not only "Places API (New)").

2. Install dependencies:
   pip install -r requirements.txt

3. Set your API key (do not commit this):
   export GOOGLE_PLACES_API_KEY="your_key_here"

Run
---
  python fetch_places.py

Output is written in the current directory. The script uses a 15 km radius around
Beer Sheva center and a fixed list of amenity-related place types. Each type returns
up to 60 results (3 pages × 20); duplicates across types are removed by place_id.

Cost note: Places API (Legacy) is billed per request. One run does roughly
  (number of types) × (1–3 requests per type) requests. Restrict PLACE_TYPES
  in fetch_places.py if you want a smaller run.
