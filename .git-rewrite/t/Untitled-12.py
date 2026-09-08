"""Run this model in Python

> pip install openai
"""
import os
from openai import OpenAI

client = OpenAI(
    api_key = os.environ["OPENAI_API_KEY"],
)

messages = [
    {
        "role": "system",
        "content": "project planner for my ultron_agent project. coordinsate other models working in visual studio code",
    },
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": "test",
            },
        ],
    },
]

response_format = {
    "type": "text"
}

while True:
    response = client.chat.completions.create(
        messages = messages,
        model = "gpt-5",
        response_format = response_format,
    )

    if response.choices[0].message.tool_calls:
        print(response.choices[0].message.tool_calls)
        messages.append(response.choices[0].message)
        for tool_call in response.choices[0].message.tool_calls:
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": [
                    {
                        "type": "text",
                        "text": locals()[tool_call.function.name](),
                    },
                ],
            })
    else:
        print(f"[Model Response] {response.choices[0].message.content}")
        break
