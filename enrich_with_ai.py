from dotenv import load_dotenv
import json
import pprint

import openai

import constants as co
from get_job_description import get_description

load_dotenv()
client = openai.OpenAI()
template_name = "example.json"

system_msg = "You are assisting with creating sections for CV. Be short and clear, give no more than 3 sentences."
user_msg = "Write a personal statement for a CV based on person's work experience, skills and job description requirements."

cv_str = ''


def get_data_from_cv() -> str:
    global cv_str
    if cv_str:
        return cv_str
    with open(co.templates_folder / template_name, "r", encoding="utf-8") as f:
        cv = json.load(f)
    work_experience = cv.get(co.DataNames.WORK_EXPERIENCE, [])
    skills = cv.get(co.DataNames.SKILLS, [])
    work_experience_str = 'Work experience:\n'
    for work in work_experience:
        for k, v in work.items():
            if isinstance(v, str):
                work_experience_str += f"{k}: {v} "
            elif isinstance(v, list):
                bullets = '\n'.join(v)
                work_experience_str += f"{bullets} "
        work_experience_str += '\n'
    skills_str = 'Skills:\n'
    for skill in skills:
        name = skill[co.DataNames.NAME]
        bullets = skill[co.DataNames.LIST]
        bullets = ', '.join(bullets)
        skills_str += f"{name}: {bullets}"
        skills_str += '\n'

    cv_str = work_experience_str + skills_str
    return cv_str


tools = [
    {
        "type": "function",
            "function": {
                "name": "get_data_from_cv",
                "description": "Get work experience and skill set for the person. Call this if you need to know what qualities the person already possesses.",
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
        return get_data_from_cv()
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
        # args = json.loads(tool_call.function.arguments)

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