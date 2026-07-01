import os
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.checkpoint.memory import MemorySaver
from dotenv import load_dotenv

load_dotenv(r"D:\IT\AI\teaching\GenAI_course\.env")


llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash", temperature=0.2)
def call_model(state: MessagesState):
    """Passes the message history to Gemini and returns its response."""
    response = llm.invoke(state["messages"])
    # We return a dictionary with the "messages" key. 
    # LangGraph knows to append this new message, not overwrite the list.
    return {"messages": [response]}

# --- 3. Build the Graph ---
# We pass MessagesState directly into the StateGraph
builder = StateGraph(MessagesState)

builder.add_node("chatbot", call_model)
builder.add_edge(START, "chatbot")
builder.add_edge("chatbot", END)

# --- 4. Compile with Memory ---
# We use MemorySaver so the bot remembers the context of the conversation
memory = MemorySaver()
graph = builder.compile(checkpointer=memory)

# --- 5. Run the Chat Interface ---
def run_chat():
    print("Gemini Chatbot initialized! (Type 'quit' or 'q' to exit)")
    print("-" * 50)
    
    # The thread_id tracks this specific conversation history in memory
    config = {"configurable": {"thread_id": "gemini_session_1"}} # thread_id must be unique.
    
    while True:
        user_input = input("You: ")
        
        if user_input.lower() in ["quit", "q", "exit"]:
            print("Ending chat. Goodbye!")
            break
            
        # Wrap the input in a HumanMessage
        input_message = HumanMessage(content=user_input)
        
        # Invoke the graph. 
        output = graph.invoke({"messages": [input_message]}, config=config)
        
        # The output state contains the full message list; we print the very last one
        ai_response = output["messages"][-1].content
        print(f"\nGemini: {ai_response}\n")

if __name__ == "__main__":
    run_chat()