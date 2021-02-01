import argparse
import csv
import glob
import os
from os import path

import fitz

from src.predict_strategy import STRATEGY_FLAIR as strategy, FaceImagePredictor

page_render_matrix = fitz.Matrix(fitz.Identity)
page_render_matrix.preScale(2, 2)

BLOCK_TEXT = 0
BLOCK_IMAGE = 1

face_image_predictor = FaceImagePredictor()


def main(src, dest, apply_redaction=False, redaction_with_annotation=True):
    all_sensitives_spans = []
    doc = fitz.Document(src)
    for page in doc:
        page.wrap_contents()
        lines = [text.replace('\n', ' ')
                 for _, _, _, _, text, _, block_type in page.getText('blocks')
                 if BLOCK_TEXT == block_type]
        sensitive_spans = [(line, span)
                           for line in lines
                           for span in strategy.predict(line)]
        for _, span in sensitive_spans:
            areas = page.searchFor(span.text)
            add_annotations(page, areas, redaction_with_annotation)
        all_sensitives_spans.extend(sensitive_spans)

        image_blocks = [block for block in page.getText('dict')['blocks']
                        if block['type'] == BLOCK_IMAGE]
        face_image_boxes = [block['bbox'] for block in image_blocks if face_image_predictor.predict(block['image'])]
        add_annotations(page, face_image_boxes, redaction_with_annotation)

    save_redacted_doc(doc, dest, apply_redaction, redaction_with_annotation)

    write_debug_file(all_sensitives_spans, dest)


def add_annotations(page, boxes, redaction_with_annotation):
    if redaction_with_annotation:
        [page.drawRect(rect, color=(0, 0, 0), fill=(1, 1, 1), overlay=True) for rect in boxes]
    else:
        [page.addRedactAnnot(rect, fill=(1, 1, 1), cross_out=False) for rect in boxes]


def save_redacted_doc(doc, dest, apply_redaction, redaction_with_annotation):
    if redaction_with_annotation and apply_redaction:
        new_doc = fitz.Document()
        for page in doc:
            pix = page.getPixmap(alpha=False, matrix=page_render_matrix)  # render page to an image
            new_page = new_doc.newPage(page.number)  # noqa
            new_page.insertImage(new_page.rect, pixmap=pix)
            # applying the redaction
            # page.apply_redactions()
        new_doc.save(dest)
    else:
        if apply_redaction:
            for page in doc:
                page.apply_redactions()
        doc.save(dest)


def write_debug_file(all_sensitives_spans, dest):
    debug_filename = os.path.splitext(dest)[0] + '_debug.csv'
    with open(debug_filename, 'w') as debug_file:
        debug_writer = csv.writer(debug_file, delimiter=';',
                                  quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for line, span in all_sensitives_spans:
            debug_writer.writerow([line, span.text, span.label])


def add_bool_arg(arg_parser, name, default=False):
    var_name = name.replace('-', '_')
    group = arg_parser.add_mutually_exclusive_group(required=False)
    group.add_argument('--' + name, dest=var_name, action='store_true')
    group.add_argument('--no-' + name, dest=var_name, action='store_false')
    arg_parser.set_defaults(**{var_name: default})


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('src', help='PDF source')
    parser.add_argument('dest', help='PDF destination')
    add_bool_arg(parser, 'apply-redaction')
    add_bool_arg(parser, 'redaction-with-annotation')
    args = parser.parse_args()

    src_files = (glob.glob(os.path.join(args.src, '*.pdf'))
                 if os.path.isdir(args.src) else [args.src])
    dest_files = ['ano_' + path.basename(src) for src in src_files]
    dest_files = [os.path.join(args.dest, filename) for filename in dest_files]

    for src, dest in zip(src_files, dest_files):
        main(src, dest, args.apply_redaction, args.redaction_with_annotation)
