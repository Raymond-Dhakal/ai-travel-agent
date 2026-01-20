# AI Travel Agent
An AI-powered travel planning assistant that generates structured travel itineraries from natural language input using an agent-based architecture.
The agent performs deterministic reasoning and tool-based planning (budget estimation, POI selection, itinerary construction), with an LLM used only for final synthesis and formatting.

## Features
1. Natural language trip planning
2. Agent-based reasoning and tool integration
3. Budget estimation and POI-based itineraries
4. Interactive Streamlit UI
5. Structured, readable output

## Tech Stack
Python
Streamlit
LangChain
Google Gemini (LLM)

## Project Structure
app.py        # Streamlit UI
agent.py      # Agent controller
tools.py      # Planning tools
prompts.py    # System and output prompts

## How to Run
1. pip install -r requirements.txt
2. streamlit run app.py