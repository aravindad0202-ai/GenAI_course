import os
import uuid
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from dotenv import load_dotenv

load_dotenv(r"D:\IT\AI\teaching\GenAI_course\.env")

# --- 1. Define Custom Tools ---
# Use the @tool decorator and ALWAYS include a clear docstring. 
# The LLM reads the docstring to know when and how to use the tool. need to provide clear description about the tool including its input args and return
@tool
def generate_user_id() -> str:
    """Generates a unique user ID (UUID). Use this when a user needs a new ID."""
    return str(uuid.uuid4())

@tool
def add_numbers(a: float, b: float) -> float:
    """Adds two numbers together.
    
    Args:
        a: First value to add.
        b: Second value to add.
        
    Returns:
        The sum of the two values."""
    return a + b

# --- 2. Initialize Built-in Tool ---
# Tavily is an AI-optimized search engine that returns clean JSON text, not messy HTML.
# tavily_tool = TavilySearchResults(max_results=2)

# --- 3. Group and Bind the Tools ---
# Put all tools into a list
tools = [generate_user_id, add_numbers]
# tools = [generate_user_id, add_numbers, tavily_tool] # If enabling tavily web search tool
# Initialize the Gemini Model (Set temperature to 0 for more reliable tool calling)
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

# Bind the tools to the LLM. This tells Gemini what tools it has access to.
llm_with_tools = llm.bind_tools(tools)


# --- 4. Define the Chatbot Node ---
def chatbot(state: MessagesState):
    """Passes the conversation to the LLM. The LLM may return text OR a tool call request."""
    # Notice we are using `llm_with_tools` here, not the base `llm`
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}


# --- 5. Build the Graph ---
builder = StateGraph(MessagesState)

# Add the chatbot node
builder.add_node("chatbot", chatbot)

# LangGraph's pre-built ToolNode automatically handles executing the tools in our list
builder.add_node("tools", ToolNode(tools))

# The graph always starts at the chatbot
builder.add_edge(START, "chatbot")

# --- THE MAGIC ROUTER ---
# `tools_condition` automatically checks the LLM's response.
# IF the LLM asked to use a tool -> Routes to the "tools" node.
# IF the LLM just replied with normal text -> Routes to END.
builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)

# After a tool is executed, the graph MUST loop back to the chatbot.
# This allows the LLM to read the tool's output and generate a human-friendly response.
builder.add_edge("tools", "chatbot")

# --- 6. Compile with Memory ---
memory = MemorySaver()
graph = builder.compile(checkpointer=memory)


# --- 7. Run the Interactive Chat ---
def run_chat():
    print("Agent initialized with Custom & Search Tools! (Type 'q' to exit)")
    print("Try asking:")
    print("1. 'Generate a new ID for me'")
    print("2. 'What is 5234 + 9123?'")
    print("3. 'Who won the most recent Super Bowl?'")
    print("-" * 60)
    
    config = {"configurable": {"thread_id": "tool_session_1"}}
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ["quit", "q", "exit"]:
            break
            
        # Stream the output so we can see the agent's thought process
        # We use stream() instead of invoke() to watch the loop happen in real-time
        events = graph.stream(
            {"messages": [HumanMessage(content=user_input)]}, 
            config=config, 
            stream_mode="values"
        )
        
        for event in events:
            # Grab the most recent message in the state
            last_message = event["messages"][-1]
            
            # 1. FIX: Safely check if the attribute exists AND if it's not empty
            if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                print(f"⚙️  Agent is calling tool: {last_message.tool_calls[0]['name']}")
            
            # 2. If it's an AI message with actual text content, print it
            elif last_message.type == "ai" and last_message.content:
                print(f"Gemini: {last_message.content}")

if __name__ == "__main__":
    run_chat()