"""Reliable AI Lab — a synthetic, offline-capable teaching app."""
from datetime import time, timedelta
from pathlib import Path
import streamlit as st
from lab_models import PRESETS, Scenario, eligible, plan_energy, reconstruction_example
from lab_charts import energy_charts, event_timeline

st.set_page_config(page_title="Reliable AI Lab · Salaheddine Chouikh", page_icon="💡", layout="wide")

st.html("""<style>
.stApp {font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;}
.block-container {max-width:1250px; padding-top:2rem; padding-bottom:2rem;}
h1,h2,h3 {letter-spacing:-0.035em;} h1 {font-size:clamp(2.2rem,4vw,3.4rem)!important;}
.result {padding:10px 14px;border-left:3px solid #00adef;background:#eef7fc;line-height:1.45;}
.result.warn {border-left-color:#b46b0c;background:#fff6e7;}
.result.bad {border-left-color:#b90057;background:#fff1f7;}
.result p {margin:0;}
.forecast-scores{width:100%;border-collapse:collapse;font-size:.9rem;font-variant-numeric:tabular-nums}
.forecast-scores caption{text-align:left;font-weight:650;margin-bottom:5px}
.forecast-scores :is(th,td){padding:7px 8px;text-align:right;border-bottom:1px solid #ccd9e9}
.forecast-scores th:first-child{text-align:left}
.forecast-scores thead{background:#eef7fc}
.forecast-scores .leakage{background:#fff6e7}
@media(max-width:480px){.forecast-scores :is(th,td){padding:5px 4px}}
.st-key-evidence_controls, .st-key-energy_controls {
    border-top:3px solid #00adef;background:#eef7fc;border-radius:0 0 6px 6px;padding:14px;
}
[data-testid="stSegmentedControl"] button:is([aria-checked="true"], [aria-pressed="true"]) {
    background:#010f4e;color:#fff;border-color:#010f4e;
}
[data-testid="stMetricValue"] {font-size:1.7rem;}
[data-testid="stSlider"] {padding-bottom:6px;} a {text-underline-offset:3px;}
@media(max-width:640px){.block-container{padding:1rem 1rem 2rem;}h2{font-size:1.65rem!important;}}
</style>""")


def projector_chart(chart, height, *, timeline=False):
    chart = chart.properties(height=height)
    chart.config.axis.labelFontSize = 16
    chart.config.axis.titleFontSize = 16
    chart.config.legend.labelFontSize = 15
    if timeline:
        chart.layer[-1].mark.fontSize = 21
    return chart


def set_energy(name="Comfortable"):
    p = PRESETS[name]
    st.session_state.update(energy=int(p.energy_wh), night=int(p.night_h),
                            minimum=int(p.minimum_pct), reserve=int(p.reserve_pct), extra=True)


def reset_evidence():
    st.session_state.update(observation=time(20, 0), cutoff=time(20, 10), receipt=time(20, 20))


if "energy" not in st.session_state:
    set_energy()
if "observation" not in st.session_state:
    reset_evidence()

st.title("Reliable AI Lab")
app_dir = Path(__file__).resolve().parent

PREDICTIONS = "01 — From Data to Reliable Predictions"
DECISIONS = "02 — From Predictions to Decisions"
EVIDENCE = "1. Information availability"
ENERGY = "2. Battery energy feasibility"

st.session_state.setdefault("lab", PREDICTIONS)
lab = st.segmented_control("Choose a lab", (PREDICTIONS, DECISIONS),
                           required=True, wrap=True,
                           key="lab", label_visibility="collapsed")
