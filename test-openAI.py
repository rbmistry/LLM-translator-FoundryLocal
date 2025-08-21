# Simple Python example using OpenAI API
from openai import OpenAI

# Configure the client to use your local endpoint
client = OpenAI(
    base_url="http://localhost:5272/V1",
    api_key="not-needed"  # API key isn't used but the client requires one
)

# Chat completion example
response = client.chat.completions.create(
    model="deepseek-r1-distill-qwen-7b-qnn-npu",  # Use the id of your loaded model, found in 'foundry service ps'
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the capital of France?"}
    ],
    max_tokens=1000
)

print(response.choices[0].message.content)