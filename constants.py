from dataclasses import dataclass
from pathlib import Path

templates_folder = Path(__file__).parent.resolve() / "templates"

BULLET_RE = "<*>"


@dataclass
class DataNames:
    PERSONAL_DETAILS = "PersonalDetails"
    PERSONAL_STATEMENT = "PersonalStatement"
    EDUCATION = "Education"
    WORK_EXPERIENCE = "WorkExperience"
    SKILLS = "Skills"
    RELEVANT_COURSES = "RelevantCourses"

    NAME = "Name"
    CURRENT_POSITION = "CurrentPosition"
    EMAIL = "Email"
    TELEPHONE = "Telephone"
    ADDRESS = "Address"
    WEBSITES = "WebSites"
    LINK = "Link"
    DEGREE = "Degree"
    UNIVERSITY = "University"
    DATES = "Dates"
    COMMENTS = "Comments"
    ORGANISATION = "Organisation"
    DESCRIPTION = "Description"
