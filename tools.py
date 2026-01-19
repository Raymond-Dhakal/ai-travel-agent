
def estimate_budget_for_trip(city: str, days: int, travelers: int = 1, travel_style: str = "standard") -> dict:
    
   
    style_map = {
        "budget": 50.0,
        "standard": 100.0,
        "luxury": 200.0,
    }
    per_person_per_day = style_map.get(travel_style.lower(), 100.0)

    daily_total = per_person_per_day * travelers
    estimated_total = daily_total * max(1, int(days))

    
    breakdown = {
        "lodging": round(daily_total * 0.6, 2),
        "food": round(daily_total * 0.25, 2),
        "transport": round(daily_total * 0.1, 2),
        "activities": round(daily_total * 0.04, 2),
        "other": round(daily_total * 0.01, 2),
    }

    assumptions = [
        f"avg per-person per-day base ${per_person_per_day:.2f} for travel style '{travel_style}'",
        "lodging ~60% of daily cost, food ~25%",
    ]

    return {
        "success": True,
        "city": city,
        "days": days,
        "travelers": travelers,
        "travel_style": travel_style,
        "daily_estimate_usd": round(daily_total, 2),
        "breakdown": breakdown,
        "estimated_total_usd": round(estimated_total, 2),
        "assumptions": assumptions,
    }


def get_attractions(city: str, interest: str) -> list:
    
    attractions_data = {
        "paris": {
            "food": ["Local Cafes", "Food Markets", "Bakeries"],
            "history": ["Louvre Museum", "Notre Dame", "Versailles"],
            "nature": ["Luxembourg Gardens", "Seine River Walk"],
            "shopping": ["Champs-Élysées", "Le Marais"]
        },
        "rome": {
            "history": ["Colosseum", "Roman Forum", "Pantheon"],
            "food": ["Italian Trattorias", "Pizza Streets"],
            "nature": ["Villa Borghese"],
            "shopping": ["Via del Corso"]
        }
    }

    city_key = (city or "").strip().lower()
    interest_key = (interest or "").strip().lower()

    raw_list = attractions_data.get(city_key, {}).get(interest_key, [])

    
    pois = []
    for idx, name in enumerate(raw_list):
        poi = {
            "id": f"local-{city_key}-{interest_key}-{idx}",
            "name": name,
            "category": interest_key,
            "lat": None,
            "lon": None,
            "address": None,
            "estimated_duration_mins": 90,  
            "estimated_cost_usd": None,
            "notes": None,
            "source": "local-fallback",
        }
        pois.append(poi)

    return pois


def build_itinerary(days: int, attractions: list) -> list:
    
    itinerary = []
    if not isinstance(days, int) or days < 1:
        days = 1

    pois = list(attractions or [])
    poi_index = 0

    activities_per_day = 2
    day_start_hour = 9  

    for day in range(1, days + 1):
        day_plan = {
            "day": day,
            "summary": None,
            "day_estimated_cost_usd": 0.0,
            "activities": []
        }

        for slot in range(activities_per_day):
            if poi_index >= len(pois):
                break
            poi = pois[poi_index]
        
            start_hour = day_start_hour + slot * 3  
            start_time = f"{start_hour:02d}:00"
            end_time = f"{min(start_hour + 2, 23):02d}:00"

            activity = {
                "id": poi.get("id"),
                "title": poi.get("name"),
                "type": poi.get("category"),
                "start_time": start_time,
                "end_time": end_time,
                "lat": poi.get("lat"),
                "lon": poi.get("lon"),
                "address": poi.get("address"),
                "estimated_cost_usd": poi.get("estimated_cost_usd"),
                "notes": poi.get("notes"),
                "source": poi.get("source"),
            }

            
            cost = activity.get("estimated_cost_usd")
            if isinstance(cost, (int, float)):
                day_plan["day_estimated_cost_usd"] += float(cost)

            day_plan["activities"].append(activity)
            poi_index += 1

    
        titles = [a.get("title") for a in day_plan["activities"] if a.get("title")]
        if titles:
            day_plan["summary"] = " / ".join(titles)
        else:
            day_plan["summary"] = "Free / unplanned"

    
        day_plan["day_estimated_cost_usd"] = round(day_plan["day_estimated_cost_usd"], 2)
        itinerary.append(day_plan)

    return itinerary

