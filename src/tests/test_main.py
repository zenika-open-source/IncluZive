from typing import Iterator

import pytest

from src.workbook import Sentence
from src.main import _get_sensitive_span_by_line
from src.predict_strategy import PredictStrategy, Span


class FakePredictionStrategy(PredictStrategy):
    def __init__(self, predictions=None):
        self._predictions = predictions or []

    def predict(self, line: str) -> Iterator[Span]:
        return (x for x in self._predictions)


def build_sentence(text: str) -> Sentence:
    return Sentence(text, None, None)


test_data = [
    ([build_sentence("line A")], [], [(build_sentence("line A"), None)]),
    (
        [build_sentence("line A"), build_sentence("line B")],
        [],
        [(build_sentence("line A"), None), (build_sentence("line B"), None)],
    ),
    ([build_sentence("line A")], [Span("span1", "label1")], [(build_sentence("line A"), Span("span1", "label1"))]),
]


@pytest.mark.parametrize("lines,spans,expected", test_data)
def test_get_sensitive_span_by_line(lines, spans, expected):
    span_by_line = _get_sensitive_span_by_line(lines, FakePredictionStrategy(predictions=spans))
    assert span_by_line == expected
