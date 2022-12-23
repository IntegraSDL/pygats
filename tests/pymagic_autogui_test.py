import pytest
from gats.gats import recognizeText, findFuzzyText, findRegExpText
from PIL import Image
results = []
def test_recognizeText():
    global results
    img = Image.open('testitems/initial-state.png')
    assert img is not None
    resultsRUS = recognizeText(img, 'rus')
    assert resultsRUS is not None
    # list of tuples expected
    assert type(resultsRUS) is list

    resultsENG = recognizeText(img, 'eng')
    assert resultsENG is not None
    # list of tuples expected
    assert type(resultsENG) is list
    results = resultsRUS + resultsENG
    map(lambda x: print(x), results)
    for r in results:
        assert type(r) is tuple
        # each tuple has x,y,w,h,text format
        (x,y,w,h,t) = r
        assert type(x) is int
        assert type(y) is int
        assert type(w) is int
        assert type(h) is int
        assert type(t) is str

def test_fuzzySearch():
    global results
    r1 = findFuzzyText(results, 'сессия')
    assert r1 is not None
    assert len(r1) > 0
    r2 = findFuzzyText(results, 'события')
    assert len(r2) > 0
    r3 = findFuzzyText(results, 'Администрирование')
    assert len(r3) > 0
    r4 = findFuzzyText(results, 'Update policy')
    assert len(r4) > 0
    r5 = findFuzzyText(results, 'Пользователь')
    assert len(r5) > 0
    print(r5)


def test_reSearch():
    global results
    r1 = findRegExpText(results, r'[0-9]{2}\.[0-9]{2}\.[0-9]{4} ')
    assert len(r1) > 0
    for l in r1:
        (x,y,w,h,text, subst) = l
        print(f'{text} <==> {subst}')
