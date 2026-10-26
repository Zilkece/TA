from src.catcalling_x.query_builder import build_query

def test_query_keeps_replies_and_quotes_and_excludes_reposts():
    q = build_query("catcalling")
    assert "catcalling" in q
    assert "-is:retweet" in q
    assert "-is:reply" not in q
