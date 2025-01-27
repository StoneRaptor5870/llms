from IPython.display import display, update_display
import ollama

MODEL_LLAMA = 'llama3.2:1b'

question = input("Please enter your question:")

# prompts
system_prompt = "You are a helpful technical tutor who answers questions about python code, software engineering, data science and LLMs"
user_prompt = "Please give a detailed explanation to the following question: " + question

# messages
messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": user_prompt}
]

response = ollama.chat(model=MODEL_LLAMA, messages=messages)
reply = response['message']['content']
print(reply)