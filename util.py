import json

import constants as co
from constants import DataNames as DN


def split_description(description: str) -> tuple[str, list]:
    try:
        first_bullet_ind = description.index(co.BULLET_RE)
    except ValueError:
        return description, []
    summary = description[:first_bullet_ind]
    bullets = description[first_bullet_ind:].split(co.BULLET_RE)
    bullets = [b.strip() for b in bullets]
    bullets = [b for b in bullets if b]
    return summary, bullets


def error_handler(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except KeyError:
            return
    return wrapper


def create_empty_template():
    personal_details = {
        DN.PERSONAL_DETAILS: {
            DN.NAME: "",
            DN.CURRENT_POSITION: "",
            DN.EMAIL: "",
            DN.TELEPHONE: "",
            DN.ADDRESS: "",
            DN.WEBSITES: [{DN.NAME: "LinkedIn", DN.LINK: ""}]
        }
    }
    education = {
        DN.EDUCATION: [
            {DN.DEGREE: "MSc Mathematics",
             DN.UNIVERSITY: "University of Glasgow",
             DN.DATES: "09/2017 - 09/2018",
             DN.COMMENTS: "With Distinction"}
        ]
    }
    work_experience = {
        DN.WORK_EXPERIENCE: [
            {DN.NAME: "Delivery Boy",
             DN.ORGANISATION: "Planet Express",
             DN.DATES: "01/3000 - present",
             DN.DESCRIPTION: "Managing challenging clients"}
        ]
    }
    skills = {
        DN.SKILLS: [
            {DN.NAME: "Professional",
             DN.LIST: ["Word", "Excel"]}
        ]
    }
    cv_template = {
        **personal_details,
        DN.PERSONAL_STATEMENT: f"Markdown-like styling: **bold**, __italics__, --underlined--."
                               f" For bullet points use {co.BULLET_RE}",
        **work_experience,
        **education,
        **skills
    }
    with open(co.templates_folder / "example_template.json", "w", encoding="utf-8") as f:
        json.dump(cv_template, f, indent=2)


if __name__ == "__main__":
    create_empty_template()