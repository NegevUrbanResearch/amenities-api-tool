"""
Visualize the Places API search area (Beer Sheva + buffer) with Folium.
Optionally overlays places from amenities_beer_sheva.json if it exists.
"""
import json
import os

import folium
from folium import Circle, Marker

BEER_SHEVA_LAT = 31.2518
BEER_SHEVA_LNG = 34.7913
RADIUS_M = 15000
OUTPUT_PATH = "search_area.html"


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
        popup=f"Search radius: {RADIUS_M / 1000:.0f} km",
    ).add_to(m)
    Marker(
        location=[BEER_SHEVA_LAT, BEER_SHEVA_LNG],
        popup="Beer Sheva (center)",
        icon=folium.Icon(color="red", icon="info-sign"),
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
    json_path = "amenities_beer_sheva.json"
    if os.path.exists(json_path):
        with open(json_path, encoding="utf-8") as f:
            places = json.load(f)
        print(f"Loaded {len(places)} places from {json_path}")
    m = create_map(places)
    m.save(OUTPUT_PATH)
    print(f"Saved: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
