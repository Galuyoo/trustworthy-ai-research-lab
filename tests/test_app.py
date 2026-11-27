from datetime import time
from pathlib import Path
from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parents[1] / "streamlit_app.py")


LAB1 = "01 — From Data to Reliable Predictions"
DECISIONS = "02 — From Predictions to Decisions"
ENERGY = "2. Battery energy feasibility"
EVIDENCE = "1. Information availability"


def select(at, name):
    return at.segmented_control(key="prediction_part").set_value(name).run()


def app():
    at = AppTest.from_file(APP, default_timeout=15).run()
    assert not at.exception
    return at


def test_launch_presets_and_reset():
    at = select(app(), ENERGY)
    for preset, expected_energy in [("Close call",220),("Impossible",120),("Comfortable",480)]:
        next(b for b in at.button if b.label == preset).click().run()
        assert not at.exception
        assert at.slider(key="energy").value == expected_energy
        if preset == "Impossible":
            assert any("Minimum brightness exceeds starting energy." in h.proto.body for h in at.get("html"))
    at.slider(key="energy").set_value(0).run()
    next(b for b in at.button if b.label == "Reset light").click().run()
    assert at.slider(key="energy").value == 480
    assert at.slider(key="reserve").value == 10


def test_live_timestamp_boundaries_reset_and_synthetic_reconstruction():
    at = select(app(), EVIDENCE)

    def compare(live_error, replay_error):
        [comparison] = [h.proto.body for h in at.get("html") if "Forecast comparison" in h.proto.body]
        assert f'<td>{live_error} pp</td></tr>' in comparison.split("Replay · observation time")[0]
        assert f'<td>{replay_error} pp</td></tr>' in comparison.split("Replay · observation time")[1]

    compare(13, 1)
    assert any("Data leakage" in w.value for w in at.warning)
    at.slider(key="receipt").set_value(time(20, 10)).run()
    compare(1, 1)
    assert not at.warning
    at.slider(key="observation").set_value(time(20, 8)).run()
    at.slider(key="cutoff").set_value(time(20, 5)).run()
    compare(13, 13)
    assert not at.warning
    at.slider(key="observation").set_value(time(20, 30)).run()
    assert any("inconsistent" in w.value for w in at.warning)
    assert all("Forecast comparison" not in h.proto.body for h in at.get("html"))
    next(b for b in at.button if b.label == "Reset evidence").click().run()
    assert at.slider(key="observation").value == time(20, 0)
    assert at.slider(key="receipt").value == time(20, 20)
    compare(13, 1)
    assert not at.exception


def test_navigation_loads_only_the_selected_demo_and_preserves_energy_state():
    at = app()
    assert at.segmented_control(key="lab").value == LAB1
    assert at.segmented_control(key="prediction_part").value == EVIDENCE
    assert not at.get("iframe")
    assert {slider.key for slider in at.slider} == {"observation", "cutoff", "receipt"}

    select(at, ENERGY)
    assert not at.get("iframe")
    at.slider(key="reserve").set_value(15).run()

    at.segmented_control(key="lab").set_value(DECISIONS).run()
    [iframe] = at.get("iframe")
    original = Path(APP).parent / "assets" / "Adaptive_Energy_Management_Simulator.html"
    assert iframe.proto.srcdoc == original.read_text(encoding="utf-8")
    assert not at.slider

    at.segmented_control(key="lab").set_value(LAB1).run()
    assert at.segmented_control(key="prediction_part").value == ENERGY
    assert at.slider(key="reserve").value == 15
    assert not at.get("iframe")
    assert not at.exception


def test_projector_and_next_experiment_preserve_settings():
    at = app()
    at.toggle(key="lab1_projector").set_value(True).run()
    at.slider(key="receipt").set_value(time(20, 10)).run()
    assert any("font-size:clamp(.9rem,1.45vw,1.15rem)" in h.proto.body for h in at.get("html"))
    next(b for b in at.button if b.label == "Next: battery energy").click().run()
    assert at.segmented_control(key="prediction_part").value == ENERGY
    assert at.toggle(key="lab1_projector").value
    assert at.slider(key="energy").value == 480
    at.slider(key="reserve").set_value(15).run()
    next(b for b in at.button if b.label == "Next: Lab 2").click().run()
    assert at.segmented_control(key="lab").value == DECISIONS
    assert at.get("iframe")
    at.segmented_control(key="lab").set_value(LAB1).run()
    assert at.slider(key="reserve").value == 15
    assert at.toggle(key="lab1_projector").value
    select(at, EVIDENCE)
    assert at.slider(key="receipt").value == time(20, 10)
    assert not at.exception
