import argparse
import json
import os
from typing import Any, Dict, List


def load_places(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def places_to_geojson(places: List[Dict[str, Any]]) -> Dict[str, Any]:
    features = []
    for place in places:
        lat = place.get("lat")
        lng = place.get("lng")
        if lat is None or lng is None:
            continue
        properties = {k: v for k, v in place.items() if k not in ("lat", "lng")}
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [lng, lat],
            },
            "properties": properties,
        }
        features.append(feature)
    return {
        "type": "FeatureCollection",
        "features": features,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert amenities output JSON to WGS84 GeoJSON."
    )
    parser.add_argument(
        "--input",
        "-i",
        default=os.path.join("output", "amenities_beer_sheva.json"),
        help="Input JSON file produced by fetch_places.py",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=os.path.join("output", "amenities_beer_sheva.geojson"),
        help="Output GeoJSON file path",
    )
    args = parser.parse_args()

    places = load_places(args.input)
    geojson = places_to_geojson(places)

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(geojson, f, ensure_ascii=False, indent=2)

    print(f"Converted {len(geojson['features'])} places to GeoJSON.")
    print(f"Saved: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

