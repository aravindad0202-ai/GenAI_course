import sys
from google import genai
from dotenv import load_dotenv

load_dotenv(r'D:\IT\AI\teaching\GenAI_course\Day_2\Chat_bot\backend\.env')

def start_chatbot():
    client = genai.Client()
    chat = client.chats.create(model="gemini-3.5-flash")
    while True:
        try:
            user_message = input("You: ")
            if user_message.strip().lower() in ['quit', 'exit']:
                print("Thank you")
                break
            if not user_message.strip():
                continue
                
            response = chat.send_message(user_message)

            print(f"Gemini: {response.text}\n")
            
        except KeyboardInterrupt:
            print("Thank you")
            sys.exit()
        except Exception as e:
            print(f"An error occurred: {e}\n")

if __name__ == "__main__":
    start_chatbot()
