from core.predict_strategy import (
    FlairPredictStrategy,
    SpacyPredictStrategy,
    PredictStrategy,
    ChainPredictStrategy,
    Span,
    PhoneNumberPredictStrategy,
)


def test_predict_flair_strategy():
    strategy = FlairPredictStrategy()
    sensitive = strategy.predict(
        "Jeanne DOMERGUE  20 ans, Nationalité française  domergue.jeanne@gmail.com  6, place des peupliers "
        "93200 Saint-Denis"
    )
    assert Span("Jeanne DOMERGUE", "PER") in sensitive


def test_predict_spacy_strategy():
    strategy = ChainPredictStrategy([SpacyPredictStrategy(), PhoneNumberPredictStrategy(region="FR")])
    sensitive = strategy.predict(
        "Jeanne DOMERGUE  20 ans, Nationalité française  domergue.jeanne@gmail.com  6, place des peupliers "
        "93200 Saint-Denis",
    )
    sensitive = list(sensitive)
    assert Span("Jeanne DOMERGUE", "PER") in sensitive
    assert Span("domergue.jeanne@gmail.com", "EMAIL") in sensitive

    sensitive = strategy.predict(
        "24 ans +33 6 98 86 08 71 vincent.dubay@gmail.com 2 rue André Gide 28110 Lucé ",
    )
    assert Span("24 ans", "AGE") in sensitive
    assert Span("+33 6 98 86 08 71", "TEL") in sensitive

    sensitive = strategy.predict("110 rue du Faubourg Saint-Pierre   marié   +33689888071")
    assert Span("marié", "FAM") in sensitive
    assert Span("+33689888071", "TEL") in sensitive


def test_chain_strategy():
    class StrategyA(PredictStrategy):
        def predict(self, line: str):
            yield Span("A")
            yield Span("A")

    class StrategyB(PredictStrategy):
        def predict(self, line: str):
            yield Span("B")

    strategy = ChainPredictStrategy([StrategyA(), StrategyB()])
    predictions = strategy.predict(None)
    assert list(predictions) == [Span("A"), Span("A"), Span("B")]
