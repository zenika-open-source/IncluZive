import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Iterator

import spacy
from flair.data import Sentence
from flair.models import SequenceTagger
from spacy.matcher import Matcher
from spacy.tokens import Span as SpacySpan


@dataclass
class Span:
    text: str
    label: str = None


class PredictStrategy(ABC):
    @abstractmethod
    def predict(self, lines: List[str]) -> Iterator[Span]:
        pass


class FlairPredictStrategy(PredictStrategy):
    def __init__(self):
        self._model = SequenceTagger.load('fr-ner')

    def predict(self, lines: List[str]) -> Iterator[Span]:
        for line in lines:
            sentence = Sentence(line)
            self._model.predict(sentence)
            # print(txt.to_tagged_string())
            for entity in sentence.get_spans('ner'):
                if entity.tag == 'PER' and entity.score > 0.7:
                    yield Span(entity.to_original_text(), entity.tag)


class SpacyPredictStrategy(PredictStrategy):
    def __init__(self):
        self._nlp = spacy.load('fr_core_news_md')
        self._matcher = Matcher(self._nlp.vocab)

        def create_add_ent_fn(ent_label):
            def _add_ent(matcher, doc, i, matches):
                match_id, start, end = matches[i]
                entity = SpacySpan(doc, start, end, label=ent_label)
                doc.ents += (entity,)

            return _add_ent

        self._matcher.add('mail', create_add_ent_fn('EMAIL'), [{'LIKE_EMAIL': True}])
        self._matcher.add('age', create_add_ent_fn('AGE'), [{}, {'ORTH': 'ans'}])
        self._matcher.add('familiale', create_add_ent_fn('FAM'),
                          [{'TEXT': {'REGEX': '[Mm]arié(e?)'}}])

    def predict(self, lines: str) -> Iterator[Span]:
        for line in lines:
            doc = self._nlp(line)
            _ = self._matcher(doc)
            for ent in doc.ents:
                if ent.label_ in ['PER', 'EMAIL', 'TEL', 'AGE', 'FAM']:
                    yield Span(ent.text, ent.label_)


class ChainPredictStrategy(PredictStrategy):

    def __init__(self, strategies):
        self._strategies = strategies

    def predict(self, lines: List[str]) -> Iterator[Span]:
        for strategy in self._strategies:
            for prediction in strategy.predict(lines):
                yield prediction


class RegexPredictStrategy(PredictStrategy):

    def __init__(self, pattern: str, label: str):
        self._pattern = re.compile(pattern)
        self._label = label

    def predict(self, lines: List[str]) -> Iterator[Span]:
        for line in lines:
            for span in self._pattern.finditer(line):
                start, end = span.span()
                yield Span(line[start: end], self._label)
