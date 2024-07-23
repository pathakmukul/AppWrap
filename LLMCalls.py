import openai
from groq import Groq
import os

# Setup your OpenAI API key here
openai.api_key = 'sk-LOLOLOLOLOL'
# load groq key if need be!

# Define bot strategies

def GPTCalls(prompt):
    """Say hello to the user """
    # prompt = f"Say hello to the user"
    
    response = openai.chat.completions.create(
    model="gpt-3.5-turbo",
    # model="gpt-4-0125-preview",
    messages=[{"role": "user", "content": prompt}],
    )
    move_strA = response.choices[0].message.content.strip()
    # print(move_strA)
    return move_strA


def GroqCalls(promptz):
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"),
)
    
    prompt = f" write me a 500 word essay on topic: {promptz}"
    


    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="llama3-8b-8192",
    )

    print("::::LLM CALL:", chat_completion.choices[0].message.content)
    return chat_completion.choices[0].message.content
