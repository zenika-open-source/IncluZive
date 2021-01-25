from typing import Iterator

import pytest

from src.debug_generation import _get_sensitive_span_by_line
from src.predict_strategy import PredictStrategy, Span


class FakePredictionStrategy(PredictStrategy):
    def __init__(self, predictions=None):
        self._predictions = predictions or []

    def predict(self, line: str) -> Iterator[Span]:
        return (x for x in self._predictions)


test_data = [
    (['line A'], [], [('line A', None)]),
    (['line A', 'line B'], [], [('line A', None), ('line B', None)]),
    (['line A'], [Span('span1', 'label1')], [('line A', Span('span1', 'label1'))]),
]


@pytest.mark.parametrize("lines,spans,expected", test_data)
def test_get_sensitive_span_by_line(lines, spans, expected):
    span_by_line = _get_sensitive_span_by_line(lines, FakePredictionStrategy(predictions=spans))
    assert span_by_line == expected
