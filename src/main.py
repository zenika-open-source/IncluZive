import argparse
import glob
import os
from os import path
from typing import List, Union, Tuple

import fitz
import pandas as pd

from workbook import write_style_frame, Sentence
from predict_strategy import (
    STRATEGY_FLAIR,
    FaceImagePredictor,
    Span,
    PredictStrategy,
)

page_render_matrix = fitz.Matrix(fitz.Identity)
page_render_matrix.preScale(2, 2)

BLOCK_TEXT = 0
BLOCK_IMAGE = 1

face_image_predictor = FaceImagePredictor()


def main(src, output_path, apply_redaction=False, redaction_with_annotation=True):
    all_sensitives_spans = []
    doc = fitz.Document(src)
    for page in doc:
        page.wrap_contents()
        lines = get_lines(page)
        span_by_line = _get_sensitive_span_by_line(lines, STRATEGY_FLAIR)
        for _, span in span_by_line:
            if not span:
                continue
            areas = page.searchFor(span.text)  # noqa
            add_annotations(page, areas, redaction_with_annotation)
        all_sensitives_spans.extend(span_by_line)

        image_blocks = [block for block in page.getText("dict")["blocks"] if block["type"] == BLOCK_IMAGE]  # noqa
        face_image_boxes = [block["bbox"] for block in image_blocks if face_image_predictor.predict(block["image"])]
        add_annotations(page, face_image_boxes, redaction_with_annotation)

    save_redacted_doc(doc, output_path, apply_redaction, redaction_with_annotation)

    df = to_data_frame(all_sensitives_spans)
    write_style_frame(df, output_path.replace("pdf", "xlsx"))


def to_data_frame(all_sensitives_spans: List[Tuple[Sentence, Union[None, Span]]]):
    df = pd.DataFrame(
        {
            "Text": [sentence.text for sentence, _ in all_sensitives_spans],
            "page": [sentence.page_num for sentence, _ in all_sensitives_spans],
            "x1": [sentence.rect[0] for sentence, _ in all_sensitives_spans],
            "y1": [sentence.rect[1] for sentence, _ in all_sensitives_spans],
            "x2": [sentence.rect[2] for sentence, _ in all_sensitives_spans],
            "y2": [sentence.rect[3] for sentence, _ in all_sensitives_spans],
            "Entity": [("" if not span else span.text) for _, span in all_sensitives_spans],
            "Label": [("" if not span else span.label) for _, span in all_sensitives_spans],
        }
    )
    return df


def add_annotations(page, boxes, redaction_with_annotation):
    if redaction_with_annotation:
        [page.drawRect(rect, color=(0, 0, 0), fill=(1, 1, 1), overlay=True) for rect in boxes]
    else:
        [page.addRedactAnnot(rect, fill=(1, 1, 1), cross_out=False) for rect in boxes]


def save_redacted_doc(doc, output_path, apply_redaction, redaction_with_annotation):
    if redaction_with_annotation and apply_redaction:
        new_doc = fitz.Document()
        for page in doc:
            pix = page.getPixmap(alpha=False, matrix=page_render_matrix)  # render page to an image
            new_page = new_doc.newPage(page.number)  # noqa
            new_page.insertImage(new_page.rect, pixmap=pix)
            # applying the redaction
            # page.apply_redactions()
        new_doc.save(output_path)
    else:
        if apply_redaction:
            for page in doc:
                page.apply_redactions()
        doc.save(output_path)


def get_lines(page) -> Sentence:
    return [
        Sentence(text.replace("\n", " "), (x1, y1, x2, y2), page.number)
        for x1, y1, x2, y2, text, _, block_type in page.getText("blocks")
        if BLOCK_TEXT == block_type
    ]


def _get_sensitive_span_by_line(
    lines: List[Sentence], predict_strategy: PredictStrategy
) -> List[Tuple[Sentence, Union[None, Span]]]:
    span_list_by_line = [(line, predict_strategy.list_predictions(line.text)) for line in lines]

    span_list_by_line = map(lambda x: (x[0], [None] if not x[1] else x[1]), span_list_by_line)
    span_by_line = [(line, span) for line, spans in span_list_by_line for span in spans]

    return span_by_line


def add_bool_arg(arg_parser, name, default=False):
    var_name = name.replace("-", "_")
    group = arg_parser.add_mutually_exclusive_group(required=False)
    group.add_argument("--" + name, dest=var_name, action="store_true")
    group.add_argument("--no-" + name, dest=var_name, action="store_false")
    arg_parser.set_defaults(**{var_name: default})


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("src", help="PDF source")
    parser.add_argument("dest", help="PDF destination")
    add_bool_arg(parser, "apply-redaction")
    add_bool_arg(parser, "redaction-with-annotation")
    args = parser.parse_args()

    src_files = glob.glob(os.path.join(args.src, "*.pdf")) if os.path.isdir(args.src) else [args.src]
    dest_files = ["ano_" + path.basename(src) for src in src_files]
    dest_files = [os.path.join(args.dest, filename) for filename in dest_files]

    for src, dest in zip(src_files, dest_files):
        main(src, dest, args.apply_redaction, args.redaction_with_annotation)
