import argparse
from typing import Generator, List

import flair
import regex as re
from flair.data import Sentence
from flair.models import SequenceTagger
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTPage

import pdf_redactor


def anonymize(token: flair.data.Token):
    return ''.ljust(len(token.text), 'x')


def is_token_per(token):
    return any([v.value.endswith('-PER') for _, values in token.annotation_layers.items()
                for v in values])


def analyse_document(pages: Generator[LTPage, None, None]) -> List[str]:
    analysis = []
    model = SequenceTagger.load('fr-ner')
    for page_layout in pages:
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                txt = Sentence(element.get_text())
                model.predict(txt)
                # print(txt.to_tagged_string())
                for token in txt.tokens:
                    # for label_type, values in token.annotation_layers.items():
                    #     print(label_type, [v.value for v in values])
                    if is_token_per(token):
                        analysis.append(token.text)
                        # print(element.get_text())
                        # print(token.text)
                        # print(anonymize(token))
    return analysis


def build_content_filters(analysis: List[str]):
    filters = [(re.compile(rf"\{token}"), lambda m: ''.ljust(len(token), '-')) for token in analysis]
    return filters


def anonymize_document(in_path, analysis: List[str], out_path):
    options = pdf_redactor.RedactorOptions()
    options.input_stream = in_path
    options.output_stream = out_path
    options.content_filters = build_content_filters(analysis)
    pdf_redactor.redactor(options)


def main(src, dest):
    with open(src, 'rb') as file:
        pages: Generator[LTPage, None, None] = extract_pages(file)
        analysis = analyse_document(pages)
    anonymize_document(src, analysis, dest)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('src', help='PDF source')
    parser.add_argument('dest', help='PDF destination')
    args = parser.parse_args()
    main(args.src, args.dest)
