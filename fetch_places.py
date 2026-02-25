"""
Fetch Google Places in Beer Sheva, Israel via Places API (New) and save as a dataset.
Uses Nearby Search with multiple place types, pagination, and deduplication by place_id.
"""
import csv
import json
import os
import time

import requests
from dotenv import load_dotenv

load_dotenv()


BEER_SHEVA_LAT = 31.2148
BEER_SHEVA_LNG = 34.8428
BEER_SHEVA_RADIUS_M = 16500

RAHAT_LAT = 31.39250
RAHAT_LNG = 34.75444
RAHAT_RADIUS_M = 10000

OFAKIM_LAT = 31.317
OFAKIM_LNG = 34.617
OFAKIM_RADIUS_M = 10000

SEARCH_AREAS = [
    ("beer_sheva", BEER_SHEVA_LAT, BEER_SHEVA_LNG, BEER_SHEVA_RADIUS_M),
    ("rahat", RAHAT_LAT, RAHAT_LNG, RAHAT_RADIUS_M),
    ("ofakim", OFAKIM_LAT, OFAKIM_LNG, OFAKIM_RADIUS_M),
]

BASE_URL = "https://places.googleapis.com/v1/places:searchNearby"

FIELD_MASK = "places.id,places.displayName,places.types,places.formattedAddress,places.location,places.businessStatus,places.rating,places.userRatingCount,places.priceLevel"

