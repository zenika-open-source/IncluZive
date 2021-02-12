import csv
import os
from typing import List, Union, Tuple

import fitz
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, NamedStyle, Border, Side
from openpyxl.worksheet.worksheet import Worksheet
from styleframe import StyleFrame, Styler

from src.predict_strategy import Span, PredictStrategy, FlairPredictStrategy

Sentence = str

TEXT_BLOCK = 0


def list_entities(src_pdf) -> List[Tuple[Sentence, Union[None, Span]]]:
    span_by_line_over_doc = []
    translation_table = str.maketrans('', '', r',')
    with fitz.Document(src_pdf) as doc:
        for page in doc:
            page.wrap_contents()
            lines = [text.replace('\n', ' ').translate(translation_table)
                     for _, _, _, _, text, _, block_type in page.getText('blocks')
                     if TEXT_BLOCK == block_type]

            span_by_line = _get_sensitive_span_by_line(lines, FlairPredictStrategy())
            span_by_line_over_doc.extend(span_by_line)
    return span_by_line_over_doc


def _get_sensitive_span_by_line(lines: List[Sentence], strategy: PredictStrategy) \
        -> List[Tuple[Sentence, Union[None, Span]]]:
    span_list_by_line = [(line, strategy.list_predictions(line)) for line in lines]
    span_list_by_line = map(lambda x: (x[0], [None] if not x[1] else x[1]),
                            span_list_by_line)
    span_by_line = [(line, span) for line, spans in span_list_by_line for span in spans]
    return span_by_line


def write_debug_file(all_sensitives_spans: List[Tuple[Sentence, Union[None, Span]]], dest):
    debug_filename = os.path.splitext(dest)[0] + '_debug.csv'
    with open(debug_filename, 'w') as debug_file:
        debug_writer = csv.writer(debug_file, delimiter=',',
                                  quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for line, span in all_sensitives_spans:
            text = '' if not span else span.text
            label = '' if not span else span.label
            debug_writer.writerow([line, text, label])


def write_debug_spreadsheet(all_sensitives_spans: List[Tuple[Sentence, Union[None, Span]]], dest):
    workbook = Workbook()
    sheet: Worksheet = workbook.active
    sheet.append(['Text Line', 'Entity Text', 'Entity Label'])
    header = NamedStyle(name="header")
    header.font = Font(bold=True)
    header.border = Border(bottom=Side(border_style="thin"))
    header.alignment = Alignment(horizontal="center", vertical="center")
    sheet.column_dimensions['A'].width = 100
    sheet.column_dimensions['A'].alignment = Alignment(wrapText=True)

    for cell in sheet[1]:
        cell.style = header
    for row_number, sentence, span in map(lambda x: (x[0] + 2, *x[1]), enumerate(all_sensitives_spans)):
        sheet.append([sentence] + (['', ''] if not span else [span.text, span.label]))
        sheet.row_dimensions[row_number].height = 25 if len(sentence) > 115 else None

    adjusted_width = (max([len(span.text) for _, span in all_sensitives_spans if span is not None])) * 1.1
    sheet.column_dimensions['B'].width = adjusted_width
    adjusted_width = (max(
        [len(span.label) for _, span in all_sensitives_spans if span is not None] + [len('Entity Label')])) * 1.1
    sheet.column_dimensions['C'].width = adjusted_width

    workbook.save(filename=dest)


def write_style_frame(all_sensitives_spans: List[Tuple[Sentence, Union[None, Span]]], dest):
    df = pd.DataFrame({
        'Text': [sentence for sentence, _ in all_sensitives_spans],
        'Entity': [('' if not span else span.text) for _, span in all_sensitives_spans],
        'Label': [('' if not span else span.label) for _, span in all_sensitives_spans],
    })
    sf = StyleFrame(df)
    header_style = Styler(bold=True, font_size=18)
    sf.apply_headers_style(styler_obj=header_style)

    adjusted_width = (max([len(span.text) for _, span in all_sensitives_spans if span is not None])) * 1.1
    sf.set_column_width(columns='Entity', width=adjusted_width)

    adjusted_width = (max(
        [len(span.label) for _, span in all_sensitives_spans if span is not None] + [len('Entity Label')])) * 1.1
    sf.set_column_width(columns='Label', width=adjusted_width)

    sf.set_column_width(columns='Text', width=100)
    sf.set_row_height(rows=[1], height=25)
    sf.set_row_height(rows=[(idx + 2) for idx, sentence_span_tuple in enumerate(all_sensitives_spans)
                            if len(sentence_span_tuple[0]) > 115],
                      height=50)

    sf.to_excel(dest).save()


if __name__ == "__main__":
    entities = list_entities('data/CV6.pdf')
    write_style_frame(entities, 'data/CV6.xlsx')
