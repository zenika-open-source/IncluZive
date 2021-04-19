from dataclasses import dataclass
from typing import Tuple, List, Iterator

from openpyxl.worksheet.worksheet import Worksheet
from styleframe import StyleFrame, Styler


@dataclass
class Sentence:
    text: str
    rect: Tuple[float, float, float, float]
    page_num: int


def write_style_frame(data_frame, dest):
    sf = StyleFrame(data_frame)
    header_style = Styler(bold=True, font_size=18)
    sf.apply_headers_style(styler_obj=header_style)

    # adjusted_width = max([len(span.text) for _, span in all_sensitives_spans if span is not None]) * 1.1
    adjusted_width = data_frame["Entity"].fillna("").apply(len).max() * 1.1
    sf.set_column_width(columns="Entity", width=adjusted_width)

    adjusted_width = data_frame["Label"].fillna("").apply(len).max() * 2.0
    sf.set_column_width(columns="Label", width=adjusted_width)

    sf.set_column_width(columns="Text", width=100)
    sf.set_row_height(rows=[1], height=25)
    rows_with_large_text = [
        (idx + 2) for idx, tuples in enumerate(data_frame.itertuples(index=False)) if len(tuples.Text) > 80
    ]
    sf.set_row_height(
        rows=rows_with_large_text,
        height=50,
    )

    sf.to_excel(dest).save()


def load_annotations(sheet: Worksheet) -> Iterator[Tuple[str, List[Tuple[str, str]]]]:
    pass
