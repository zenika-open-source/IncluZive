from typing import List

from src.predict_strategy import FlairPredictStrategy, SpacyPredictStrategy, PredictStrategy, ChainPredictStrategy, \
    RegexPredictStrategy


def test_predict_flair_strategy():
    strategy = FlairPredictStrategy()
    sensitive = strategy.predict([
        'Jeanne DOMERGUE  20 ans, Nationalité française  domergue.jeanne@gmail.com  6, place des peupliers '
        '93200 Saint-Denis'])
    assert 'Jeanne DOMERGUE' in sensitive


def test_predict_spacy_strategy():
    strategy = ChainPredictStrategy([
        SpacyPredictStrategy(),
        RegexPredictStrategy(r'(?:(?:\+|00)33|0)\s*[1-9](?:[\s.-]*\d{2}){4}')])
    sensitive = strategy.predict([
        'Jeanne DOMERGUE  20 ans, Nationalité française  domergue.jeanne@gmail.com  6, place des peupliers '
        '93200 Saint-Denis',
        '24 ans +33 6 98 86 08 71 vincent.dubay@gmail.com 2 rue André Gide 28110 Lucé ',
        '110 rue du Faubourg Saint-Pierre   marié   +33689888071',
    ])
    sensitive = list(sensitive)
    assert 'Jeanne DOMERGUE' in sensitive
    assert 'domergue.jeanne@gmail.com' in sensitive
    assert '24 ans' in sensitive
    assert '+33689888071' in sensitive
    assert 'marié' in sensitive
    assert '+33 6 98 86 08 71' in sensitive


def test_chain_strategy():
    class StrategyA(PredictStrategy):
        def predict(self, lines: List[str]):
            yield 'A'
            yield 'A'

    class StrategyB(PredictStrategy):
        def predict(self, lines: List[str]):
            yield 'B'

    strategy = ChainPredictStrategy([StrategyA(), StrategyB()])
    predictions = strategy.predict(None)
    assert list(predictions) == ['A', 'A', 'B']


def test_regex_strategy():
    strategy = RegexPredictStrategy(r'(?:(?:\+|00)33|0)\s*[1-9](?:[\s.-]*\d{2}){4}')

    prediction = strategy.predict(['24 ans +33 6 98 86 08 71 vincent.dubay@gmail.com '
                                   '2 rue André Gide 28110 Lucé '])
    assert list(prediction) == ['+33 6 98 86 08 71']

    prediction = strategy.predict(['110 rue du Faubourg Saint-Pierre   marié   +33689888071'])
    assert list(prediction) == ['+33689888071']

    prediction = strategy.predict(['24 ans +33 6 98 86 08 71 110 rue du Faubourg Saint-Pierre  '
                                   ' marié   +33689888071'])
    assert list(prediction) == ['+33 6 98 86 08 71', '+33689888071']
