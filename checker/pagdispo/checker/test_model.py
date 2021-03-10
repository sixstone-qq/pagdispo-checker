from pagdispo.checker.model import Website


def test_id_generation():
    w1 = Website(url='http://foo.bar')
    assert len(w1.id) == 24

    w2 = Website(url='http://foo.bar', method='HEAD')
    assert len(w2.id) == 24
    assert w2.id != w1.id

    w3 = Website(url='http://foo.bar', method='GET', match_regex=r'foo')
    assert len(w3.id) == 24
    assert w3.id != w2.id
    assert w3.id != w1.id
