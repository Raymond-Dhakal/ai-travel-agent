import streamlit as st
from agent import run_travel_agent

st.set_page_config(page_title="AI Travel Agent")

st.title("AI Travel Planner")

user_query = st.text_area(
    "Enter your travel request:",
    placeholder="Example: Plan a 5-day budget trip to Paris focused on food and history"
)

if st.button("Generate Itinerary"):
    if user_query.strip() == "":
        st.warning("Please enter a travel request.")
    else:
        with st.spinner("Planning your trip..."):
            result = run_travel_agent(user_query)
            st.subheader("Your Travel Plan")
            st.write(result)
