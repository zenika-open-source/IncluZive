import pytest
from openpyxl import Workbook

from core.workbook import load_annotations


@pytest.mark.parametrize(
    "table, annotations",
    [
        (
            """
Text	page	x1	y1	x2	y2	Entity	Label
06/07/2018 zenika-resume 	0	26,4531002044678	14,7578125	358,363220214844	23,6953125	06/07/2018	DATE
""",
            [["06/07/2018 zenika-resume ", [("06/07/2018", "DATE")]]],
        ),
        (
            """
Text	page	x1	y1	x2	y2	Entity	Label
06/07/2018 zenika-resume 	0	26,4531002044678	14,7578125	358,363220214844	23,6953125	06/07/2018	DATE
Velay S 6 ans d'expérience 	0	28,0065994262695	76,0113220214844	565,976501464844	111,218208312988	Velay S	PER
""",
            [
                ["06/07/2018 zenika-resume ", [("06/07/2018", "DATE")]],
                ["Velay S 6 ans d'expérience ", [("Velay S", "PER")]],
            ],
        ),
        (
            """
Text	page	x1	y1	x2	y2	Entity	Label
06/07/2018 zenika-resume 	0	26,4531002044678	14,7578125	358,363220214844	23,6953125	06/07/2018	DATE
06/07/2018 zenika-resume 	1	26,453125	14,7578125	358,363464355469	23,6953125	06/07/2018	DATE
""",
            [["06/07/2018 zenika-resume ", [("06/07/2018", "DATE")]]],
        ),
        (
            """
Text	page	x1	y1	x2	y2	Entity	Label
Velay S 6 ans d'expérience 	0	28,0065994262695	76,0113220214844	565,976501464844	111,218208312988	Velay S	PER
Velay S 6 ans d'expérience 	0	28,0065994262695	76,0113220214844	565,976501464844	111,218208312988	6 ans	PERIODE
""",
            [
                ["Velay S 6 ans d'expérience ", [("Velay S", "PER"), ("6 ans", "PERIODE")]],
            ],
        ),
        (
            """
Text	page	x1	y1	x2	y2	Entity	Label
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
