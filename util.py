import json
import re
import os

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


def remove_double_spaces(text: str) -> str:
    text = re.subn(r"\s{2,}", " ", text)[0]
    return text


def create_empty_template():
    personal_details = {
        DN.PERSONAL_DETAILS: {
            DN.NAME: "Philip Fry",
            DN.CURRENT_POSITION: "Intergalactic delivery worker",
            DN.EMAIL: "panucci.asst@panuccis.com",
            DN.TELEPHONE: "0123455678",
            DN.ADDRESS: "Rugby Road in Brooklyn, New York",
            DN.WEBSITES: [{DN.NAME: "LinkedIn", DN.LINK: ""}]
        }
    }
    education = {
        DN.EDUCATION: [
            {DN.DEGREE: "MSc in Delivery",
             DN.UNIVERSITY: "Academy of Delivery",
             DN.DATES: "09/2017 - 09/2018",
             DN.COMMENTS: "With Distinction"}
        ]
    }
    work_experience = {
        DN.WORK_EXPERIENCE: [
            {DN.NAME: "Intergalactic delivery worker",
             DN.ORGANISATION: "Planet Express",
             DN.DATES: "01/3000 - present",
             DN.DESCRIPTION: "Managing challenging clients",
             DN.LIST: ["Item 1", "Item 2"]},
            {DN.NAME: "Head tank feeder",
             DN.ORGANISATION: "New New York Museum",
             DN.DATES: "01/3000 - present",
             DN.DESCRIPTION: "Managing challenging clients",
             DN.LIST: []}
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
        DN.PERSONAL_STATEMENT: "Markdown-like styling: **bold**, __italics__, --underlined--.",
        **work_experience,
        **education,
        **skills
    }
    if not os.path.exists(co.templates_folder):
        os.mkdir(co.templates_folder)
    with open(co.templates_folder / "example_template.json", "w", encoding="utf-8") as f:
        json.dump(cv_template, f, indent=2)


if __name__ == "__main__":
    create_empty_template()