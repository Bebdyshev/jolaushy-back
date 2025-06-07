from typing import List
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage
from langchain.tools import tool
from sqlalchemy.orm import Session
from datetime import datetime

load_dotenv()

global_db = None
global_roadmap_id = None

@tool
def find_tickets_tool(destination: str, start_date: str, end_date: str) -> str:
    """Find tickets for a given destination and date range. Logs to terminal when called."""
    print(f"[TOOL] find_tickets_tool called with: roadmap_id={global_roadmap_id}, destination={destination}, start_date={start_date}, end_date={end_date}")
    return f"Tickets found for {destination} from {start_date} to {end_date}."

@tool
def find_hotels_tool(destination: str, check_in_date: str, check_out_date: str, preference: str) -> str:
    """Find hotels for a given destination, date range, and preference. Logs to terminal when called."""
    print(f"[TOOL] find_hotels_tool called with: roadmap_id={global_roadmap_id}, destination={destination}, check_in_date={check_in_date}, check_out_date={check_out_date}, preference={preference}")
    return f"Hotel found in {destination} ({preference}) from {check_in_date} to {check_out_date}."

@tool
def find_activities_tool(destination: str, interests: list) -> str:
    """Find activities for a given destination and list of interests. Logs to terminal when called."""
    print(f"[TOOL] find_activities_tool called with: roadmap_id={global_roadmap_id}, destination={destination}, interests={interests}")
    return f"Activities found in {destination} for interests: {', '.join(interests)}."

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    roadmap_id: int

class ChatResponse(BaseModel):
    response: str

class AIAgent:
    def __init__(self):
        self.llm = ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=0.7,
            groq_api_key=os.environ.get("GROQ_API_KEY"),
        )
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a friendly and helpful travel planning assistant.\nYour goal is to help the user plan a trip by gathering their preferences step-by-step.\n\nAs soon as you have all the information needed for a planning step (like travel dates, hotel preferences, or interests), IMMEDIATELY use the appropriate tool. Do not wait for further user input if you can proceed.\n\nAfter using a tool, confirm with the user and ask for the next missing piece of information.\n\nIf you do not have enough information for a tool, ask the user a clear, specific question to get it.\n\nAlways be friendly and conversational.\n\nExample:\nUser: I want to go to Paris from July 10 to July 15.\nThought: I have the destination and dates. I should find tickets.\nAction: find_tickets_tool(destination='Paris', start_date='2024-07-10', end_date='2024-07-15')\nObservation: Tickets found for Paris from 2024-07-10 to 2024-07-15.\nFinal Answer: I found tickets for Paris from July 10 to July 15! Would you like to look for hotels next?\n\nBased on the user's request, you can:\n1.  Ask for clarifying information if you don't have enough details (e.g., travel dates, hotel preferences, interests).\n2.  Use the available tools if you have all the necessary information for a planning step.\n\nAfter a tool is used successfully, confirm with the user and ask what they'd like to do next. YOU HAVE TO USE TOOLS IF IT IS NEEDED (WHEN SEARCHING FOR TICKETS/HOTLES/FOOD/ACTIVITY)"""),
            ("placeholder", "{chat_history}"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])

    async def chat(self, request: ChatRequest, db: Session) -> ChatResponse:
        global global_db, global_roadmap_id
        global_db = db
        global_roadmap_id = request.roadmap_id
        tools = [find_tickets_tool, find_hotels_tool, find_activities_tool]
        agent = create_tool_calling_agent(self.llm, tools, self.prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
        chat_history = []
        for msg in request.messages[:-1]:
            chat_history.append(HumanMessage(content=msg.content) if msg.role == "user" else AIMessage(content=msg.content))
        user_input = request.messages[-1].content
        response = await agent_executor.ainvoke({
            "input": user_input,
            "chat_history": chat_history,
        })
        return ChatResponse(response=response.get("output", "I'm not sure how to respond to that."))