from copy import deepcopy

from dotenv import load_dotenv
import openai
import gradio as gr

import util

template_name = "example.json"

load_dotenv()
client = openai.OpenAI()
MODEL_NAME = "gpt-4o"
cv_str = ""

system_msg = ("You are assisting with creating sections for CV. Be short and clear. Do not make facts up."
              "You can have access to both user's CV and job description. If you don't, say so, don't give generic answer.")


tools = [
    {
        "type": "function",
            "function": {
                "name": "get_data_from_cv",
                "description": "Get personal information (like name, education, work experience) that"
                               " typically can be found in a CV. Call this to get information about a user"
                               " or when answering question requires to have knowledge of CV content.",
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


def user(message, history):
    return "", history + [{"role": "user", "content": message}]


def insert_system_role(history: list[dict], system_message: str) -> \
        list[dict]:
    if len(history) == 1:
        history.insert(0, {"role": "system", "content": system_message})
    else:
        history[0] = {"role": "system", "content": system_message}
    return history


def get_data_from_cv():
    global cv_str
    if not cv_str:
        cv_str = util.load_cv(template_name)
    return cv_str


if __name__ == "__main__":
    pixels_per_line = 19.2
    chatbot_height = 800
    with gr.Blocks(title="CV Assistant") as ui:
        job_description = ""
        with gr.Row():
            with gr.Column():
                job_desc = gr.Textbox(placeholder="Insert job description here",
                                      lines=int(chatbot_height // pixels_per_line),
                                      label="Job description")
                clear_btn_desc = gr.Button("Clear")
            with gr.Column():
                chatbot = gr.Chatbot(type="messages", height=chatbot_height, label="")
                msg_box = gr.Textbox(placeholder="Your message", label="")
                with gr.Row():
                    clear_btn_chat = gr.Button("Clear")
                    submit_btn = gr.Button("Send")

        def chat(history: list[dict]):
            history = insert_system_role(history, system_msg)
            completion = client.chat.completions.create(
                model=MODEL_NAME,
                messages=history,
                tools=tools
            )
            if completion.choices[0].finish_reason == "tool_calls":
                history_copy = deepcopy(history)
                history_copy.append(completion.choices[0].message)
                for tool_call in completion.choices[0].message.tool_calls:
                    name = tool_call.function.name
                    print(f"Calling `{name}`")

                    result = call_function(name)
                    history_copy.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result
                    })
                completion = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=history_copy
                )
            history.append({"role": "assistant", "content": completion.choices[0].message.content})
            return history

        def call_function(name: str):
            if name == "get_data_from_cv":
                return get_data_from_cv()
            if name == "get_description":
                return util.clean_text(job_description)

        def update_job_description(job_desc_textbox):
            global job_description
            job_description = job_desc_textbox

        gr.on(triggers=[msg_box.submit, submit_btn.click],
              fn=user, inputs=[msg_box, chatbot], outputs=[msg_box, chatbot],
              queue=False).then(
            chat, inputs=[chatbot], outputs=[chatbot])

        job_desc.change(fn=update_job_description, inputs=[job_desc])
        clear_btn_chat.click(lambda: None, None, chatbot, queue=False)
        clear_btn_desc.click(lambda: None, None, job_desc, queue=False)

    ui.launch()