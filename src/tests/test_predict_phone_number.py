import pytest

from src.predict_strategy import Span, PhoneNumberPredictStrategy


@pytest.mark.parametrize('text_line, expected_span_list', [
    ('24 ans +33 6 98 86 08 71 vincent.dubay@gmail.com 2 rue André Gide 28110 Lucé ',
     [Span('+33 6 98 86 08 71', 'TEL')]),
    ('110 rue du Faubourg Saint-Pierre   marié   +33689888071', [Span('+33689888071', 'TEL')]),
    # TODO without '\n' in test case below
    ('24 ans +33 6 98 86 08 71\n 110 rue du Faubourg Saint-Pierre marié   +33689888071',
     [Span('+33 6 98 86 08 71', 'TEL'), Span('+33689888071', 'TEL')]),
])
def test_phone_number_predict_strategy(text_line, expected_span_list):
    strategy = PhoneNumberPredictStrategy(region='FR')

    prediction = strategy.predict(text_line)
    assert list(prediction) == expected_span_list


@pytest.mark.parametrize('region, text_line, expected_span_list', [
    ('TN', '+21699995795', [Span('+21699995795', 'TEL')]),
    ('TN', '+216 99 99 57 95', [Span('+216 99 99 57 95', 'TEL')]),
    ('TN', '+216 99 995 795', [Span('+216 99 995 795', 'TEL')]),
    ('TN', '0021699995795', [Span('0021699995795', 'TEL')]),
    ('TN', '2012-2013', [Span(text='2012-2013', label='TEL')]),
    ('TN', '+21 2012-2013', [Span(text='2012-2013', label='TEL')]),
    ('FR', '2012-2013', []),
    ('FR', '+21 2012-2013', []),
])
def test_recognize_telephone_number_by_region(region, text_line, expected_span_list):
    strategy = PhoneNumberPredictStrategy(region=region)

    prediction = strategy.predict(text_line)
    assert list(prediction) == expected_span_list
