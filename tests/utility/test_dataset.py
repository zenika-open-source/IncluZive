from typing import List, Tuple

import pytest

from utility import dataset as dataset


@pytest.mark.parametrize(
    "text, annotations, iob_tags",
    [
        ("I like London", [("London", "LOCATION")], [("I", "O"), ("like", "O"), ("London", "B-LOCATION")]),
        (
            "I like London and Berlin",
            [("London", "LOCATION"), ("Berlin", "LOCATION")],
            [("I", "O"), ("like", "O"), ("London", "B-LOCATION"), ("and", "O"), ("Berlin", "B-LOCATION")],
        ),
        (
            "Who is Shaka Khan",
            [("Shaka Khan", "PER")],
            [("Who", "O"), ("is", "O"), ("Shaka", "B-PER"), ("Khan", "I-PER")],
        ),
    ],
)
def test_annotation_to_iob_tags(text: str, annotations: List[Tuple[str, str]], iob_tags: List[Tuple[str, str]]):
    assert dataset.annotation_to_bio_tags(text, annotations) == iob_tags
