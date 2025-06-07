from typing import List
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from tools.toolbelt import TravelToolBelt
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()

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
        
        # A more proactive prompt for a tool-calling agent
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a proactive and friendly travel planning assistant.
Your goal is to help the user plan a trip by gathering their preferences and immediately using tools when you have enough information.

**Your Instructions:**
1.  **Be Proactive:** As soon as you have the necessary information for a planning step (like finding tickets or hotels), use the corresponding tool immediately. Do not wait to ask for more information if you can already take an action.
2.  **Gather Information Sequentially:** If you need more details to use a tool, ask for them clearly (e.g., travel dates, hotel preferences, interests).
3.  **Confirm and Continue:** After a tool is used successfully, confirm what you've done and then ask the next logical question to continue the planning process.
4.  **Be Conversational:** Maintain a friendly and helpful tone throughout the conversation.
"""),
            ("placeholder", "{chat_history}"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])

    async def chat(self, request: ChatRequest, toolbelt: TravelToolBelt) -> ChatResponse:
        tools = [toolbelt.find_tickets_tool, toolbelt.find_hotels_tool, toolbelt.find_activities_tool]
        
        agent = create_tool_calling_agent(self.llm, tools, self.prompt)
        # Setting verbose=True will print the agent's thoughts and tool usage
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

        # Reformat message history for this agent type
        chat_history = []
        for msg in request.messages[:-1]:
            chat_history.append(HumanMessage(content=msg.content) if msg.role == "user" else AIMessage(content=msg.content))

        user_input = request.messages[-1].content
        
        response = await agent_executor.ainvoke({
            "input": user_input,
            "chat_history": chat_history,
        })
        
        return ChatResponse(response=response.get("output", "I'm not sure how to respond to that."))