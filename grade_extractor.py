from bs4 import BeautifulSoup

class GradeExtractor:
    def __init__(self, html_content):
        self.soup = BeautifulSoup(html_content, 'html.parser')

    def extract_grades(self):
        """Extracts grades from the HTML page."""
        grades = []
        # Target the first grade table (course grades)
        grade_table = self.soup.select_one('.grade-table:not(.box-primary .grade-table)')
        if grade_table:
            for row in grade_table.select('tbody tr'):
                cells = row.find_all('td')
                if len(cells) >= 6:
                    grades.append({
                        "Course": cells[1].get_text(strip=True),
                        "Grade": cells[2].get_text(strip=True),
                        "Mark": cells[3].get_text(strip=True),
                        "Credit Hours": cells[4].get_text(strip=True),
                        "Grade Point": cells[5].get_text(strip=True)
                    })
        return grades

    def extract_gpa_summary(self):
        """Extracts GPA summary (Grade Point, Credit Hours, GPA)."""
        summary = {}
        # Correct selector for the GPA summary box
        summary_box = self.soup.select_one('.box.box-primary')
        if summary_box:
            rows = summary_box.select('.grade-table tr')
            if len(rows) >= 4:
                # Grade Point (This Semester)
                grade_point = rows[1].select_one('td span')
                # Credit Hours (This Semester)
                credit_hour = rows[2].select_one('td span')
                # GPA (This Semester)
                gpa = rows[3].select_one('td span')

                summary = {
                    "Grade Point": grade_point.get_text(strip=True) if grade_point else "N/A",
                    "Credit Hour": credit_hour.get_text(strip=True) if credit_hour else "N/A",
                    "GPA": gpa.get_text(strip=True) if gpa else "N/A"
                }
        return summary