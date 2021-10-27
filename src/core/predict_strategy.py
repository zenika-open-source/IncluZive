import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterator

import phonenumbers
import cv2
import numpy as np

import spacy
from flair.data import Sentence
from flair.models import SequenceTagger
from spacy.pipeline import EntityRuler


@dataclass
class Span:
    text: str
    label: str = None


class PredictStrategy(ABC):
    spacy_entities_list = []

    @abstractmethod
    def predict(self, lines: str) -> Iterator[Span]:
        pass

    def list_predictions(self, line):
        return list(self.predict(line))


class FlairPredictStrategy(PredictStrategy):
    def __init__(self):
        self._model = SequenceTagger.load("fr-ner")
        self.lang_list = []
        self.skills_list = ["Jenkins", "Docker", "Newman", "Kafka"]

    def predict(self, line: str) -> Iterator[Span]:
        sentence = Sentence(line)
        self._model.predict(sentence)
        for entity in sentence.get_spans("ner"):
            for word in LANG_PATTERN_STRATEGIES[0].predict(str((entity[0]))):
                self.lang_list.append(word.text)
            if (
                entity.tag in ["PER", "LOC"]
                and entity.score > 0.7
                and not (any(entity.text in s for s in self.spacy_entities_list))
                and entity.text not in self.lang_list + self.skills_list
            ):
                yield Span(entity.to_original_text(), entity.tag)


class SpacyPredictStrategy(PredictStrategy):
    def __init__(self):
        self._nlp = spacy.load("fr_core_news_md")
        # self._matcher = Matcher(self._nlp.vocab)
        self.ruler = EntityRuler(self._nlp, overwrite_ents=True)
        self.adrs_prefix = "^[Rr]ue|^[Pp]lace|^[Cc]hemin|^[Pp]lace|^[Aa]v$|^[Aa]venue|^[Ii]mpasse"
        self.org_prefix = "^[EÉé]cole|^[Uu]niversité|^[Pp]olytech|^UNIVERSITÉ|^ECOLE|^Grandes Écoles"
        self.org_prefix_2 = "^ENI|^INSA|^I.U.T|^IUT|^I.U.P|^IUP"
        self.pattern = [
            {
                "label": "ADDRESS",
                "pattern": [
                    {"TEXT": {"REGEX": self.adrs_prefix}},
                    {"TEXT": {"REGEX": "de|du|aux"}, "OP": "?"},
                    {"ENT_TYPE": {"IN": ["PER", "LOC", "ORG"]}, "OP": "+"},
                ],
            },
            {
                "label": "ORG_ENS",
                "pattern": [
                    {"TEXT": {"REGEX": self.org_prefix + "|" + self.org_prefix_2}},
                    {"TEXT": {"REGEX": "de"}, "OP": "?"},
                    {"ENT_TYPE": {"IN": ["PER", "LOC", "MISC", "ORG"]}, "OP": "+"},
                    {"TEXT": {"REGEX": "-"}, "OP": "?"},
                    {"ENT_TYPE": {"IN": ["LOC", "MISC"]}, "OP": "*"},
                    {"TEXT": {"REGEX": "D’|de|et"}, "OP": "?"},
                    {"ENT_TYPE": {"IN": ["PER", "LOC", "ORG"]}, "OP": "*"},
                ],
            },
        ]
        self.ruler.add_patterns(self.pattern)
        self._nlp.add_pipe(self.ruler)

    def predict(self, line: str) -> Iterator[Span]:
        doc = self._nlp(line)
        for ent in doc.ents:
            if ent.label_ in ["ADDRESS", "ORG_ENS"]:
                self.spacy_entities_list.append(ent.text)
                yield Span(ent.text, ent.label_)


class ChainPredictStrategy(PredictStrategy):
    def __init__(self, strategies):
        self._strategies = strategies

    def predict(self, line: str) -> Iterator[Span]:
        for strategy in self._strategies:
            for prediction in strategy.predict(line):
                yield prediction


class RegexPredictStrategy(PredictStrategy):
    def __init__(self, pattern: str, label: str):
        self._pattern = re.compile(pattern)
        self._label = label

    def predict(self, line: str) -> Iterator[Span]:
        for span in self._pattern.finditer(line):
            start, end = span.span()
            yield Span(line[start:end], self._label)


