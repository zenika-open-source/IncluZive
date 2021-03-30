from dataclasses import dataclass
from typing import List, Union, Tuple

import pandas as pd
from styleframe import StyleFrame, Styler

from src.predict_strategy import Span

TEXT_BLOCK = 0


@dataclass
class Sentence:
    text: str
    rect: Tuple[float, float, float, float]
    page_num: int


def write_style_frame(
        all_sensitives_spans: List[Tuple[Sentence, Union[None, Span]]], dest
):
    df = pd.DataFrame(
        {
            "Text": [sentence.text for sentence, _ in all_sensitives_spans],
            "page": [sentence.page_num for sentence, _ in all_sensitives_spans],
            "x1": [sentence.rect[0] for sentence, _ in all_sensitives_spans],
            "y1": [sentence.rect[1] for sentence, _ in all_sensitives_spans],
            "x2": [sentence.rect[2] for sentence, _ in all_sensitives_spans],
            "y2": [sentence.rect[3] for sentence, _ in all_sensitives_spans],
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

    adjusted_width = max([len(span.text) for _, span in all_sensitives_spans if span is not None]) * 1.1
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
            if len(sentence_span_tuple[0].text) > 115
        ],
        height=50,
    )

    sf.to_excel(dest).save()
