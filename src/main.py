import argparse
from typing import List

import fitz
import flair
import regex as re
from flair.data import Sentence
from flair.models import SequenceTagger

model = SequenceTagger.load('fr-ner')

page_render_matrix = fitz.Matrix(fitz.Identity)
page_render_matrix.preScale(2, 2)


def anonymize(token: flair.data.Token):
    return ''.ljust(len(token.text), 'x')


def is_token_per(token):
    return any([v.value.endswith('-PER') for _, values in token.annotation_layers.items()
                for v in values])


def build_content_filters(analysis: List[str]):
    filters = [(re.compile(rf"\{token}"), lambda m: ''.ljust(len(token), '-')) for token in analysis]
    return filters


def get_sensitive_data(lines: List[str]):
    sensitive = []
    for line in lines:
        sentence = Sentence(line)
        model.predict(sentence)
        # print(txt.to_tagged_string())
        for entity in sentence.get_spans('ner'):
            if entity.tag == 'PER' and entity.score > 0.7:
                sensitive.append(entity.to_original_text())
    return sensitive


TEXT_BLOCK = 0


def main(src, dest):
    # opening the pdf
    doc = fitz.Document(src)
    new_doc = fitz.Document()

    # iterating through pages
    for page in doc:
        page.wrap_contents()
        lines = [lines.replace('\n', ' ')
                 for _, _, _, _, lines, _, block_type in page.getText('blocks')
                 if TEXT_BLOCK == block_type]
        sensitive = get_sensitive_data(lines)
        for data in sensitive:
            areas = page.searchFor(data)

            # drawing outline over sensitive datas
            # [page.addRedactAnnot(area, fill=(0, 0, 0), cross_out=False) for area in areas]
            [page.drawRect(area, color=(0, 0, 0), fill=(0, 0, 0), overlay=True) for area in areas]

        pix = page.getPixmap(alpha=False, matrix=page_render_matrix)  # render page to an image
        new_page = new_doc.newPage(page.number)
        new_page.insertImage(new_page.rect, pixmap=pix)

        # applying the redaction
        # page.apply_redactions()

    new_doc.save(dest)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('src', help='PDF source')
    parser.add_argument('dest', help='PDF destination')
    args = parser.parse_args()
    main(args.src, args.dest)
