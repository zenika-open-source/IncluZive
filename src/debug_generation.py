import csv
import os
from typing import List, Union, Tuple

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, NamedStyle, Border, Side
from openpyxl.worksheet.worksheet import Worksheet
from styleframe import StyleFrame, Styler

from src.predict_strategy import Span

Sentence = str

TEXT_BLOCK = 0


def write_debug_file(
    all_sensitives_spans: List[Tuple[Sentence, Union[None, Span]]], dest
):
    debug_filename = os.path.splitext(dest)[0] + "_debug.csv"
    with open(debug_filename, "w") as debug_file:
        debug_writer = csv.writer(
            debug_file, delimiter=",", quotechar="|", quoting=csv.QUOTE_MINIMAL
        )
        for line, span in all_sensitives_spans:
            text = "" if not span else span.text
            label = "" if not span else span.label
            debug_writer.writerow([line, text, label])


def write_debug_spreadsheet(
    all_sensitives_spans: List[Tuple[Sentence, Union[None, Span]]], dest
):
    workbook = Workbook()
    sheet: Worksheet = workbook.active
    sheet.append(["Text Line", "Entity Text", "Entity Label"])
    header = NamedStyle(name="header")
    header.font = Font(bold=True)
    header.border = Border(bottom=Side(border_style="thin"))
    header.alignment = Alignment(horizontal="center", vertical="center")
    sheet.column_dimensions["A"].width = 100
    sheet.column_dimensions["A"].alignment = Alignment(wrapText=True)

    for cell in sheet[1]:
        cell.style = header
    for row_number, sentence, span in map(
        lambda x: (x[0] + 2, *x[1]), enumerate(all_sensitives_spans)
    ):
        sheet.append([sentence] + (["", ""] if not span else [span.text, span.label]))
        sheet.row_dimensions[row_number].height = 25 if len(sentence) > 115 else None

    adjusted_width = (
        max([len(span.text) for _, span in all_sensitives_spans if span is not None])
    ) * 1.1
    sheet.column_dimensions["B"].width = adjusted_width
    adjusted_width = (
        max(
            [len(span.label) for _, span in all_sensitives_spans if span is not None]
            + [len("Entity Label")]
        )
    ) * 1.1
    sheet.column_dimensions["C"].width = adjusted_width

    workbook.save(filename=dest)


def write_style_frame(
    all_sensitives_spans: List[Tuple[Sentence, Union[None, Span]]], dest
):
    df = pd.DataFrame(
        {
            "Text": [sentence for sentence, _ in all_sensitives_spans],
            "Entity": [
                ("" if not span else span.text) for _, span in all_sensitives_spans
            ],
            "Label": [
                ("" if not span else span.label) for _, span in all_sensitives_spans
            ],
        }
    )
    sf = StyleFrame(df)
    header_style = Styler(bold=True, font_size=18)
    sf.apply_headers_style(styler_obj=header_style)

    adjusted_width = (
        max([len(span.text) for _, span in all_sensitives_spans if span is not None])
    ) * 1.1
    sf.set_column_width(columns="Entity", width=adjusted_width)

    adjusted_width = (
        max(
            [len(span.label) for _, span in all_sensitives_spans if span is not None]
            + [len("Entity Label")]
        )
    ) * 1.1
    sf.set_column_width(columns="Label", width=adjusted_width)

    sf.set_column_width(columns="Text", width=100)
    sf.set_row_height(rows=[1], height=25)
    sf.set_row_height(
        rows=[
            (idx + 2)
            for idx, sentence_span_tuple in enumerate(all_sensitives_spans)
            if len(sentence_span_tuple[0]) > 115
        ],
        height=50,
    )

    sf.to_excel(dest).save()
