import pprint

import openai
from dotenv import load_dotenv

import util
from get_job_description import get_description

load_dotenv()
client = openai.OpenAI()
template_name = "example.json"

system_msg = "You are assisting with creating sections for CV. Be short and clear, give no more than 3 sentences. Do not make facts up."
user_msg = ("Write a personal statement for a CV based on user's work experience, skills and job description requirements."
            " Don't repeat facts from CV.")


MODEL_NAME = "gpt-4o"


tools = [
    {
        "type": "function",
            "function": {
                "name": "get_data_from_cv",
                "description": "Get work personal, work and education information common for CV. Call when need to get information about user.",
                "parameters": {}
            }
    },
    {
        "type": "function",
            "function": {
                "name": "get_description",
                "description": "Get job description. Call this if you need to know what skills, qualities are required by job offer.",
                "parameters": {}
            }
    }
]

def call_function(name: str):
    if name == "get_data_from_cv":
        return util.load_cv(template_name)
    if name == "get_description":
        return get_description()


def write_suggestions_for_cv():

    messages = [{"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg}]
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=tools,
    )
    messages.append(completion.choices[0].message)
    for tool_call in completion.choices[0].message.tool_calls:
        name = tool_call.function.name
        print(f"Calling `{name}`")

        result = call_function(name)
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": result
        })

    completion_2 = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=tools,
    )
    print(completion_2.choices[0].message.content)
    print()
    pprint.pp(completion_2.choices[0].message.content)


if __name__ == "__main__":

    write_suggestions_for_cv()