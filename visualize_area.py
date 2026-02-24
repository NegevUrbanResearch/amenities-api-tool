"""
Visualize the Places API search area (Beer Sheva + buffer) with Folium.
Optionally overlays places from amenities_beer_sheva.json if it exists.
"""
import json
import os

import folium
from folium import Circle, Marker

BEER_SHEVA_LAT = 31.2148
BEER_SHEVA_LNG = 34.8428
RADIUS_M = 16500

RAHAT_LAT = 31.39250
RAHAT_LNG = 34.75444
RAHAT_RADIUS_M = 10000

OFAKIM_LAT = 31.317
OFAKIM_LNG = 34.617
OFAKIM_RADIUS_M = 10000
OUTPUT_DIR = "output"
JSON_PATH = os.path.join(OUTPUT_DIR, "amenities_beer_sheva.json")
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "search_area.html")


def create_map(places: list[dict] | None = None) -> folium.Map:
    m = folium.Map(
        location=[BEER_SHEVA_LAT, BEER_SHEVA_LNG],
        zoom_start=11,
        tiles="OpenStreetMap",
    )
    Circle(
        location=[BEER_SHEVA_LAT, BEER_SHEVA_LNG],
        radius=RADIUS_M,
        color="#3388ff",
        fill=True,
        fill_color="#3388ff",
        fill_opacity=0.2,
        popup=f"Beer Sheva radius: {RADIUS_M / 1000:.0f} km",
    ).add_to(m)
    Marker(
        location=[BEER_SHEVA_LAT, BEER_SHEVA_LNG],
        popup="Beer Sheva (center)",
        icon=folium.Icon(color="red", icon="info-sign"),
    ).add_to(m)
    Circle(
        location=[RAHAT_LAT, RAHAT_LNG],
        radius=RAHAT_RADIUS_M,
        color="#ff7800",
        fill=True,
        fill_color="#ff7800",
        fill_opacity=0.15,
        popup=f"Rahat radius: {RAHAT_RADIUS_M / 1000:.0f} km",
    ).add_to(m)
    Marker(
        location=[RAHAT_LAT, RAHAT_LNG],
        popup="Rahat (center)",
        icon=folium.Icon(color="green", icon="info-sign"),
    ).add_to(m)
    Circle(
        location=[OFAKIM_LAT, OFAKIM_LNG],
        radius=OFAKIM_RADIUS_M,
        color="#8000ff",
        fill=True,
        fill_color="#8000ff",
        fill_opacity=0.15,
        popup=f"Ofakim radius: {OFAKIM_RADIUS_M / 1000:.0f} km",
    ).add_to(m)
    Marker(
        location=[OFAKIM_LAT, OFAKIM_LNG],
        popup="Ofakim (center)",
        icon=folium.Icon(color="blue", icon="info-sign"),
    ).add_to(m)
    if places:
        for p in places:
            lat, lng = p.get("lat"), p.get("lng")
            if lat is not None and lng is not None:
                folium.CircleMarker(
                    location=[lat, lng],
                    radius=4,
                    color="#e74c3c",
                    fill=True,
                    fill_color="#e74c3c",
                    popup=f"{p.get('name', '')}",
                ).add_to(m)
    return m


def main():
    places = None
    if os.path.exists(JSON_PATH):
        with open(JSON_PATH, encoding="utf-8") as f:
            places = json.load(f)
        print(f"Loaded {len(places)} places from {JSON_PATH}")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    m = create_map(places)
    m.save(OUTPUT_PATH)
    print(f"Saved: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
