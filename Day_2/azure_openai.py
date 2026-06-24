from openai import AzureOpenAI

client = AzureOpenAI(
    type='azure',
    azure_endpoint="https://{your-resource-name}.openai.azure.com/",
    api_key = 'asdfhkjbadkv9uo3h98uuihakg',
    api_version='version name'
)

systemMessage = """You are a senior technical advisor specialized in Python.You provide accurate, actionable, and structured information to users.
Rules:
* Use clear formatting, such as bold text, bullet points, and code blocks (where applicable) to make your answers scannable.
* Tailor your explanation to the user's level of expertise.
* Avoid unsupported speculation; clearly state assumptions if any data is missing."""

chat_history = [{'role':'system','content':systemMessage}]

def chat_bot(user_input:str):
    chat_history.append([{'role':'user','content':user_input}])
    response = client.chat.completions.create(model='gpt-4.1',temperature = 0.3, messages=chat_history)
    output_content = response.choices[0].message.content
    if output_content:
        chat_history.append({'role':'assistant','content':output_content})

if __name__ == '__main__':
    chat_bot("Hi")
        