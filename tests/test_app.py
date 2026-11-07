from datetime import time
from pathlib import Path
from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parents[1] / "streamlit_app.py")


def app():
    at = AppTest.from_file(APP, default_timeout=15).run()
    assert not at.exception
    return at


def test_launch_presets_and_reset():
    at = app()
    for preset, expected_energy in [("Close call",220),("Impossible",120),("Comfortable",480)]:
        next(b for b in at.button if b.label == preset).click().run()
        assert not at.exception
        assert at.slider(key="energy").value == expected_energy
        if preset == "Impossible":
            assert any("Service failure is explicit" in e.value for e in at.error)
    at.slider(key="energy").set_value(0).run()
    next(b for b in at.button if b.label == "↺ Reset light").click().run()
    assert at.slider(key="energy").value == 480
    assert at.slider(key="reserve").value == 10


def test_live_timestamp_boundaries_reset_and_fixed_counts():
    at = app()
    baseline = [m.value for m in at.metric if m.label in ["Resource-status eligible",
        "Receipt-time eligible","Individual decisions changed","Forecasts audited","Predictions that differed"]]
    assert baseline == ["184/782","126/782","66","87","345/348"]
    at.toggle(key="reveal").set_value(True).run()
    assert any("rules disagree" in e.value for e in at.error)
    at.slider(key="receipt").set_value(time(20,10)).run()
    assert any("both timestamps pass" in s.value for s in at.success)
    at.slider(key="cutoff").set_value(time(20,0)).run()
    assert any("rules disagree" in e.value for e in at.error)
    at.slider(key="observation").set_value(time(20,30)).run()
    assert any("inconsistent" in w.value for w in at.warning)
    at.toggle(key="later").set_value(True).run()
    assert next(m.value for m in at.metric if m.label == "Absolute error") == "1 pp"
    next(b for b in at.button if b.label == "Impossible").click().run()
    after = [m.value for m in at.metric if m.label in ["Resource-status eligible",
        "Receipt-time eligible","Individual decisions changed","Forecasts audited","Predictions that differed"]]
    assert after == baseline
    next(b for b in at.button if b.label == "↺ Reset evidence").click().run()
    assert at.slider(key="observation").value == time(20,0)
    assert at.slider(key="receipt").value == time(20,20)
    assert not at.toggle(key="later").value
    assert not at.toggle(key="reveal").value
    assert not at.exception