# Full Table A (Places API New) — every filterable place type for max coverage
# https://developers.google.com/maps/documentation/places/web-service/place-types
PLACE_TYPES = sorted({
    # Automotive
    "car_dealer", "car_rental", "car_repair", "car_wash", "ebike_charging_station",
    "electric_vehicle_charging_station", "gas_station", "parking", "parking_garage",
    "parking_lot", "rest_stop", "tire_shop", "truck_dealer",
    # Business
    "business_center", "corporate_office", "coworking_space", "farm", "manufacturer",
    "ranch", "supplier", "television_studio",
    # Culture
    "art_gallery", "art_museum", "art_studio", "auditorium", "castle", "cultural_landmark",
    "fountain", "historical_place", "history_museum", "monument", "museum",
    "performing_arts_theater", "sculpture",
    # Education
    "academic_department", "educational_institution", "library", "preschool",
    "primary_school", "research_institute", "school", "secondary_school", "university",
    # Entertainment and Recreation
    "adventure_sports_center", "amphitheatre", "amusement_center", "amusement_park",
    "aquarium", "banquet_hall", "barbecue_area", "botanical_garden", "bowling_alley",
    "casino", "childrens_camp", "city_park", "comedy_club", "community_center",
    "concert_hall", "convention_center", "cultural_center", "cycling_park", "dance_hall",
    "dog_park", "event_venue", "ferris_wheel", "garden", "go_karting_venue",
    "hiking_area", "historical_landmark", "indoor_playground", "internet_cafe", "karaoke",
    "live_music_venue", "marina", "miniature_golf_course", "movie_rental", "movie_theater",
    "national_park", "night_club", "observation_deck", "off_roading_area", "opera_house",
    "paintball_center", "park", "philharmonic_hall", "picnic_ground", "planetarium",
    "plaza", "roller_coaster", "skateboard_park", "state_park", "tourist_attraction",
    "video_arcade", "vineyard", "visitor_center", "water_park", "wedding_venue",
    "wildlife_park", "wildlife_refuge", "zoo",
    # Facilities
    "public_bath", "public_bathroom", "stable",
    # Finance
    "accounting", "atm", "bank",
    # Food and Drink
    "acai_shop", "afghani_restaurant", "african_restaurant", "american_restaurant",
    "argentinian_restaurant", "asian_fusion_restaurant", "asian_restaurant",
    "australian_restaurant", "austrian_restaurant", "bagel_shop", "bakery",
    "bangladeshi_restaurant", "bar", "bar_and_grill", "barbecue_restaurant",
    "basque_restaurant", "bavarian_restaurant", "beer_garden", "belgian_restaurant",
    "bistro", "brazilian_restaurant", "breakfast_restaurant", "brewery", "brewpub",
    "british_restaurant", "brunch_restaurant", "buffet_restaurant", "burmese_restaurant",
    "burrito_restaurant", "cafe", "cafeteria", "cajun_restaurant", "cake_shop",
    "californian_restaurant", "cambodian_restaurant", "candy_store", "cantonese_restaurant",
    "caribbean_restaurant", "cat_cafe", "chicken_restaurant", "chicken_wings_restaurant",
    "chilean_restaurant", "chinese_noodle_restaurant", "chinese_restaurant",
    "chocolate_factory", "chocolate_shop", "cocktail_bar", "coffee_roastery",
    "coffee_shop", "coffee_stand", "colombian_restaurant", "confectionery",
    "croatian_restaurant", "cuban_restaurant", "czech_restaurant", "danish_restaurant",
    "deli", "dessert_restaurant", "dessert_shop", "dim_sum_restaurant", "diner",
    "dog_cafe", "donut_shop", "dumpling_restaurant", "dutch_restaurant",
    "eastern_european_restaurant", "ethiopian_restaurant", "european_restaurant",
    "falafel_restaurant", "family_restaurant", "fast_food_restaurant", "filipino_restaurant",
    "fine_dining_restaurant", "fish_and_chips_restaurant", "fondue_restaurant",
    "food_court", "french_restaurant", "fusion_restaurant", "gastropub", "german_restaurant",
    "greek_restaurant", "gyro_restaurant", "halal_restaurant", "hamburger_restaurant",
    "hawaiian_restaurant", "hookah_bar", "hot_dog_restaurant", "hot_dog_stand",
    "hot_pot_restaurant", "hungarian_restaurant", "ice_cream_shop", "indian_restaurant",
    "indonesian_restaurant", "irish_pub", "irish_restaurant", "israeli_restaurant",
    "italian_restaurant", "japanese_curry_restaurant", "japanese_izakaya_restaurant",
    "japanese_restaurant", "juice_shop", "kebab_shop", "korean_barbecue_restaurant",
    "korean_restaurant", "latin_american_restaurant", "lebanese_restaurant", "lounge_bar",
    "malaysian_restaurant", "meal_delivery", "meal_takeaway", "mediterranean_restaurant",
    "mexican_restaurant", "middle_eastern_restaurant", "mongolian_barbecue_restaurant",
    "moroccan_restaurant", "noodle_shop", "north_indian_restaurant", "oyster_bar_restaurant",
    "pakistani_restaurant", "pastry_shop", "persian_restaurant", "peruvian_restaurant",
    "pizza_delivery", "pizza_restaurant", "polish_restaurant", "portuguese_restaurant",
    "pub", "ramen_restaurant", "restaurant", "romanian_restaurant", "russian_restaurant",
    "salad_shop", "sandwich_shop", "scandinavian_restaurant", "seafood_restaurant",
    "shawarma_restaurant", "snack_bar", "soul_food_restaurant", "soup_restaurant",
    "south_american_restaurant", "south_indian_restaurant", "southwestern_us_restaurant",
    "spanish_restaurant", "sports_bar", "sri_lankan_restaurant", "steak_house",
    "sushi_restaurant", "swiss_restaurant", "taco_restaurant", "taiwanese_restaurant",
    "tapas_restaurant", "tea_house", "tex_mex_restaurant", "thai_restaurant",
    "tibetan_restaurant", "tonkatsu_restaurant", "turkish_restaurant", "ukrainian_restaurant",
    "vegan_restaurant", "vegetarian_restaurant", "vietnamese_restaurant", "western_restaurant",
    "wine_bar", "winery", "yakiniku_restaurant", "yakitori_restaurant",
    # Geographical Areas
    "administrative_area_level_1", "administrative_area_level_2", "country", "locality",
    "postal_code", "school_district",
    # Government
    "city_hall", "courthouse", "embassy", "fire_station", "government_office",
    "local_government_office", "neighborhood_police_station", "police", "post_office",
    # Health and Wellness
    "chiropractor", "dental_clinic", "dentist", "doctor", "drugstore", "general_hospital",
    "hospital", "massage", "massage_spa", "medical_center", "medical_clinic", "medical_lab",
    "pharmacy", "physiotherapist", "sauna", "skin_care_clinic", "spa", "tanning_studio",
    "wellness_center", "yoga_studio",
    # Housing
    "apartment_building", "apartment_complex", "condominium_complex", "housing_complex",
    # Lodging
    "bed_and_breakfast", "budget_japanese_inn", "campground", "camping_cabin", "cottage",
    "extended_stay_hotel", "farmstay", "guest_house", "hostel", "hotel", "inn",
    "japanese_inn", "lodging", "mobile_home_park", "motel", "private_guest_room",
    "resort_hotel", "rv_park",
    # Natural Features
    "beach", "island", "lake", "mountain_peak", "nature_preserve", "river", "scenic_spot",
    "woods",
    # Places of Worship
    "buddhist_temple", "church", "hindu_temple", "mosque", "shinto_shrine", "synagogue",
    # Services
    "aircraft_rental_service", "association_or_organization", "astrologer", "barber_shop",
    "beautician", "beauty_salon", "body_art_service", "catering_service", "cemetery",
    "chauffeur_service", "child_care_agency", "consultant", "courier_service", "electrician",
    "employment_agency", "florist", "food_delivery", "foot_care", "funeral_home",
    "hair_care", "hair_salon", "insurance_agency", "laundry", "lawyer", "locksmith",
    "makeup_artist", "marketing_consultant", "moving_company", "nail_salon",
    "non_profit_organization", "painter", "pet_boarding_service", "pet_care", "plumber",
    "psychic", "real_estate_agency", "roofing_contractor", "service", "shipping_service",
    "storage", "summer_camp_organizer", "tailor", "telecommunications_service_provider",
    "tour_agency", "tourist_information_center", "travel_agency", "veterinary_care",
    # Shopping
    "asian_grocery_store", "auto_parts_store", "bicycle_store", "book_store",
    "building_materials_store", "butcher_shop", "cell_phone_store", "clothing_store",
    "convenience_store", "cosmetics_store", "department_store", "discount_store",
    "discount_supermarket", "electronics_store", "farmers_market", "flea_market",
    "food_store", "furniture_store", "garden_center", "general_store", "gift_shop",
    "grocery_store", "hardware_store", "health_food_store", "home_goods_store",
    "home_improvement_store", "hypermarket", "jewelry_store", "liquor_store", "market",
    "pet_store", "shoe_store", "shopping_mall", "sporting_goods_store", "sportswear_store",
    "store", "supermarket", "tea_store", "thrift_store", "toy_store", "warehouse_store",
    "wholesaler", "womens_clothing_store",
    # Sports
    "arena", "athletic_field", "fishing_charter", "fishing_pier", "fishing_pond",
    "fitness_center", "golf_course", "gym", "ice_skating_rink", "indoor_golf_course",
    "playground", "race_course", "ski_resort", "sports_activity_location", "sports_club",
    "sports_coaching", "sports_complex", "sports_school", "stadium", "swimming_pool",
    "tennis_court",
    # Transportation
    "airport", "airstrip", "bike_sharing_station", "bridge", "bus_station", "bus_stop",
    "ferry_service", "ferry_terminal", "heliport", "international_airport",
    "light_rail_station", "park_and_ride", "subway_station", "taxi_service", "taxi_stand",
    "toll_station", "train_station", "train_ticket_office", "tram_stop", "transit_depot",
    "transit_station", "transit_stop", "transportation_service", "truck_stop",
})
# Search with no type filter to catch uncategorized places
PLACE_TYPES = list(PLACE_TYPES) + [None]


