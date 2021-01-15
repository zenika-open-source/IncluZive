import argparse

import fitz
from flair.models import SequenceTagger

from predict_strategy import FlairPredictStrategy, SpacyPredictStrategy, RegexPredictStrategy, ChainPredictStrategy

model = SequenceTagger.load('fr-ner')

page_render_matrix = fitz.Matrix(fitz.Identity)
page_render_matrix.preScale(2, 2)

TEXT_BLOCK = 0


def main(src, dest, apply_redactions=False):
    strategy = ChainPredictStrategy([FlairPredictStrategy(),RegexPredictStrategy()])
    # opening the pdf
    doc = fitz.Document(src)
    # iterating through pages
    for page in doc:
        page.wrap_contents()
        lines = [lines.replace('\n', ' ')
                 for _, _, _, _, lines, _, block_type in page.getText('blocks')
                 if TEXT_BLOCK == block_type]
        sensitive = strategy.predict(lines)
        for data in sensitive:
            areas = page.searchFor(data)

            if apply_redactions:
                [page.drawRect(area, color=(0, 0, 0), fill=(0, 0, 0), overlay=True) for area in areas]
            else:
                [page.addRedactAnnot(area, fill=(0, 0, 0), cross_out=False) for area in areas]

    if apply_redactions:
        new_doc = fitz.Document()
        for page in doc:
            pix = page.getPixmap(alpha=False, matrix=page_render_matrix)  # render page to an image
            new_page = new_doc.newPage(page.number)
            new_page.insertImage(new_page.rect, pixmap=pix)
            # applying the redaction
            # page.apply_redactions()
        new_doc.save(dest)
    else:
        # for page in doc:
        #     page.apply_redactions()
        doc.save(dest)


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
    add_bool_arg(parser, 'apply-redactions')
    args = parser.parse_args()
    main(args.src, args.dest, args.apply_redactions)
