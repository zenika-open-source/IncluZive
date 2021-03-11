import pytest
from src.predict_strategy import RegexPredictStrategy


@pytest.mark.parametrize(
    "test_url",
    [
        "https://regex101.com/r/wcSXEr/5/",
        "https://regexsf101.com/r/wcSXsfEr/5/",
        "www.lala.com",
    ],
)
def test_RegexPredictStrategy_URL(test_url):
    my_regex = r"""(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+
    |(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"""
    strat = RegexPredictStrategy(pattern=my_regex, label="URL")
    assert strat.predict(test_url)


@pytest.mark.parametrize("test_periode", [" - 8 ans", " 6 mois", "(5 ans)", "(1 an)"])
def test_RegexPredictStrategy_PERIODE(test_periode):
    my_regex = r"[0-99]+?\s*(ans\b|an\b|mois\b)"
    strat = RegexPredictStrategy(pattern=my_regex, label="PERIODE")
    assert strat.predict(test_periode)
