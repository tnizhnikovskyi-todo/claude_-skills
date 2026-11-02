from notify.templates import render


def test_render():
    assert render("Hi {name}", {"name": "Ann"}) == "Hi Ann"