part = None
if lab == PREDICTIONS:
    projector = st.toggle("Projector view", key="lab1_projector", persist_state="page")
    if projector:
        st.html("""<style>
        .block-container {max-width:1440px;padding-top:1.25rem}
        .block-container h1 {font-size:2.1rem!important;padding-bottom:.25rem}
        .block-container [data-testid="stVerticalBlock"] {gap:.65rem}
        .st-key-evidence_controls [data-testid="stVerticalBlock"],
        .st-key-energy_controls [data-testid="stVerticalBlock"] {gap:.45rem}
        .block-container [data-testid="stSlider"] {padding-bottom:0}
        .forecast-scores {font-size:clamp(.9rem,1.45vw,1.15rem)}
        .result {font-size:clamp(1rem,1.5vw,1.2rem)}
        .st-key-evidence_controls [data-testid="stWidgetLabel"] p,
        .st-key-energy_controls [data-testid="stWidgetLabel"] p,
        .st-key-evidence_controls [data-testid="stButton"] p,
        .st-key-energy_controls [data-testid="stButton"] p {
            font-size:clamp(.95rem,1.45vw,1.15rem)
        }
        </style>""")
    st.session_state.setdefault("prediction_part", EVIDENCE)
    part = st.segmented_control("Choose a part of Lab 1", (EVIDENCE, ENERGY),
                               required=True, wrap=True,
                               key="prediction_part", persist_state="page", label_visibility="collapsed")

if lab == DECISIONS:
    st.iframe(app_dir / "assets" / "Adaptive_Energy_Management_Simulator.html",
              alt="Interactive solar streetlight battery and lighting simulator")

elif part == EVIDENCE:
    st.caption("Synthetic timestamps. The reading is available if it arrives by the forecast cutoff.")
    chart, controls = st.columns([1.7, 1], gap="medium")
    with controls, st.container(key="evidence_controls"):
        st.markdown("**Experiment controls**")
        for label, key in [("Observation time", "observation"), ("Forecast cutoff", "cutoff"),
                           ("Receipt time", "receipt")]:
            st.slider(label, min_value=time(20, 0), max_value=time(21, 0),
                      step=timedelta(minutes=1), format="HH:mm", key=key, persist_state="page")
        st.button("Reset evidence", on_click=reset_evidence, width="stretch")
        st.button("Next: battery energy", on_click=st.session_state.update,
                  kwargs={"prediction_part": ENERGY}, width="stretch")
    obs, cut, rec = [st.session_state[k].hour * 60 + st.session_state[k].minute
                     for k in ("observation", "cutoff", "receipt")]
    with chart:
        timeline = event_timeline(obs, cut, rec)
        if projector:
            timeline = projector_chart(timeline, 250, timeline=True)
        st.altair_chart(timeline, width="stretch", theme=None)
        if rec < obs:
            st.warning("Receipt precedes observation. Those times are inconsistent for a single event on one clock.")
        else:
            received_in_time = eligible(rec, cut)
            observed_in_time = eligible(obs, cut)
            live = reconstruction_example(received_in_time)
            replay = reconstruction_example(observed_in_time)
            leakage = observed_in_time and not received_in_time

            def score_row(label, forecast, row_class=""):
                return (f'<tr class="{row_class}"><th scope="row">{label}</th>'
                        f'<td>{forecast.input_soc:.0f}%</td><td>{forecast.prediction_soc:.0f}%</td>'
                        f'<td>{forecast.absolute_error_pp:.0f} pp</td></tr>')

            st.html(
                '<table class="forecast-scores"><caption>Forecast comparison</caption>'
                '<thead><tr><th scope="col">Cutoff rule</th><th scope="col">Input SOC</th>'
                '<th scope="col">Forecast SOC</th><th scope="col">Absolute error</th></tr></thead><tbody>'
                + score_row("Live · receipt time", live)
                + score_row("Replay · observation time", replay, "leakage" if leakage else "")
                + '</tbody></table>'
            )
            if leakage:
                st.warning("Data leakage: the replay uses a reading that arrived after the forecast cutoff.")
            elif received_in_time:
                st.caption("Both forecasts can use the reading because it arrived by the cutoff.")
            else:
                st.caption("Both forecasts use the earlier reading because the new reading was taken after the cutoff.")
            st.caption(f"Synthetic example. Earlier reading: 70%. New reading: 58%. "
                       f"The rule subtracts 10 percentage points. Simulated outcome: {live.outcome_soc:.0f}%.")


