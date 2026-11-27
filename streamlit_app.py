"""Reliable AI Lab — a synthetic, offline-capable teaching app."""
from datetime import time, timedelta
from pathlib import Path
import streamlit as st
from lab_models import PRESETS, Scenario, clock, eligible, plan_energy, reconstruction_example
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


def set_energy(name="Comfortable"):
    p = PRESETS[name]
    st.session_state.update(energy=int(p.energy_wh), night=int(p.night_h),
                            minimum=int(p.minimum_pct), reserve=int(p.reserve_pct), extra=True)


def reset_evidence():
    st.session_state.update(observation=time(20, 0), cutoff=time(20, 10), receipt=time(20, 20),
                            reveal=False, later=False)


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

lab = st.segmented_control("Choose a lab", (PREDICTIONS, DECISIONS),
                           default=PREDICTIONS, required=True, wrap=True,
                           key="lab", label_visibility="collapsed")
part = None
if lab == PREDICTIONS:
    part = st.segmented_control("Choose a part of Lab 1", (EVIDENCE, ENERGY),
                               default=EVIDENCE, required=True, wrap=True,
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
        st.toggle("Show result", key="reveal", persist_state="page")
        st.button("Reset evidence", on_click=reset_evidence, width="stretch")
    obs, cut, rec = [st.session_state[k].hour * 60 + st.session_state[k].minute
                     for k in ("observation", "cutoff", "receipt")]
    with chart:
        st.altair_chart(event_timeline(obs, cut, rec), width="stretch", theme=None)
        if rec < obs:
            st.warning("Receipt precedes observation. Those times are inconsistent for a single event on one clock.")
        if st.session_state.reveal:
            observation_ok, receipt_ok = eligible(obs, cut), eligible(rec, cut)
            if observation_ok == receipt_ok:
                comparison = "Both times pass the cutoff." if receipt_ok else "Neither time passes the cutoff."
            else:
                comparison = "Only the receipt time passes." if receipt_ok else "Only the observation time passes."
            result = "Available by the cutoff." if receipt_ok else "Unavailable at the cutoff."
            st.html(f'<div class="result{"" if receipt_ok else " warn"}"><strong>{result}</strong> '
                    f'{comparison}</div>')

    with st.expander("How later data changes an error score"):
        st.caption("Synthetic inputs, forecast and outcome")
        st.toggle("Use the later reconstructed input", key="later", persist_state="page")
        toy = reconstruction_example(st.session_state.later)
        st.markdown(f"**{toy.label}** · The toy rule always predicts a 10 percentage-point SOC drop.")
        m = st.columns(3)
        m[0].metric("Input battery SOC", f"{toy.input_soc:.0f}%")
        m[1].metric("Predicted later SOC", f"{toy.prediction_soc:.0f}%")
        m[2].metric("Absolute error", f"{toy.absolute_error_pp:.0f} pp")
        st.write("**Frozen issued input: 70% → prediction 60%.** "
                 "**Later reconstructed input: 58% → prediction 48%.** Fixed invented outcome: **47%**.")
        st.caption("The apparent error changes from 13 to 1 percentage point only because the input changes. "
                   "This is a different retrospective forecast—not a correction to what the model originally issued. "
                   "Reconstruction need not improve a score; this example was chosen to expose that possibility.")

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
