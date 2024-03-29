import argparse
import glob
import os
import random
from typing import Tuple, List

from openpyxl import load_workbook

from core.workbook import load_annotations


def annotation_to_bio_tags(text: str, annotations: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
    token_dict = {token: "O" for token in text.split()}
    tagged_tokens = [(annotation[0].split(), annotation[1]) for annotation in annotations]
    tagged_tokens = [
        (token, f"{'I' if i > 0 else 'B'}-{tag}") for tokens, tag in tagged_tokens for i, token in enumerate(tokens)
    ]
    token_dict.update(tagged_tokens)
    return list(token_dict.items())


def create_train_test_dataset_from_workbooks(
    workbooks: List[str], train_file: str, test_file: str, split: float = 0.2, seed: int = 3
):
    """
    Write train/test files from workbooks in CoNLL column-format
    """
    worksheets = (load_workbook(file).active for file in workbooks)
    annotated_texts = [annotation for sheet in worksheets for annotation in load_annotations(sheet)]
    random.seed(seed)
    random.shuffle(annotated_texts)
    split_idx = int(split * len(annotated_texts))

    end_of_sentence_tag = (None, None)

    def to_bio_tags(part):
        return (
            tag
            for text, annotations in part
            for tag in (annotation_to_bio_tags(text, annotations) + [end_of_sentence_tag])
        )

    test_bio_tags = to_bio_tags(annotated_texts[:split_idx])
    train_bio_tags = to_bio_tags(annotated_texts[split_idx:])

    with open(train_file, "w") as file:
        lines = (f"{token} {bio_tag}\n" if token else "\n" for token, bio_tag in train_bio_tags)
        file.writelines(lines)

    with open(test_file, "w") as file:
        lines = (f"{token} {bio_tag}\n" if token else "\n" for token, bio_tag in test_bio_tags)
        file.writelines(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("src", help="Annotated workbooks")
    parser.add_argument("dest", help="Destination directory")
    parser.add_argument("--split", help="Split data", type=float)
    parser.add_argument("--seed", help="seed value", type=int)
    args = parser.parse_args()

    workbook_files = glob.glob(os.path.join(args.src, "*.xlsx")) if os.path.isdir(args.src) else [args.src]
    create_train_test_dataset_from_workbooks(
        workbook_files,
        train_file=args.dest + "/train.txt",
        test_file=args.dest + "/test.txt",
        split=args.split,
        seed=args.seed,
    )
