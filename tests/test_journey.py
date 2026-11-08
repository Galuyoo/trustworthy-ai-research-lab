"""New controls preserve the scientific experiment rather than resetting it."""
from datetime import time
from pathlib import Path
import pytest
from streamlit.testing.v1 import AppTest
from lab_models import PRESETS, Scenario, plan_energy
from lab_views import night_frame

APP = str(Path(__file__).resolve().parents[1] / 'streamlit_app.py')


def click(at, label):
    next(b for b in at.button if b.label == label).click().run()
    assert not at.exception


def test_journey_and_mode_preserve_both_experiments():
    at = AppTest.from_file(APP, default_timeout=15).run()
    click(at, 'Begin the night →')
    assert at.session_state.journey == '1 · Energy'
    click(at, 'Close call')
    at.slider(key='reserve').set_value(15).run()
    at.slider(key='night_progress').set_value(75).run()
    click(at, 'Follow the measurement →')
    assert at.session_state.journey == '2 · Evidence'
    at.slider(key='receipt').set_value(time(20, 8)).run()
    at.toggle(key='reveal').set_value(True).run()
    at.toggle(key='later').set_value(True).run()
    at.toggle(key='presentation').set_value(False).run()
    click(at, '← Return to the lighting plan')
    assert at.slider(key='energy').value == 220
    assert at.slider(key='reserve').value == 15
    assert at.slider(key='night_progress').value == 75
    assert at.slider(key='receipt').value == time(20, 8)
    assert at.toggle(key='reveal').value
    assert at.toggle(key='later').value


def test_start_over_resets_all_content_and_keeps_accessibility_preferences():
    at = AppTest.from_file(APP, default_timeout=15).run()
    click(at, 'Impossible')
    at.toggle(key='motion').set_value(False).run()
    at.toggle(key='presentation').set_value(False).run()
    at.toggle(key='reveal').set_value(True).run()
    at.toggle(key='later').set_value(True).run()
    click(at, '↺ Start over')
    assert at.session_state.journey == 'The system'
    assert at.slider(key='energy').value == 480
    assert at.slider(key='reserve').value == 10
    assert at.slider(key='night_progress').value == 35
    assert at.slider(key='receipt').value == time(20, 20)
    assert not at.toggle(key='reveal').value
    assert not at.toggle(key='later').value
    assert not at.toggle(key='motion').value
    assert not at.toggle(key='presentation').value


def test_equality_shortcut_uses_current_cutoff():
    at = AppTest.from_file(APP, default_timeout=15).run()
    at.slider(key='cutoff').set_value(time(20, 35)).run()
    at.toggle(key='reveal').set_value(True).run()
    click(at, 'Receive at cutoff')
    assert at.slider(key='receipt').value == time(20, 35)
    assert any('both timestamps pass' in msg.value for msg in at.success)


@pytest.mark.parametrize('preset', list(PRESETS))
@pytest.mark.parametrize('progress', [0, 35, 75, 100])
def test_scrubber_conserves_energy_and_never_changes_plan(preset, progress):
    plan = plan_energy(PRESETS[preset])
    frame = night_frame(plan, progress)
    assert frame.remaining_wh == pytest.approx(plan.remaining_at(frame.hour))
    assert 0 <= frame.remaining_fraction <= 1
    used = 40 * plan.brightness_pct / 100 * min(frame.hour, plan.service_h)
    assert used + frame.remaining_wh == pytest.approx(plan.scenario.energy_wh)
    assert frame.status == ('Dawn' if progress == 100 else 'Serving' if frame.hour < plan.service_h else 'Unserved')
    assert frame.brightness_pct == (plan.brightness_pct if frame.status == 'Serving' else 0)


def test_failure_boundary_is_explicit_and_dawn_is_not_a_failure():
    plan = plan_energy(PRESETS['Impossible'])
    stop = plan.service_h / plan.scenario.night_h * 100
    assert night_frame(plan, stop - .001).status == 'Serving'
    assert night_frame(plan, stop).status == 'Unserved'
    assert night_frame(plan, stop).brightness_pct == 0
    assert night_frame(plan, 100).status == 'Dawn'
    zero = night_frame(plan_energy(Scenario(0, 12, 40, 10)), 0)
    assert zero.remaining_fraction == 0
    assert zero.brightness_pct == 0
    assert zero.status == 'Unserved'


@pytest.mark.parametrize('progress', [-1, 101, float('nan'), float('inf')])
def test_invalid_scrubber_progress_is_rejected(progress):
    with pytest.raises(ValueError):
        night_frame(plan_energy(PRESETS['Comfortable']), progress)
