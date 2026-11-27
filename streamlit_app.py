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
.status {border-radius:12px;padding:17px 20px;margin:8px 0 14px;border:1px solid #9acbc6;background:#e7f4ef;}
.status h3 {font-size:1.25rem;margin:0 0 5px;} .status p {margin:0;line-height:1.5;}
.status.warn {border-color:#dbba7a;background:#fff3d9;} .status.bad {border-color:#df9ca2;background:#ffedec;}
.verdict {border-radius:12px;padding:15px 18px;background:#fff;border:1px solid #d7e0de;}
.verdict strong {font-size:1.6rem;display:block;} .verdict p {margin:0;font-size:.88rem;}
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
                               key="prediction_part", persist_state="page")

if lab == DECISIONS:
    st.iframe(app_dir / "assets" / "Adaptive_Energy_Management_Simulator.html",
              alt="Interactive solar streetlight battery and lighting simulator")

elif part == EVIDENCE:
    st.caption("Synthetic example · compares observation and receipt times at the forecast cutoff.")
    a, b, c = st.columns(3)
    for col, label, key in [(a, "Observation time", "observation"), (b, "Forecast issue / cutoff", "cutoff"),
                            (c, "Actual receipt time", "receipt")]:
        col.slider(label, min_value=time(20, 0), max_value=time(21, 0),
                   step=timedelta(minutes=1), format="HH:mm", key=key, persist_state="page")
    obs, cut, rec = [st.session_state[k].hour * 60 + st.session_state[k].minute
                     for k in ("observation", "cutoff", "receipt")]
    st.altair_chart(event_timeline(obs, cut, rec), width="stretch", theme=None)
    st.caption("All times use one clock and date. A record received at the cutoff is available.")
    if rec < obs:
        st.warning("Receipt is earlier than observation. That is inconsistent for a single sensor event on a shared clock. "
                   "The timestamp comparisons below still apply, but this is not a physically consistent event history. "
                   "A resource-status clock in a real system may have different semantics.")
    reveal, reset = st.columns([3, 1])
    reveal.toggle("Reveal the verdict", key="reveal", persist_state="page")
    reset.button("↺ Reset evidence", on_click=reset_evidence, width="stretch", type="primary")
    if st.session_state.reveal:
        resource_ok, receipt_ok = eligible(obs, cut), eligible(rec, cut)
        for col, label, ok, at in zip(st.columns(2), ["Observation / resource-time rule", "Receipt-time rule"],
                                      [resource_ok, receipt_ok], [obs, rec]):
            with col:
                st.html(f'<div class="verdict"><p>{label}</p><strong style="color:{"#087f8c" if ok else "#c23d49"}">'
                        f'{"Eligible" if ok else "Not eligible"}</strong><p>{clock(at)} '
                        f'{"≤" if ok else ">"} cutoff {clock(cut)}</p></div>')
        if resource_ok and not receipt_ok:
            st.error("The rules disagree. No—the system had not received this observation when the forecast was issued.")
        elif receipt_ok and not resource_ok:
            st.warning("The rules disagree. Receipt passes, while observation time fails. Check the clock-consistency warning above.")
        elif receipt_ok:
            st.success("The rules agree: both timestamps pass the cutoff. Availability alone does not prove quality or usefulness.")
        else:
            st.info("The rules agree: neither timestamp passes the cutoff.")

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
    buttons = st.columns([1, 1, 1, 1])
    for column, name in zip(buttons, PRESETS):
        column.button(name, on_click=set_energy, args=(name,), width="stretch")
    buttons[3].button("↺ Reset light", on_click=set_energy, type="primary", width="stretch")

    controls, visual = st.columns([1, 1.8], gap="large")
    with controls:
        st.slider("Available battery energy (Wh)", 0, 600, step=5, key="energy", persist_state="page")
        st.slider("Night duration (hours)", 4, 16, key="night", persist_state="page")
        st.slider("Minimum required brightness (%)", 10, 100, step=5, key="minimum", persist_state="page")
        st.slider("Conservative planning reserve (%)", 0, 40, step=1, key="reserve", persist_state="page",
                  help="Hold back this share of starting energy. This is a planning choice, not a calibrated uncertainty probability.")
        st.checkbox("Aim for 80% brightness if energy allows", key="extra", persist_state="page")
        scenario = Scenario(st.session_state.energy, st.session_state.night,
                            st.session_state.minimum, st.session_state.reserve)
        plan = plan_energy(scenario, 80 if st.session_state.extra else scenario.minimum_pct)
        st.caption(f"Required floor: **{scenario.minimum_pct:.0f}%** all night. "
                   f"Desired target: **{plan.desired_pct:.0f}%**. Extra brightness is optional.")
        st.caption("Lamp model: 40 W at 100% brightness. No overnight charging. Night begins at hour 0.")

    with visual:
        if plan.feasible:
            kind, title = "", "The minimum service is feasible"
            message = (f"{plan.brightness_pct:.1f}% brightness for all {scenario.night_h:.0f} hours. "
                       f"The plan keeps {plan.reserve_wh:.0f} Wh in reserve.")
        elif plan.physically_feasible:
            kind, title = "warn", "The reserve makes this plan infeasible"
            message = (f"The minimum could fit without this reserve. With it, {plan.unmet_h:.2f} hours "
                       f"are unserved: a {plan.planning_gap_wh:.0f} Wh planning shortfall.")
        else:
            kind, title = "bad", "Insufficient energy at minimum brightness"
            message = (f"Even with no reserve, the floor needs {plan.physical_gap_wh:.0f} Wh more. "
                       f"This reserve-aware plan leaves {plan.unmet_h:.2f} hours unserved.")
        st.html(f'<div class="status {kind}"><h3>{title}</h3><p>{message}</p></div>')
        metrics = st.columns(3)
        metrics[0].metric("Minimum needs", f"{plan.floor_wh:.0f} Wh")
        metrics[1].metric("Usable after reserve", f"{plan.budget_wh:.0f} Wh")
        metrics[2].metric("Planning margin", f"{plan.budget_wh - plan.floor_wh:+.0f} Wh")
        brightness_chart, battery_chart = energy_charts(plan)
        st.altair_chart(brightness_chart, width="stretch", theme=None)
        st.altair_chart(battery_chart, width="stretch", theme=None)
        st.caption(f"Synthetic plan · {plan.consumed_wh:.1f} Wh used + {plan.remaining_wh:.1f} Wh left = "
                   f"{scenario.energy_wh:.1f} Wh initially. Amber dashed energy line = held reserve.")
        if not plan.feasible:
            st.error(f"Service failure is explicit: the lamp switches off after {plan.service_h:.2f} hours. "
                     "The red interval fails the required minimum; it is not a valid all-night lighting plan.")
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
