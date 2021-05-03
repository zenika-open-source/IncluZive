import pytest

from predict_strategy import RegexPredictStrategy


@pytest.mark.parametrize(
    "test_url",
    [
        "https://regex101.com/r/wcSXEr/5/",
        "https://regexsf101.com/r/wcSXsfEr/5/",
        "www.lala.com",
        "julien.wordpress.com",
        "http:// julien.blogspot.fr",
    ],
)
def test_RegexPredictStrategy_URL(test_url):
    strat = RegexPredictStrategy(
        pattern=r"(?i)\b((?:https?://\s?|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+"
        r"|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))",
        label="URL",
    )
    assert strat.predict(test_url)


@pytest.mark.parametrize("test_periode", [" - 8 ans", "(1 an)", "	1 an et demi", "9 années", "1.5 mois", "4,5 ANS"])
def test_RegexPredictStrategy_PERIODE(test_periode):
    my_regex = r"\d\.*\,*?\d*?\s?\s?(ans|ANS|an\b|AN\b|mois\b|MOIS\b|années\b)(\set demi)*"
    strat = RegexPredictStrategy(pattern=my_regex, label="PERIODE")
    assert strat.predict(test_periode)


@pytest.mark.parametrize("test_date", ["07/12/78", "5/10/2006", "3/12/2003"])
def test_RegexPredictStrategy_DATE(test_date):
    my_regex = r"(0*[1-9]|[12][0-9]|3[01])[-/](0[1-9]|1[012])[-/](19|20)*\d\d"
    strat = RegexPredictStrategy(pattern=my_regex, label="DATE")
    assert strat.predict(test_date)


@pytest.mark.parametrize("test_children", ["2 enfants", " 3 enfants"])
def test_RegexPredictStrategy_CHILDREN(test_children):
    my_regex = r"([0-99]+?)\s*enfants"
    strat = RegexPredictStrategy(pattern=my_regex, label="CHILDREN")
    assert strat.predict(test_children)


@pytest.mark.parametrize("test_mail", ["ab.cd@ef.fr", "abcd@ef.com"])
def test_RegexPredictStrategy_MAIL(test_mail):
    my_regex = r"[\w\.-]+[@]\w+[.]\w{2,4}([.]\w{2,4})*"
    strat = RegexPredictStrategy(pattern=my_regex, label="MAIL")
    assert strat.predict(test_mail)
