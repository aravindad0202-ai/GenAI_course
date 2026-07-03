from dotenv import load_dotenv
load_dotenv(r'D:\IT\AI\teaching\GenAI_course\agent\.env')

from langgraph.graph import StateGraph, START, END
from schemas import State
from src.transcript_processor import TranscriptProcessor
from src.utils import llm
from langchain_core.messages import SystemMessage, HumanMessage
from src.prompt_loader import prompt
from src.email_tool import email_sender

builder = StateGraph(State)
# def analyze_transcript(state: State):
print('invoking')

def analyze_transcript(state: State) -> State:
    meeting_MOM = TranscriptProcessor().generate_MOM()
    return {
        'analysisOutput':meeting_MOM
    }

def draft_email(state: State) -> State:
    mom = state.get('analysisOutput')
    draftPrompt = f"{prompt['email_prompt']}\nTranscript:\n{mom}"
    message = [
        SystemMessage(content=prompt['system_prompt']),
        HumanMessage(content=draftPrompt)
    ]
    response = llm.invoke(message)
    return {
        'emailOutput': response.content[0]['text']
    }

def send_email(state: State) -> State:
    emailStatus = email_sender(state.get('emailOutput'))
    return {
        'nodeStatus': emailStatus
    }

builder.add_node('analyze_transcript', analyze_transcript)
builder.add_node('draft_email', draft_email)
builder.add_node('email_sender',send_email)

builder.add_edge(START, 'analyze_transcript')
builder.add_edge('analyze_transcript','draft_email')
builder.add_edge('draft_email','email_sender')
builder.add_edge('email_sender', END)

graph = builder.compile()
response = graph.invoke({})

print(response['emailOutput'])