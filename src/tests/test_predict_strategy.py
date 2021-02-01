import pytest

from src.predict_strategy import FlairPredictStrategy, SpacyPredictStrategy, PredictStrategy, ChainPredictStrategy, \
    RegexPredictStrategy, Span


def test_predict_flair_strategy():
    strategy = FlairPredictStrategy()
    sensitive = strategy.predict(
        'Jeanne DOMERGUE  20 ans, Nationalité française  domergue.jeanne@gmail.com  6, place des peupliers '
        '93200 Saint-Denis')
    assert Span('Jeanne DOMERGUE', 'PER') in sensitive


def test_predict_spacy_strategy():
    strategy = ChainPredictStrategy([
        SpacyPredictStrategy(),
        RegexPredictStrategy(r'(?:(?:\+|00)33|0)\s*[1-9](?:[\s.-]*\d{2}){4}', 'TEL')])
    sensitive = strategy.predict(
        'Jeanne DOMERGUE  20 ans, Nationalité française  domergue.jeanne@gmail.com  6, place des peupliers '
        '93200 Saint-Denis',
    )
    sensitive = list(sensitive)
    assert Span('Jeanne DOMERGUE', 'PER') in sensitive
    assert Span('domergue.jeanne@gmail.com', 'EMAIL') in sensitive

    sensitive = strategy.predict(
        '24 ans +33 6 98 86 08 71 vincent.dubay@gmail.com 2 rue André Gide 28110 Lucé ',
    )
    assert Span('24 ans', 'AGE') in sensitive
    assert Span('+33 6 98 86 08 71', 'TEL') in sensitive

    sensitive = strategy.predict('110 rue du Faubourg Saint-Pierre   marié   +33689888071')
    assert Span('marié', 'FAM') in sensitive
    assert Span('+33689888071', 'TEL') in sensitive


def test_chain_strategy():
    class StrategyA(PredictStrategy):
        def predict(self, lines: str):
            yield Span('A')
            yield Span('A')

    class StrategyB(PredictStrategy):
        def predict(self, lines: str):
            yield Span('B')

    strategy = ChainPredictStrategy([StrategyA(), StrategyB()])
    predictions = strategy.predict(None)
    assert list(predictions) == [Span('A'), Span('A'), Span('B')]


@pytest.mark.parametrize('text_line, expected_span_list', [
    ('24 ans +33 6 98 86 08 71 vincent.dubay@gmail.com 2 rue André Gide 28110 Lucé ',
     [Span('+33 6 98 86 08 71', 'TEL')]),
    ('110 rue du Faubourg Saint-Pierre   marié   +33689888071', [Span('+33689888071', 'TEL')]),
    ('24 ans +33 6 98 86 08 71 110 rue du Faubourg Saint-Pierre marié   +33689888071',
     [Span('+33 6 98 86 08 71', 'TEL'), Span('+33689888071', 'TEL')]),
])
def test_regex_strategy_french_tel(text_line, expected_span_list):
    strategy = RegexPredictStrategy(r'(?:(?:\+|00)33|0)\s*[1-9](?:[\s.-]*\d{2}){4}', 'TEL')

    prediction = strategy.predict(text_line)
    assert list(prediction) == expected_span_list


@pytest.mark.parametrize('tel_regex, text_line, expected_span_list', [
    (r'(?:(?:\+|00)216)(?:[\s.-]*\d{2}){4}', '+21699995795', [Span('+21699995795', 'TEL')]),
    (r'(?:(?:\+|00)216)(?:[\s.-]*\d{2}){4}', '+216 99 99 57 95', [Span('+216 99 99 57 95', 'TEL')]),
    (r'(?:(?:\+|00)216)(?:[\s.-]*\d{3}){2}', '+216 99 99 57 95', [Span('+216 99 995 795', 'TEL')]),
    (r'(?:(?:\+|00)216)\s*[1-9](?:[\s.-]*\d{2}){4}', '0021699995795', [Span('0021699995795', 'TEL')]),
])
def test_regex_strategy_foreign_tel(tel_regex, text_line, expected_span_list):
    strategy = RegexPredictStrategy(tel_regex, 'TEL')

    prediction = strategy.predict(text_line)
    assert list(prediction) == expected_span_list
