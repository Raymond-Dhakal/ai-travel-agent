from langchain_google_genai import ChatGoogleGenerativeAI
from prompts import SYSTEM_PROMPT, REASONING_PROMPT, TOOL_USAGE_PROMPT, OUTPUT_FORMAT_PROMPT
import json
import re

from tools import estimate_budget_for_trip, get_attractions, build_itinerary


llm = ChatGoogleGenerativeAI(
    model="models/gemini-flash-latest",
    temperature=0.3,
    convert_system_message_to_human=True,
)

def _simple_extract(query: str):
   
    out = {
        "destination": None,
        "days": None,
        "travelers": 1,
        "travel_style": None,
        "interests": [],
    }
    q = (query or "").lower()


    m = re.search(r"\b(?:to|in)\s+([a-z ]+?)(?:\s+for\b|\s+focused|\s*,|$)", q)
    if m:
        out["destination"] = m.group(1).strip()


    m = re.search(r"(\d+)\s*-?\s*day", q)
    if m:
        out["days"] = int(m.group(1))
    else:
        m2 = re.search(r"for\s+(\d+)\s+days", q)
        if m2:
            out["days"] = int(m2.group(1))


    m = re.search(r"for\s+(\d+)\s+(?:people|persons|travelers|travellers)", q)
    if m:
        out["travelers"] = int(m.group(1))


    if "budget" in q or "cheap" in q:
        out["travel_style"] = "budget"
    elif "luxury" in q:
        out["travel_style"] = "luxury"
    elif "comfort" in q:
        out["travel_style"] = "standard"


    for keyword in [
        "food", "history", "museums", "nature",
        "hiking", "beaches", "shopping", "nightlife"
    ]:
        if keyword in q:
            out["interests"].append(keyword)


    if out["days"] is None:
        out["days"] = 3

    return out


def run_travel_agent(user_query: str):
    
    parsed = _simple_extract(user_query)

    destination = parsed["destination"]
    days = parsed["days"]
    travelers = parsed["travelers"]
    travel_style = parsed["travel_style"] or "standard"
    interests = parsed["interests"] or ["food"]

    pois = []
    if destination:
        for interest in interests[:3]:
            pois.extend(get_attractions(destination, interest))
    pois = pois[:12]

    
    budget = estimate_budget_for_trip(
        destination or "unknown",
        days,
        travelers,
        travel_style
    )
    
    draft_itinerary = build_itinerary(days, pois)
    evidence = {
        "destination": destination,
        "days": days,
        "travelers": travelers,
        "travel_style": travel_style,
        "interests": interests,
        "pois_sample": pois,
        "budget_estimate": budget,
        "draft_itinerary": draft_itinerary,
    }
    prompt = f"""
    {SYSTEM_PROMPT}

    {REASONING_PROMPT}

    {TOOL_USAGE_PROMPT}

    User request:
    {user_query}

    Evidence (JSON):
    {json.dumps(evidence)}

    Using ONLY the evidence above, produce the final itinerary.
    Follow the output format exactly:

    {OUTPUT_FORMAT_PROMPT}
"""


    response = llm.invoke(prompt)
    raw = response.content

    if isinstance(raw, (dict, list)):
        return json.dumps(raw, indent=2)
    return str(raw)


if __name__ == "__main__":
    query = "Plan a 7-day luxury trip to Tokyo for 2 people"
    print(run_travel_agent(query))
