import csv
import os
import string
from typing import List, Union, Tuple

import fitz

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


if __name__ == "__main__":
    entities = list_entities('data/CV BAILLEUL Valentin.pdf')
    write_debug_file(entities, 'data/CV BAILLEUL Valentin.csv')
