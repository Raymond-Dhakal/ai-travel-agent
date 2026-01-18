
def estimate_budget(days: int, travel_style: str = "standard"):
    """
    Estimates budget based on number of days and travel style.

    If travel_style is not provided, defaults to 'standard'.
    """
    if travel_style == "budget":
        return days * 50
    elif travel_style == "luxury":
        return days * 200
    else:
        return days * 100


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

    city = city.lower()
    interest = interest.lower()

    return attractions_data.get(city, {}).get(interest, [])


def build_itinerary(days: int, attractions: list) -> list:
    
    itinerary = []
    attraction_index = 0

    for day in range(1, days + 1):
        day_plan = {
            "day": day,
            "activities": []
        }

        for _ in range(2):
            if attraction_index < len(attractions):
                day_plan["activities"].append(attractions[attraction_index])
                attraction_index += 1

        itinerary.append(day_plan)

    return itinerary
