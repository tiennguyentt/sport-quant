"""Smoke tests via Streamlit AppTest — no network, no model calls."""
import os

import pytest
from streamlit.testing.v1 import AppTest

# Force deterministic synthetic fixtures (no live API) so tests are stable.
os.environ["SPORTQUANT_OFFLINE"] = "1"


@pytest.fixture()
def at():
    a = AppTest.from_file("streamlit_app.py", default_timeout=60)
    a.run()
    assert not a.exception, a.exception
    return a


def test_terminal_is_front_door(at):
    assert at.radio[0].value == "Terminal"
    body = " ".join(getattr(m, "value", "") or "" for m in at.markdown)
    assert "polymarket" in body.lower()  # hero targets Polymarket & Kalshi
    assert "venue" in body.lower()       # fixture cards render
    assert "LIVE SCORE TRACKER" in body  # ticker present


def test_about_has_the_math(at):
    at.radio[0].set_value("About").run()
    assert not at.exception, at.exception
    body = " ".join(getattr(m, "value", "") or "" for m in at.markdown)
    assert "dixon" in body.lower() and "kelly" in body.lower()  # the flow + math live here


def test_ask_routes_through_gate(at):
    at.text_input[0].set_value("Bayern vs Werder Bremen")  # in-body chat form
    next(b for b in at.button if "➤" in b.label).click().run()
    assert not at.exception, at.exception
    assert len(at.session_state["thread"]) == 2  # user + engine reply


def test_rejection_shows_reason_codes(at):
    sea = next((b for b in at.button if "Seahawks" in b.key), None)
    assert sea is not None
    sea.click().run()
    assert not at.exception, at.exception
    body = " ".join(getattr(m, "value", "") or "" for m in at.markdown)
    assert "REJECTED" in body  # the honest no-bet path


def test_all_pages_render(at):
    for pg in ["Performance", "Calibration"]:
        at.radio[0].set_value(pg).run()
        assert not at.exception, f"{pg}: {at.exception}"
