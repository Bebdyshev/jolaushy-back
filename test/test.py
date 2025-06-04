from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search
from google.genai import types

agent = Agent(
    name="hotel_search_agent",
    model="gemini-2.0-flash",
    description="Find hotels in a specified city for given dates.",
    instruction="When the user asks for hotels, use google_search to find options.",
    tools=[google_search]
)

session_service = InMemorySessionService()
session = session_service.create_session(
    app_name="jolaushy",
    user_id="user123",
    session_id="session1"
)
runner = Runner(agent=agent, app_name="jolaushy", session_service=session_service)

def search_hotels(location, start_date, end_date):
    query = f"Find me a hotel in {location} from {start_date} to {end_date}"
    content = types.Content(role="user", parts=[types.Part(text=query)])
    for event in runner.run(user_id="user123", session_id="session1", new_message=content):
        if event.is_final_response():
            return event.content.parts[0].text
    return "No response from agent."

print(search_hotels("Astana", "2025-06-10", "2025-06-12"))