class PhoneNumberPredictStrategy(PredictStrategy):
    def __init__(self, region):
        self._region = region

    def predict(self, line: str) -> Iterator[Span]:
        for match in phonenumbers.PhoneNumberMatcher(line, region=self._region):
            yield Span(match.raw_string, "TEL")


PATTERN_STRATEGIES = [
    RegexPredictStrategy(pattern=r"[\w\.-]+[@]\w+[.]\w{2,4}([.]\w{2,4})*", label="EMAIL"),  # extract_email
    RegexPredictStrategy(
        pattern=r"(0*[1-9]|[12][0-9]|3[01])[-/](0[1-9]|1[012])[-/](19|20)*\d\d",
        label="DATE",
    ),
    # extract_date
    RegexPredictStrategy(pattern=r"\d\s*\d{2}\s*\d{2}\s*\d{2}\s*\d{3}\s*\d{3}", label="NSEC"),  # extract_num_so_sec
    # RegexPredictStrategy(pattern=r' ([0-9][0-9][0-9][0-9] )|(\s*\d{4}-\d{4}\s*)', label=),  # extract_single_date
    RegexPredictStrategy(
        pattern=r"\d\.*\,*?\d*?\s?\s?(ans|ANS|an\b|AN\b|mois\b|MOIS\b|années\b)(\set demi)*", label="PERIODE"
    ),  # extract_time_period
    RegexPredictStrategy(pattern=r"([0-99]+?)\s*enfants", label="CHILDREN"),  # extract_enfants
    RegexPredictStrategy(
        pattern=r"[Mm]arié(e?)|[Pp]acsé(e?)|[Dd]ivorcé(e?)|[Ss]éparé(e?)|[Cc]élibataire",
        label="FAMILY_STATUS",
    ),  # extract_sit_fam
    RegexPredictStrategy(
        pattern=r"((\s)(\()*(Féminin)(\))*(\s))|((\s)(\()*(Masculin)(\))*(\s))",
        label="GENDER",
    ),
    # extract_sexe
    # RegexPredictStrategy(pattern=r'((\s)(\()*(F)(\))*(\s))|((\s)(\()*(M)(\))*(\s))', label=),  # extract_sexe_abrev
    # PhoneNumberPredictStrategy(region="FR"), # deanonymizing phone number for this branch [deanonimizing-phone-number]
    RegexPredictStrategy(
        pattern=r"(?i)\b((?:https?://\s?|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+"
        r"|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))",
        label="URL",
    ),  # extract_url
]

LANG_PATTERN_STRATEGIES = [
    RegexPredictStrategy(
        pattern=r"Mandarin|MANDARIN|Hindi|HINDI|Espagnol|ESPAGNOL|Arabe|ARABE|Bengali|BENGALI|Russe"
        r"|RUSSE|Portugais|PORTUGAIS|Indonésien|INDONESIEN|Urdu|URDU|Allemand|ALLEMAND"
        r"|Japonais|JAPONAIS|Swahili|SWAHILI|Marathi|MARATHI|Télougou|TELOUGOU|Punjabi"
        r"|PUNJABI|Chinois Wu|CHINOIS WU|Tamoul|TAMOUL|Turc|TURC|Roumain|ROUMAIN|"
        r"Italien|ITALIEN|Chinois|CHINOIS|Kabyle|KABYLE|Vietnamien|VIETNAMIEN|Brésilien|BRESILIEN|Suédois|SUEDOIS",
        label="LANG",
    ),
]
STRATEGY = ChainPredictStrategy(
    LANG_PATTERN_STRATEGIES + PATTERN_STRATEGIES + [SpacyPredictStrategy(), FlairPredictStrategy()]
)


class FaceImagePredictor:
    def __init__(self):
        self._face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    def predict(self, image: bytes) -> bool:
        image_arr = np.frombuffer(image, dtype=np.uint8)
        image_np = cv2.imdecode(image_arr, flags=cv2.IMREAD_COLOR)
        gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)
        faces = self._face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
            # flags = cv2.CV_HAAR_SCALE_IMAGE
        )
        return len(faces) > 0
