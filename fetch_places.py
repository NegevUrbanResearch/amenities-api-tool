"""
Fetch Google Places in Beer Sheva, Israel via Places API (Legacy) and save as a dataset.
Uses Nearby Search with multiple place types, pagination, and deduplication by place_id.
"""
import csv
import json
import os
import time
from urllib.parse import urlencode

import requests

BEER_SHEVA_LAT = 31.2518
BEER_SHEVA_LNG = 34.7913
RADIUS_M = 25000  # 15 km + 10 km buffer
BASE_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

# All place types from Table 1 (searchable in Nearby Search)
# https://developers.google.com/maps/documentation/places/web-service/supported_types
PLACE_TYPES = [
    "accounting", "airport", "amusement_park", "aquarium", "art_gallery", "atm",
    "bakery", "bar", "bank", "beauty_salon", "bicycle_store", "book_store",
    "bowling_alley", "bus_station", "cafe", "campground", "car_dealer",
    "car_rental", "car_repair", "car_wash", "casino", "cemetery", "church",
    "city_hall", "clothing_store", "convenience_store", "courthouse", "dentist",
    "department_store", "doctor", "drugstore", "electrician", "electronics_store",
    "embassy", "fire_station", "florist", "funeral_home", "furniture_store",
    "gas_station", "gym", "hair_care", "hardware_store", "hindu_temple",
    "home_goods_store", "hospital", "insurance_agency", "jewelry_store", "laundry",
    "lawyer", "library", "light_rail_station", "liquor_store",
    "local_government_office", "locksmith", "lodging", "meal_delivery",
    "meal_takeaway", "mosque", "movie_rental", "movie_theater", "moving_company",
    "museum", "night_club", "painter", "park", "parking", "pet_store",
    "pharmacy", "physiotherapist", "plumber", "police", "post_office",
    "primary_school", "real_estate_agency", "restaurant", "roofing_contractor",
    "rv_park", "school", "secondary_school", "shoe_store", "shopping_mall",
    "spa", "stadium", "storage", "store", "subway_station", "supermarket",
    "synagogue", "taxi_stand", "tourist_attraction", "train_station",
    "transit_station", "travel_agency", "university", "veterinary_care", "zoo",
]
# Search with no type filter to catch uncategorized places
PLACE_TYPES.append(None)


def nearby_search(api_key: str, lat: float, lng: float, radius: int, place_type: str = None, page_token: str = None) -> dict:
    params = {
        "location": f"{lat},{lng}",
        "radius": radius,
        "key": api_key,
        "language": "en",
    }
    if place_type:
        params["type"] = place_type
    if page_token:
        params["pagetoken"] = page_token
    r = requests.get(BASE_URL, params=params, timeout=15)
    r.raise_for_status()
    return r.json()


def flatten_place(place: dict) -> dict:
    loc = place.get("geometry", {}).get("location", {})
    return {
        "place_id": place.get("place_id"),
        "name": place.get("name"),
        "types": "|".join(place.get("types", [])),
        "vicinity": place.get("vicinity") or place.get("formatted_address", ""),
        "lat": loc.get("lat"),
        "lng": loc.get("lng"),
        "rating": place.get("rating"),
        "user_ratings_total": place.get("user_ratings_total"),
        "business_status": place.get("business_status"),
        "price_level": place.get("price_level"),
    }


def fetch_all_places(api_key: str, output_dir: str = ".") -> list[dict]:
    seen_ids = set()
    results = []
    csv_path = os.path.join(output_dir, "amenities_beer_sheva.csv")
    json_path = os.path.join(output_dir, "amenities_beer_sheva.json")

    for i, place_type in enumerate(PLACE_TYPES):
        page_token = None
        page = 0
        label = place_type or "all"
        print(f"[{i+1}/{len(PLACE_TYPES)}] type={label}", end=" ")
        type_count = 0
        while True:
            try:
                data = nearby_search(
                    api_key,
                    BEER_SHEVA_LAT,
                    BEER_SHEVA_LNG,
                    RADIUS_M,
                    place_type=place_type,
                    page_token=page_token,
                )
            except requests.RequestException as e:
                print(f" error: {e}")
                break
            status = data.get("status")
            if status == "ZERO_RESULTS":
                print("0")
                break
            if status != "OK":
                print(f" status={status}")
                break
            for place in data.get("results", []):
                pid = place.get("place_id")
                if pid and pid not in seen_ids:
                    seen_ids.add(pid)
                    flat = flatten_place(place)
                    flat["search_type"] = place_type or "all"
                    results.append(flat)
                    type_count += 1
            page_token = data.get("next_page_token")
            if not page_token:
                print(type_count)
                break
            page += 1
            time.sleep(2)
        time.sleep(0.2)

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        if results:
            w = csv.DictWriter(f, fieldnames=results[0].keys())
            w.writeheader()
            w.writerows(results)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"Total unique places: {len(results)}")
    print(f"Saved: {csv_path}, {json_path}")
    return results


def main():
    api_key = os.environ.get("GOOGLE_PLACES_API_KEY")
    if not api_key:
        print("Set GOOGLE_PLACES_API_KEY in your environment.")
        print("Get a key: https://console.cloud.google.com/apis/credentials")
        print("Enable: Places API (and optionally Places API (New))")
        return 1
    fetch_all_places(api_key)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
