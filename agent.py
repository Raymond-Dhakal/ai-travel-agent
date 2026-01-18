from langchain_google_genai import ChatGoogleGenerativeAI

from prompts import (
    SYSTEM_PROMPT,
    OUTPUT_FORMAT_PROMPT
)

llm = ChatGoogleGenerativeAI(
    model="models/gemini-flash-latest",
    temperature=0.3,
    convert_system_message_to_human=True
)
def run_travel_agent(user_query: str):
    prompt = f"""
{SYSTEM_PROMPT}

User request:
{user_query}

You MUST strictly follow this output format:
{OUTPUT_FORMAT_PROMPT}
"""

    response = llm.invoke(prompt)
    return response.content


if __name__ == "__main__":
    query = "Plan a 5-day budget trip to Paris focused on food"
    print(run_travel_agent(query))
