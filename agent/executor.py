import os

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from .tools import TOOLS

SYSTEM_PROMPT = (
    "You are the booking assistant for Harbor Hotels. "
    "Help guests find hotels by city and budget, look up bookings and cancel confirmed bookings. "
    "Always use the tools for availability, rates and bookings; never guess. "
    "Booking ids look like HB-5001. Ask for the booking id when the guest has not given one. "
    "Checked-in or already cancelled bookings cannot be cancelled; explain why. "
    "For anything unrelated to Harbor Hotels, say you can only help with Harbor Hotels bookings."
)


def build_executor() -> AgentExecutor:
    model = ChatAnthropic(
        model=os.environ.get("ANTHROPIC_MODEL", "claude-haiku-5-5"),
        api_key=os.environ.get("ANTHROPIC_API_KEY"),
        temperature=0,
        max_tokens=1024,
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad"),
        ]
    )
    agent = create_tool_calling_agent(model, TOOLS, prompt)
    return AgentExecutor(agent=agent, tools=TOOLS, return_intermediate_steps=True)
