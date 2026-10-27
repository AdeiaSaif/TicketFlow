from typing import TypedDict, Optional, Sequence
from typing_extensions import Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from datetime import datetime
import httpx
import json

load_dotenv()

current_date_str = datetime.now().strftime("%Y-%m-%d")

class PriceExtraction(BaseModel):
    operator: str = Field(description="Use <=, >=, or ==.")
    amount: Optional[float] = None

class EventExtraction(BaseModel):
    city: Optional[list[str]] = None
    date: Optional[list[str]] = None
    category: Optional[list[str]] = None
    venue: Optional[list[str]] = None
    title: Optional[list[str]] = None
    price: Optional[PriceExtraction] = None

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    city: Optional[str]
    date: Optional[str]
    category: Optional[str]
    venue: Optional[str]
    title: Optional[str]
    price: Optional[float]

@tool
def search_event(
    city: Optional[str] = None,
    date: Optional[str] = None,
    category: Optional[str] = None,
    venue: Optional[str] = None,
    title: Optional[str] = None,
    price: Optional[float] = None
) -> dict:
    """Search events by city, date, category, venue, title, and maximum price."""

    response = httpx.get(
        "http://0.0.0.0:8000/event_search",
        params={
            "city": city,
            "date": date,
            "category": category,
            "venue": venue,
            "title": title,
            "price": price
        },
        timeout=10
    )
    response.raise_for_status()
    return response.json()

tools = [search_event]

base_llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite"
)

extractor = base_llm.with_structured_output(EventExtraction)
llm = base_llm.bind_tools(tools)

def init_state(state: AgentState):
    print("init node")

    extracted = extractor.invoke(list(state["messages"]))

    state_updates = {
        "city": extracted.city[0] if extracted.city else None,
        "date": extracted.date[0] if extracted.date else None,
        "category": extracted.category[0] if extracted.category else None,
        "venue": extracted.venue[0] if extracted.venue else None,
        "title": extracted.title[0] if extracted.title else None,
        "price": extracted.price.amount if extracted.price else None
    }

    return state_updates

def agent(state: AgentState):
    print("agent node")

    filters = {
        key: state.get(key)
        for key in ["city", "date", "category", "venue", "title", "price"]
    }

    resp = llm.invoke(
        [
            SystemMessage(
                content="You are an event search assistant. "
                f"Use these filters to search events: {filters}"
            )
        ] + list(state["messages"])
    )

    return {"messages": [resp]}


def should_cont(state: AgentState):
    last_message = state["messages"][-1]
    return "tools" if isinstance(last_message, AIMessage) and last_message.tool_calls else END

graph = StateGraph(AgentState)

graph.add_node("init", init_state)
graph.add_node("agent", agent)
graph.add_node("tools", ToolNode(tools))

graph.add_edge(START, "init")
graph.add_edge("init", "agent")

graph.add_conditional_edges(
    "agent",
    should_cont,
    {
        "tools": "tools",
        END: END
    }
)

graph.add_edge("tools", "agent")

app = graph.compile()

result = app.invoke({
    "messages": [
        HumanMessage(
            content="Is there any tech event in Karachi this month under 5000?"
        )
    ]
})

print(result["messages"][-1].content)