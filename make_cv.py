import json
from copy import deepcopy
import math
import logging

import fpdf.errors
from fpdf import FPDF

from constants import DataNames as DN
import constants as co
import util

SECTION_TITLE_FONT = 12
MAIN_FONT_SIZE = 11
PT_TO_MM = 0.3528
PARA_MARGIN = 6
LINE_MARGIN = 1.5
BULLET_X_OFFSET = 5
BULLET_Y_OFFSET = 2.5
FONT_NAME = "Nunito"


class CV:
    def __init__(self, json_template: dict):
        self.pdf = FPDF()
        self.pdf.add_page()
        self.template = json_template
        self.line_margin = MAIN_FONT_SIZE * PT_TO_MM + LINE_MARGIN
        self.section_margin = SECTION_TITLE_FONT * PT_TO_MM + PARA_MARGIN
        self.col_width = self.pdf.w // 2 - 20
        self.multi_cell_kwargs = {
            "h": self.line_margin, "w": 0,
            "new_x": "LMARGIN", "new_y": "NEXT",
            "markdown": True
        }
        self.person_name = None

    def draw_line(self):
        self.pdf.set_line_width(0.1)
        self.pdf.line(x1=self.pdf.get_x(), y1=self.pdf.get_y(),
                      x2=self.pdf.w-self.pdf.r_margin, y2=self.pdf.get_y())

    def make_section_title(self, text: str):
        self.pdf.set_font(size=SECTION_TITLE_FONT, style="B")
        self.pdf.cell(text=text.upper(), new_x="LMARGIN", new_y="NEXT",
                      h=self.section_margin)
        self.pdf.set_font(size=MAIN_FONT_SIZE)

    def maybe_add_page(self, num_lines: int) -> bool:
        if self.pdf.will_page_break(self.line_margin * num_lines + self.section_margin):
            self.pdf.add_page()

    def add_font(self, name: str):
        self.pdf.add_font(name, style="", fname=co.fonts_folder / name / f"{name}-Regular.ttf")
        self.pdf.add_font(name, style="b", fname=co.fonts_folder / name / f"{name}-ExtraBold.ttf")
        self.pdf.add_font(name, style="i", fname=co.fonts_folder / name / f"{name}-Italic.ttf")
        self.pdf.add_font(name, style="bi", fname=co.fonts_folder / name / f"{name}-BoldItalic.ttf")

    def make_bullet_points_list(self, x, y, values_list: list[str], cell_kwargs: dict):
        self.pdf.set_y(y)
        self.pdf.set_x(x)
        for item in values_list:
            item = util.remove_double_spaces(item)
            self.pdf.circle(x=x + BULLET_X_OFFSET, y=self.pdf.get_y() + BULLET_Y_OFFSET,
                            radius=0.5, style='DF')
            self.pdf.set_x(x=x + BULLET_X_OFFSET + 3)
            self.pdf.multi_cell(text=item, **cell_kwargs)

    def create_cv(self):
        try:
            self.pdf.set_font(FONT_NAME)
        except fpdf.errors.FPDFException:
            self.add_font(FONT_NAME)
            self.pdf.set_font(FONT_NAME)
        self.add_personal_details()
        self.add_personal_statement()
        self.add_education()
        self.add_work_experience()
        self.add_skills()
        return self.pdf

    @util.error_handler
    def add_skills(self):
        skills = self.template[DN.SKILLS]
        approx_lines = 0
        for skill in skills:
            approx_lines += 1 + len(skill[DN.LIST]) // 2
        self.maybe_add_page(approx_lines)
        self.make_section_title("Skills")
        left_x = self.pdf.l_margin
        mid_x = self.pdf.w / 2

        multi_cell_kwargs = deepcopy(self.multi_cell_kwargs)
        multi_cell_kwargs['w'] = self.col_width
        for skill_dict in skills:
            self.pdf.cell(text=f"**{skill_dict[DN.NAME]}**", **self.multi_cell_kwargs)
            col_start_y = self.pdf.get_y()
            bullets = skill_dict[DN.LIST]
            mid = math.ceil(len(bullets) / 2)
            first_half, second_half = bullets[:mid], bullets[mid:]
            self.make_bullet_points_list(left_x, col_start_y, first_half, multi_cell_kwargs)
            col_end_y = self.pdf.get_y()
            self.make_bullet_points_list(mid_x, col_start_y, second_half, multi_cell_kwargs)
            if self.pdf.get_y() > col_end_y:
                col_end_y = self.pdf.get_y()
            self.pdf.set_y(col_end_y)
            self.pdf.ln(PARA_MARGIN / 4)

    @util.error_handler
    def add_education(self):
        education = self.template[DN.EDUCATION]
        self.maybe_add_page(len(education[0]))
        self.make_section_title("Education")
        current_y = self.pdf.get_y()
        left_x = self.pdf.get_x()
        mid_x = self.pdf.w / 2
        current_x = left_x
        multi_cell_kwargs = deepcopy(self.multi_cell_kwargs)
        multi_cell_kwargs['w'] = self.col_width
        for edu in education:
            self.pdf.set_y(current_y)
            self.pdf.set_x(current_x)
            uni = edu[DN.UNIVERSITY]
            degree = edu[DN.DEGREE]
            dates = edu[DN.DATES]
            comments = edu[DN.COMMENTS]
            text = f"**{degree}**\n{uni}\n{dates}\n__{comments}__"
            text = util.remove_double_spaces(text)
            self.pdf.multi_cell(text=text, **multi_cell_kwargs)
            current_x = left_x if current_x == mid_x else mid_x
        self.pdf.ln(PARA_MARGIN / 2)
        self.draw_line()


    @util.error_handler
    def add_personal_statement(self):
        personal_statement = self.template[DN.PERSONAL_STATEMENT]
        personal_statement = util.remove_double_spaces(personal_statement)
        self.pdf.multi_cell(text=personal_statement, **self.multi_cell_kwargs)
        self.pdf.ln(PARA_MARGIN / 2)
        self.draw_line()


    @util.error_handler
    def add_work_experience(self):
        work_experience = self.template[DN.WORK_EXPERIENCE]
        self.make_section_title("Work Experience")
        for i, work in enumerate(work_experience):
            name = work[DN.NAME]
            org = work[DN.ORGANISATION]
            dates=  work[DN.DATES]
            desc = work[DN.DESCRIPTION]
            bullets = work[DN.LIST]
            if desc:
                header_text = f"**{name}**\n__{org}__\n{dates}\n{desc}"
            else:
                header_text = f"**{name}**\n__{org}__\n{dates}"
            header_text = util.remove_double_spaces(header_text)
            approx_len = 1 + len(header_text.split('\n')) + len(bullets)
            self.maybe_add_page(approx_len)
            self.pdf.multi_cell(text=header_text,
                                **self.multi_cell_kwargs)
            self.make_bullet_points_list(self.pdf.get_x(), self.pdf.get_y(), bullets,
                                         self.multi_cell_kwargs)
            self.pdf.ln(PARA_MARGIN/2)
        self.draw_line()

    @util.error_handler
    def add_personal_details(self):
        personal_details = self.template[DN.PERSONAL_DETAILS]

        name = personal_details[DN.NAME]
        current_position = personal_details[DN.CURRENT_POSITION]
        email = personal_details[DN.EMAIL]
        telephone = personal_details[DN.TELEPHONE]
        address = personal_details[DN.ADDRESS]
        websites = personal_details[DN.WEBSITES]
        websites_text = ""
        for website in websites:
            websites_text += f"[{website[DN.NAME]}]({website[DN.LINK]})\n"

        text = f"**Email:** {email}\n**Tel:** {telephone}\n**Address:** {address}\n" + websites_text
        text = util.remove_double_spaces(text)

        self.pdf.set_font(size=26, style="B")
        self.pdf.cell(w=self.pdf.w / 2, text=name.upper(), new_x="LMARGIN", new_y="NEXT")
        self.pdf.set_font(size=12, style="B")
        self.pdf.cell(w=self.pdf.w / 2, text=current_position.upper(), new_x="RIGHT",
                      new_y="TMARGIN", h=12*PT_TO_MM+PARA_MARGIN)
        self.pdf.set_font(size=MAIN_FONT_SIZE)
        self.pdf.multi_cell(w=0, h=MAIN_FONT_SIZE*PT_TO_MM + LINE_MARGIN,
                            text=text,
                            markdown=True, align="R")
        self.person_name = name.title()


def main():
    with open(co.templates_folder / "example.json", encoding="utf-8") as f:
        template = json.load(f)

    cv_maker = CV(template)
    cv = cv_maker.create_cv()
    if cv_maker.person_name:
        doc_name = f"{cv_maker.person_name}.pdf"
    else:
        doc_name = "CV.pdf"
    try:
        cv.output(doc_name)
    except PermissionError:
        logging.warning("The pdf you are trying to modify is open! Close it and try again.")


if __name__ == "__main__":
    main()