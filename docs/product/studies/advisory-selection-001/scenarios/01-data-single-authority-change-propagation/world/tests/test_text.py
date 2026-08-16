from catalog.text import tokenize


def test_lowercases_and_splits_on_punctuation():
    assert tokenize("Stainless-Steel Bottle, 1L!") == ["stainless", "steel", "bottle", "1l"]


def test_drops_stopwords_and_single_characters():
    assert tokenize("a grinder for the home") == ["grinder", "home"]


def test_empty_text_gives_no_tokens():
    assert tokenize("") == []
