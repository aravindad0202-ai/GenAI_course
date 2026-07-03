from langchain_google_genai import ChatGoogleGenerativeAI
from .email_tool import email_sender

llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash", temperature=0.2)
llm_with_tool = llm.bind_tools(tools=[email_sender])