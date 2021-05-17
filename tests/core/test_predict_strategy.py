from core.predict_strategy import (
    FlairPredictStrategy,
    SpacyPredictStrategy,
    PredictStrategy,
    ChainPredictStrategy,
    Span,
)


def test_predict_flair_strategy():
    strategy = FlairPredictStrategy()
    sensitive = strategy.predict(
        "Jeanne DOMERGUE  20 ans, Nationalité française  domergue.jeanne@gmail.com  6, place des peupliers "
        "93200 Saint-Denis"
    )
    assert Span("Jeanne DOMERGUE", "PER") in sensitive


def test_predict_spacy_strategy():
    strategy = ChainPredictStrategy([SpacyPredictStrategy()])
    sensitive = strategy.predict(
        "Emma Louisa diplômée de l'Université Paris-Nanterre ",
    )
    assert Span("Université Paris-Nanterre", "ORG_ENS") in sensitive

    sensitive = strategy.predict(
        "Emma Louisa, rue Victor Hugo, Paris",
    )
    assert Span("rue Victor Hugo", "ADDRESS") in sensitive


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