def nearby_search(api_key: str, lat: float, lng: float, radius: int, place_type: str = None, page_token: str = None) -> dict:
    body = {
        "locationRestriction": {
            "circle": {
                "center": {"latitude": lat, "longitude": lng},
                "radius": float(radius),
            }
        },
        "maxResultCount": 20,
        "languageCode": "en",
    }
    if place_type:
        body["includedTypes"] = [place_type]
    if page_token:
        body["pageToken"] = page_token
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": FIELD_MASK,
    }
    r = requests.post(BASE_URL, json=body, headers=headers, timeout=15)
    r.raise_for_status()
    return r.json()


def flatten_place(place: dict) -> dict:
    loc = place.get("location") or {}
    display = place.get("displayName") or {}
    name = display.get("text") if isinstance(display, dict) else None
    return {
        "place_id": place.get("id"),
        "name": name,
        "types": "|".join(place.get("types", [])),
        "vicinity": place.get("formattedAddress") or "",
        "lat": loc.get("latitude"),
        "lng": loc.get("longitude"),
        "rating": place.get("rating"),
        "user_ratings_total": place.get("userRatingCount"),
        "business_status": place.get("businessStatus"),
        "price_level": place.get("priceLevel"),
    }


OUTPUT_DIR = "output"


def fetch_all_places(api_key: str, output_dir: str = OUTPUT_DIR) -> list[dict]:
    os.makedirs(output_dir, exist_ok=True)
    seen_ids = set()
    results = []
    request_count = 0
    csv_path = os.path.join(output_dir, "amenities_beer_sheva.csv")
    json_path = os.path.join(output_dir, "amenities_beer_sheva.json")

    for area_name, lat, lng, radius in SEARCH_AREAS:
        print(f"=== area={area_name} radius_km={radius/1000:.1f} ===")
        for i, place_type in enumerate(PLACE_TYPES):
            page_token = None
            page = 0
            label = place_type or "all"
            print(f"[{i+1}/{len(PLACE_TYPES)}] type={label}", end=" ")
            type_count = 0
            while True:
                last_error = None
                for attempt in range(3):
                    try:
                        data = nearby_search(
                            api_key,
                            lat,
                            lng,
                            radius,
                            place_type=place_type,
                            page_token=page_token,
                        )
                        break
                    except requests.RequestException as e:
                        last_error = e
                        resp = getattr(e, "response", None)
                        if resp is not None and resp.status_code == 403:
                            try:
                                err_json = resp.json()
                                msg = (err_json.get("error") or {}).get("message") or ""
                                if "has not been used" in msg or "disabled" in msg.lower():
                                    if attempt < 2:
                                        wait = 30 * (attempt + 1)
                                        print(f" 403 (propagation?), retry in {wait}s...", end=" ")
                                        time.sleep(wait)
                                        continue
                                    print(f" error: {e}")
                                    return results
                            except Exception:
                                pass
                        print(f" error: {e}")
                        if resp is not None:
                            try:
                                print(f" response body: {resp.text}")
                            except Exception:
                                pass
                        return results
                else:
                    print(f" error: {last_error}")
                    if getattr(last_error, "response", None) is not None:
                        try:
                            print(f" response body: {last_error.response.text}")
                        except Exception:
                            pass
                    return results
                request_count += 1
                places_batch = data.get("places", [])
                for place in places_batch:
                    pid = place.get("id")
                    if pid and pid not in seen_ids:
                        seen_ids.add(pid)
                        flat = flatten_place(place)
                        flat["search_type"] = place_type or "all"
                        results.append(flat)
                        type_count += 1
                page_token = data.get("nextPageToken")
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
    print(f"API requests used: {request_count}")
    print(f"Saved: {csv_path}, {json_path}")
    return results


def main():
    api_key = os.environ.get("GOOGLE_PLACES_API_KEY")
    if not api_key:
        print("Set GOOGLE_PLACES_API_KEY in .env")
        print("Get a key: https://console.cloud.google.com/apis/credentials")
        print("Enable: Places API (New)")
        return 1
    fetch_all_places(api_key)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
