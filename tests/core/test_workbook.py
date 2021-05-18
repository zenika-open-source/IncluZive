import pytest
from openpyxl import Workbook

from core.workbook import load_annotations


@pytest.mark.parametrize(
    "table, annotations",
    [
        (
            """
Text	Entity	Label
06/07/2018 zenika-resume 	06/07/2018	DATE
""",
            [["06/07/2018 zenika-resume ", [("06/07/2018", "DATE")]]],
        ),
        (
            """
Text	Entity	Label
06/07/2018 zenika-resume 	06/07/2018	DATE
Velay S 6 ans d'expérience 	Velay S	PER
""",
            [
                ["06/07/2018 zenika-resume ", [("06/07/2018", "DATE")]],
                ["Velay S 6 ans d'expérience ", [("Velay S", "PER")]],
            ],
        ),
        (
            """
Text	Entity	Label
06/07/2018 zenika-resume 	06/07/2018	DATE
06/07/2018 zenika-resume 	06/07/2018	DATE
""",
            [["06/07/2018 zenika-resume ", [("06/07/2018", "DATE")]]],
        ),
        (
            """
Text	Entity	Label
Velay S 6 ans d'expérience 	Velay S	PER
Velay S 6 ans d'expérience 	6 ans	PERIODE
""",
            [
                ["Velay S 6 ans d'expérience ", [("Velay S", "PER"), ("6 ans", "PERIODE")]],
            ],
        ),
        (
            """
Text	Entity	Label
Velay S 6 ans d'expérience\t\t\t\t\t\t\t
""",
            [],
        ),
    ],
)
def test_load_annotations(table, annotations):
    data = [line.split(sep="\t") for line in table.splitlines() if line.strip()]
    workbook = Workbook()
    worksheet = workbook.active
    for row in data:
        worksheet.append(row)

    actual = load_annotations(worksheet)
    assert actual == annotations
