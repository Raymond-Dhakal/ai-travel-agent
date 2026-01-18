import streamlit as st
from datetime import datetime, timedelta
import json
from agent import run_travel_agent

st.set_page_config(page_title="AI Travel Agent", layout="wide")
st.title("AI Travel Planner")


if "plans" not in st.session_state:
    st.session_state.plans = []  

if "last_prompt" not in st.session_state:
    st.session_state.last_prompt = None
if "last_result" not in st.session_state:
    st.session_state.last_result = None


with st.sidebar:
    st.header("Quick Settings")
    
    if "travel_style" not in st.session_state:
        st.session_state.travel_style = "Budget"
    if "travelers" not in st.session_state:
        st.session_state.travelers = 1
    travel_style = st.selectbox("Travel style", ["Budget", "Comfort", "Luxury"], index=["Budget","Comfort","Luxury"].index(st.session_state.travel_style), key="travel_style")
    travelers = st.number_input("Number of travelers", min_value=1, max_value=20, value=st.session_state.travelers, key="travelers")
    example = st.selectbox(
        "Choose an example request",
        [
            "—",
            "5-day budget trip to Paris focused on food and history",
            "Weekend nature escape near San Francisco for two, hiking and relaxation",
            "10-day luxury family vacation in Japan with kid-friendly activities"
        ],
    )
    if st.button("Use example"):
        if example != "—":
          
            st.session_state.destination = example
            st.session_state.interests = ["Food", "History"]
            st.session_state.must_see = ""
            st.session_state.avoid = ""
            st.session_state.start_date = datetime.today().date()
            st.session_state.end_date = (datetime.today() + timedelta(days=5)).date()
            st.session_state.budget = 800
            st.session_state.pace = "Balanced"
            st.session_state.extra_notes = ""
            st.success("Example loaded into the form — adjust any fields and click Generate Itinerary.")


with st.form("travel_form"):
    col1, col2 = st.columns([2, 1])
    with col1:
        destination = st.text_input(
            "Destination (city or country)",
            value=st.session_state.get("destination", ""),
            placeholder="e.g., Paris, France",
            key="destination",
        )
        interests = st.multiselect(
            "Interests (choose up to 5)",
            ["Food", "History", "Museums", "Nightlife", "Nature", "Hiking", "Beaches", "Family", "Romance", "Shopping"],
            default=st.session_state.get("interests", ["Food", "History"]),
            key="interests",
        )
        must_see = st.text_input("Must-see / must-do (optional)", value=st.session_state.get("must_see", ""), placeholder="E.g., Louvre, Eiffel Tower", key="must_see")
        avoid = st.text_input("Avoid (optional)", value=st.session_state.get("avoid", ""), placeholder="E.g., long walks, museums", key="avoid")
    with col2:
      
        start_date = st.date_input("Start date", value=st.session_state.get("start_date", datetime.today().date()), key="start_date")
        end_date = st.date_input("End date", value=st.session_state.get("end_date", (datetime.today() + timedelta(days=5)).date()), key="end_date")
        if end_date < start_date:
            st.warning("End date is before start date — we'll use duration instead.")
        budget = st.slider("Budget per person (USD)", min_value=50, max_value=10000, value=st.session_state.get("budget", 800), step=10, key="budget")
        pace = st.radio("Travel pace", ["Relaxed", "Balanced", "Packed"], index=["Relaxed","Balanced","Packed"].index(st.session_state.get("pace", "Balanced")), key="pace")

    extra_notes = st.text_area("Extra notes / constraints", value=st.session_state.get("extra_notes", ""), placeholder="e.g., wheelchair accessible, vegetarian food only", key="extra_notes")
    submit = st.form_submit_button("Generate Itinerary")


def build_prompt():
    parts = []
    if destination:
        parts.append(f"Destination: {destination}")
    duration_days = (end_date - start_date).days + 1
    parts.append(f"Dates: {start_date.isoformat()} to {end_date.isoformat()} ({duration_days} days)")
    parts.append(f"Travelers: {travelers}")
    parts.append(f"Style: {travel_style} / Pace: {pace}")
    parts.append(f"Budget per person (USD): {budget}")
    if interests:
        parts.append("Interests: " + ", ".join(interests))
    if must_see:
        parts.append(f"Must-see: {must_see}")
    if avoid:
        parts.append(f"Avoid: {avoid}")
    if extra_notes:
        parts.append(f"Constraints or extra notes: {extra_notes}")
    parts.append("Please produce a daily itinerary with transport suggestions, approximate cost breakdown, recommended restaurants or activities, and alternative options. Also include packing tips and links to useful maps/booking pages if possible.")
    return "\n\n".join(parts)


if submit:
    if not destination or destination.strip() == "":
        st.error("Please enter a destination.")
    elif end_date < start_date:

        st.error("Please fix the dates (end date must be same or after start date).")
    else:
        prompt = build_prompt()
        st.session_state.last_prompt = prompt

        with st.spinner("Planning your trip..."):
            try:
                result = run_travel_agent(prompt)
            except Exception as e:
                st.error(f"Agent returned an error: {e}")
                result = None

        if result:
            entry = {
                "id": len(st.session_state.plans) + 1,
                "query": prompt,
                "result": result,
                "meta": {
                    "destination": destination,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "budget": budget,
                    "travelers": travelers,
                },
            }
            st.session_state.plans.append(entry)
            st.session_state.last_result = entry


st.markdown("---")
st.header("Latest Plan")
if st.session_state.last_result:
    plan = st.session_state.last_result
    st.subheader(f"Trip to {plan['meta']['destination']} ({plan['meta']['start_date']} → {plan['meta']['end_date']})")
    st.write(plan["result"])
    coldl, coldr = st.columns([3,1])
    with coldr:
        
        st.download_button("Download JSON", data=json.dumps(plan, indent=2), file_name=f"itinerary_{plan['id']}.json")
        st.download_button("Download text", data=plan["result"], file_name=f"itinerary_{plan['id']}.txt")

   
    st.markdown("### Refine this plan")
    followup = st.text_input("Ask a follow-up (e.g., 'Make it cheaper', 'Add more family activities')", key="followup_input")
    if st.button("Send follow-up"):
        if followup.strip():
            combined_prompt = plan["query"] + "\n\nUser follow-up: " + followup
            with st.spinner("Updating plan..."):
                try:
                    updated = run_travel_agent(combined_prompt)
                except Exception as e:
                    st.error(f"Agent returned an error: {e}")
                    updated = None
            if updated:
              
                new_entry = {
                    "id": len(st.session_state.plans) + 1,
                    "query": combined_prompt,
                    "result": updated,
                    "meta": {**plan["meta"], "refined_from": plan["id"], "followup": followup},
                }
                st.session_state.plans.append(new_entry)
                st.session_state.last_result = new_entry
                st.success("Plan updated — see the Latest Plan section below.")

else:
    st.info("No itinerary generated yet — fill the form above and click Generate Itinerary.")


st.markdown("---")
st.header("Saved Plans")
if st.session_state.plans:
    for p in reversed(st.session_state.plans):
        with st.expander(f"#{p['id']} — {p['meta'].get('destination','Unknown')} ({p['meta'].get('start_date')})", expanded=False):
            st.write(p["result"])
            st.write("Meta:", p["meta"])
else:
    st.write("No saved plans yet.")


st.sidebar.markdown("---")
if st.sidebar.button("Clear saved plans"):
    st.session_state.plans = []
    st.success("Cleared saved plans.")