elif part == ENERGY:
    st.caption("Synthetic simulation inspired by the published SETA battery-runtime and dimming study.")
    charts, controls = st.columns([1.7, 1], gap="medium")
    with controls, st.container(key="energy_controls"):
        st.markdown("**Experiment controls**")
        first, second = st.columns(2)
        for column, name in zip((first, second, first), PRESETS):
            column.button(name, on_click=set_energy, args=(name,), width="stretch")
        second.button("Reset light", on_click=set_energy, width="stretch")
        st.slider("Available battery energy (Wh)", 0, 600, step=5, key="energy", persist_state="page")
        st.slider("Night duration (hours)", 4, 16, step=1, key="night", persist_state="page")
        st.slider("Minimum brightness (%)", 10, 100, step=5, key="minimum", persist_state="page")
        st.slider("Planning reserve (%)", 0, 40, step=1, key="reserve", persist_state="page",
                  help="Share of the starting energy held in reserve.")
        st.checkbox("Aim for 80% brightness if energy allows", key="extra", persist_state="page")
        st.button("Next: Lab 2", on_click=st.session_state.update,
                  kwargs={"lab": DECISIONS}, width="stretch")
    scenario = Scenario(st.session_state.energy, st.session_state.night,
                        st.session_state.minimum, st.session_state.reserve)
    plan = plan_energy(scenario, 80 if st.session_state.extra else scenario.minimum_pct)
    with charts:
        if plan.feasible:
            kind, result = "", "Minimum brightness is feasible."
            detail = f"{plan.brightness_pct:.1f}% brightness for {scenario.night_h:.0f} hours."
        elif plan.physically_feasible:
            kind, result = "warn", "Minimum brightness exceeds the budget after reserve."
            detail = f"Shortfall: {plan.planning_gap_wh:.0f} Wh. Unserved: {plan.unmet_h:.2f} hours."
        else:
            kind, result = "bad", "Minimum brightness exceeds starting energy."
            detail = f"Without reserve, the shortfall is {plan.physical_gap_wh:.0f} Wh. With reserve, {plan.unmet_h:.2f} hours are unserved."
        energy = f"{plan.budget_wh:.0f} Wh usable · {plan.floor_wh:.0f} Wh required"
        st.html(f'<div class="result {kind}"><strong>{result}</strong> {detail}<p>{energy}</p></div>')
        for chart in energy_charts(plan):
            if projector:
                chart = projector_chart(chart, 185)
            st.altair_chart(chart, width="stretch", theme=None)
        st.caption("Dashed amber line: battery reserve.")
    with st.expander("How this simulation works · assumptions & research limits"):
        st.markdown("**Minimum energy (Wh) = 40 W × minimum brightness / 100 × night hours.**\n\n"
                    "Usable energy = starting energy × (1 − reserve / 100). If that covers the minimum, "
                    "we allocate constant brightness up to the desired target. Otherwise, we deliver the floor "
                    "until usable energy runs out and explicitly mark the remaining time as unserved. "
                    "The reserve stays in the battery.\n\n"
                    "Linear power versus brightness, perfect conversion and no charging, standby load, "
                    "temperature, ageing or stochastic error are assumed. The reserve is not a confidence level.\n\n"
                    "**Inspired by the published SETA research; not a reproduction.** The original paper used "
                    "NASA laboratory battery discharge data and simulation-based evaluation, with its own "
                    "experimental horizons. These invented night lengths and energy values are not published "
                    "numerical results, a field-validated controller, or measured real-world energy savings.")
        st.markdown("[Published SETA paper](https://doi.org/10.1016/j.seta.2026.105315)")
