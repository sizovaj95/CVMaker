import json

from fpdf import FPDF

from constants import DataNames as DN
import constants as co
import util

SECTION_TITLE_FONT = 12
MAIN_FONT_SIZE = 11
PT_TO_MM = 0.3528
PARA_MARGIN = 6
LINE_MARGIN = 1.5
BULLET_MARGIN = 5


class CV:
    def __init__(self, json_template: dict):
        self.pdf = FPDF()
        self.pdf.add_page()
        self.template = json_template
        self.line_margin = MAIN_FONT_SIZE * PT_TO_MM + LINE_MARGIN
        self.section_margin = SECTION_TITLE_FONT * PT_TO_MM + PARA_MARGIN
        self.multi_cell_kwargs = {
            "h": self.line_margin, "w": 0,
            "new_x": "LMARGIN", "new_y": "NEXT",
            "markdown": True
        }

    def draw_line(self):
        self.pdf.set_line_width(0.1)
        self.pdf.line(x1=self.pdf.get_x(), y1=self.pdf.get_y(),
                      x2=self.pdf.w-self.pdf.r_margin, y2=self.pdf.get_y())

    def make_section_title(self, text: str):
        self.pdf.set_font('Helvetica', size=SECTION_TITLE_FONT, style="B")
        self.pdf.cell(text=text.upper(), new_x="LMARGIN", new_y="NEXT",
                      h=self.section_margin)
        self.pdf.set_font(size=MAIN_FONT_SIZE)

    def maybe_add_page(self, num_lines: int) -> bool:
        if self.pdf.will_page_break(self.line_margin * num_lines + self.section_margin):
            self.pdf.add_page()

    def create_cv(self):
        self.add_personal_details()
        self.add_personal_statement()
        self.add_work_experience()
        self.add_education()
        return self.pdf

    @util.error_handler
    def add_skills(self):
        skills = self.template[DN.SKILLS]


    @util.error_handler
    def add_education(self):
        education = self.template[DN.EDUCATION]
        self.maybe_add_page(len(education[0]))
        self.make_section_title("Education")
        current_y = self.pdf.get_y()
        left_x = self.pdf.get_x()
        mid_x = self.pdf.w / 2
        current_x = left_x
        for edu in education:
            self.pdf.set_y(current_y)
            self.pdf.set_x(current_x)
            uni = edu[DN.UNIVERSITY]
            degree = edu[DN.DEGREE]
            dates = edu[DN.DATES]
            comments = edu[DN.COMMENTS]
            self.pdf.multi_cell(text=f"**{degree}**\n{uni}\n{dates}\n__{comments}__",
                                **self.multi_cell_kwargs)
            current_x = left_x if current_x == mid_x else mid_x
        self.pdf.ln(PARA_MARGIN / 2)
        self.draw_line()


    @util.error_handler
    def add_personal_statement(self):
        personal_statement = self.template[DN.PERSONAL_STATEMENT]
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
            summary, bullets = util.split_description(desc)
            self.pdf.multi_cell(text=f"**{name}**\n__{org}__\n{dates}\n{summary}",
                                **self.multi_cell_kwargs)
            for bullet in bullets:
                self.pdf.circle(x=self.pdf.l_margin + BULLET_MARGIN, y=self.pdf.get_y() + 1.9,
                                radius=0.5, style='DF')
                self.pdf.set_x(x=self.pdf.l_margin + BULLET_MARGIN + 3)
                self.pdf.multi_cell(text=bullet, **self.multi_cell_kwargs)
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

        self.pdf.set_font('Helvetica', size=26, style="B")
        self.pdf.cell(w=self.pdf.w / 2, text=name.upper(), new_x="LMARGIN", new_y="NEXT")
        self.pdf.set_font(size=12, style="B")
        self.pdf.cell(w=self.pdf.w / 2, text=current_position, new_x="RIGHT", new_y="TMARGIN", h=12*PT_TO_MM+PARA_MARGIN)
        self.pdf.set_font(size=MAIN_FONT_SIZE)
        self.pdf.multi_cell(w=0, h=MAIN_FONT_SIZE*PT_TO_MM + LINE_MARGIN,
                            text=f"**Email:** {email}\n**Tel:** {telephone}\n**Address:** {address}\n" + websites_text,
                            markdown=True, align="R")


def main():
    with open(co.templates_folder / "example.json", encoding="utf-8") as f:
        template = json.load(f)

    cv = CV(template).create_cv()
    cv.output("CV.pdf")


if __name__ == "__main__":
    main()