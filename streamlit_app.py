"""Trustworthy AI Lab — a ten-minute, synthetic, offline-capable teaching app."""
from datetime import time, timedelta
from base64 import b64encode
import streamlit as st
from lab_models import AUDIT, PRESETS, Scenario, clock, eligible, plan_energy, reconstruction_example
from lab_charts import energy_charts, event_timeline

st.set_page_config(page_title="Trustworthy AI Lab · Salaheddine Chouikh", page_icon="💡", layout="wide")

st.html("""<style>
.stApp {font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;}
.block-container {max-width:1250px; padding-top:2rem; padding-bottom:2rem;}
h1,h2,h3 {letter-spacing:-0.035em;} h1 {font-size:clamp(2.2rem,4vw,3.4rem)!important;}
.eyebrow {font-size:.75rem;letter-spacing:.16em;font-weight:750;color:#087f8c;text-transform:uppercase;margin-bottom:12px;}
.hero {border-top:5px solid #087f8c;padding:23px 0 20px;}
.hero h1 {margin:0 0 8px;line-height:1.08;} .hero p {margin:8px 0;font-size:1.06rem;}
.muted {color:#526573;} .badge {display:inline-block;border-radius:6px;background:#e0efed;color:#12636b;padding:5px 9px;font-size:.73rem;font-weight:750;letter-spacing:.07em;text-transform:uppercase;}
.badge.research {background:#ebe7f6;color:#55417e;}
.status {border-radius:12px;padding:17px 20px;margin:8px 0 14px;border:1px solid #9acbc6;background:#e7f4ef;}
.status h3 {font-size:1.25rem;margin:0 0 5px;} .status p {margin:0;line-height:1.5;}
.status.warn {border-color:#dbba7a;background:#fff3d9;} .status.bad {border-color:#df9ca2;background:#ffedec;}
.lamp-scene {background:#132d43;border-radius:12px;color:#fff;display:flex;align-items:center;gap:10px;padding:8px 20px;margin-bottom:12px;}
.lamp-scene img {width:110px;height:120px;flex:0 0 110px;}
.lamp-scene strong {font-size:1.7rem;} .lamp-scene p {margin:2px 0;color:#d2e0eb;font-size:.85rem;}
.verdict {border-radius:12px;padding:15px 18px;background:#fff;border:1px solid #d7e0de;}
.verdict strong {font-size:1.6rem;display:block;} .verdict p {margin:0;font-size:.88rem;}
.takeaway {border-left:4px solid #087f8c;padding:10px 16px;background:#edf3f1;font-size:1.05rem;line-height:1.5;margin:14px 0;}
.research-box {border-top:3px solid #7e69a6;padding-top:16px;margin-top:20px;}
[data-testid="stMetricValue"] {font-size:1.7rem;} [data-baseweb="tab"] {font-size:1rem;font-weight:650;}
[data-testid="stSlider"] {padding-bottom:6px;} a {text-underline-offset:3px;}
@media(max-width:640px){.block-container{padding:1rem 1rem 2rem;}.hero{padding:16px 0}.lamp-scene strong{font-size:1.45rem;}[data-baseweb="tab"]{font-size:.84rem;}h2{font-size:1.65rem!important;}}
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

st.html("""<div class="hero"><div class="eyebrow">Birmingham City University · 30 November 2026 · Interactive research</div>
<h1>Trustworthy AI Lab<span style="color:#087f8c">.</span></h1>
<p><strong>From Engineering to Trustworthy AI: What Real Systems Taught Me</strong></p>
<p class="muted">Salaheddine Chouikh &nbsp;·&nbsp; Two experiments. Ten minutes. Test the decision—and the evidence behind it.</p></div>""")
from pathlib import Path
source_file = Path(__file__).parent / "SOURCE_URL.txt"
links = "[GitHub ↗](https://github.com/Galuyoo) &nbsp; · &nbsp; " \
        "[Published SETA paper ↗](https://doi.org/10.1016/j.seta.2026.105315) &nbsp; · &nbsp; " \
        "[Research code ↗](https://github.com/Galuyoo/offgrid-streetlight-dimming-control)"
if source_file.exists():
    links += f" &nbsp; · &nbsp; [Demo source ↗]({source_file.read_text().strip()})"
st.markdown(links, unsafe_allow_html=True)
st.caption("Explore an energy constraint, then discover how late data can change an evaluation. All interactive examples are synthetic.")

energy_tab, evidence_tab = st.tabs(["01 · Can You Save the Light?", "02 · Catch the Data Leakage"], key="experiment")

with energy_tab:
    st.html('<span class="badge">Synthetic educational simulation</span>')
    st.subheader("Can you keep this light on until dawn?")
    st.write("Start with a scenario. Then change the energy or reserve and watch the night change.")
    buttons = st.columns([1, 1, 1, 1])
    for column, name in zip(buttons, PRESETS):
        column.button(name, on_click=set_energy, args=(name,), width="stretch")
    buttons[3].button("↺ Reset light", on_click=set_energy, type="primary", width="stretch")

    controls, visual = st.columns([1, 1.8], gap="large")
    with controls:
        st.slider("Available battery energy (Wh)", 0, 600, step=5, key="energy")
        st.slider("Night duration (hours)", 4, 16, key="night")
        st.slider("Minimum required brightness (%)", 10, 100, step=5, key="minimum")
        st.slider("Conservative planning reserve (%)", 0, 40, step=1, key="reserve",
                  help="Hold back this share of starting energy. This is a planning choice, not a calibrated uncertainty probability.")
        st.checkbox("Aim for 80% brightness if energy allows", key="extra")
        scenario = Scenario(st.session_state.energy, st.session_state.night,
                            st.session_state.minimum, st.session_state.reserve)
        plan = plan_energy(scenario, 80 if st.session_state.extra else scenario.minimum_pct)
        st.caption(f"Required floor: **{scenario.minimum_pct:.0f}%** all night. "
                   f"Desired target: **{plan.desired_pct:.0f}%**. Extra brightness is optional.")
        st.caption("Toy lamp: 40 W at 100% brightness. No overnight charging. Night begins at hour 0.")

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
            kind, title = "bad", "Not enough energy—even at the minimum"
            message = (f"Even with no reserve, the floor needs {plan.physical_gap_wh:.0f} Wh more. "
                       f"This reserve-aware plan leaves {plan.unmet_h:.2f} hours unserved.")
        st.html(f'<div class="status {kind}"><h3>{title}</h3><p>{message}</p></div>')
        lamp_svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 110 120">
        <circle cx="85" cy="20" r="10" fill="#f2e5ab"/><circle cx="90" cy="16" r="10" fill="#132d43"/>
        <path d="M14 15h31l-5 12H10Z" fill="#487792" stroke="#a8c4d5"/><path d="M27 27v77M27 40h33" stroke="#bed3dc" stroke-width="4"/>
        <path d="M50 42h20l20 58H31Z" fill="#f7d873" opacity="{0.06 + plan.brightness_pct / 400:.3f}"/>
        <rect x="49" y="37" width="24" height="7" rx="3" fill="#ffe6a0"/><path d="M8 105h92" stroke="#78939e"/>
        <rect x="18" y="76" width="18" height="17" rx="3" fill="#87c3b9"/></svg>'''
        lamp_src = "data:image/svg+xml;base64," + b64encode(lamp_svg.encode()).decode()
        st.html(f'''<div class="lamp-scene"><img src="{lamp_src}" width="110" height="120"
        alt="Synthetic illustration of a solar streetlight at night"/>
        <div><strong>{plan.service_h:.2f} / {scenario.night_h:.0f} hours</strong><p>Simulated service at or above the floor</p>
        <p>Nightfall → {'Dawn' if plan.feasible else 'Budget exhausted → unserved night'}</p></div></div>''')
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
    st.html('<div class="takeaway"><strong>The lesson:</strong> A better prediction cannot create missing energy. '
            'A trustworthy system must recognise when the required service is infeasible.</div>')
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

with evidence_tab:
    st.html('<span class="badge">Synthetic timeline · no industrial observations</span>')
    st.subheader("Could the model have used this observation?")
    st.write("The sensor says it happened before the forecast. But when did the system receive it?")
    a, b, c = st.columns(3)
    for col, label, key in [(a, "Observation time", "observation"), (b, "Forecast issue / cutoff", "cutoff"),
                            (c, "Actual receipt time", "receipt")]:
        col.slider(label, min_value=time(20, 0), max_value=time(21, 0),
                   step=timedelta(minutes=1), format="HH:mm", key=key)
    obs, cut, rec = [st.session_state[k].hour * 60 + st.session_state[k].minute
                     for k in ("observation", "cutoff", "receipt")]
    st.altair_chart(event_timeline(obs, cut, rec), width="stretch", theme=None)
    st.caption("Synthetic example · all times share one date and clock. At the exact cutoff, the record counts as available.")
    if rec < obs:
        st.warning("Receipt is earlier than observation. That is inconsistent for a single sensor event on a shared clock. "
                   "The timestamp comparisons below still apply, but this is not a physically consistent event history. "
                   "A resource-status clock in a real system may have different semantics.")
    reveal, reset = st.columns([3, 1])
    reveal.toggle("Reveal the verdict", key="reveal")
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
    else:
        st.info("Make your prediction, then reveal the verdict. Move the cutoff or receipt time and try again.")
    st.html('<div class="takeaway"><strong>The lesson:</strong> Happening earlier does not mean being available earlier. '
            'A forecast must be evaluated using evidence available at its issue time.</div>')

    with st.expander("A second trap · can later history rewrite a score?", expanded=True):
        st.caption("ANOTHER SYNTHETIC EXAMPLE · invented input values, forecast and outcome")
        st.toggle("Use the later reconstructed input", key="later")
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

    st.html('<div class="research-box"><span class="badge research">Actual research · fixed historical audit aggregates</span></div>')
    st.subheader("What changed in the audited subsets?")
    st.caption("These counts stay fixed when you change the synthetic controls. Second research investigation: publication or acceptance is not asserted.")
    with st.container(border=True):
        st.markdown("**A1 · Timestamp eligibility**")
        r = st.columns(3)
        r[0].metric("Resource-status eligible", f"{AUDIT['resource_eligible']}/{AUDIT['a1_total']}")
        r[1].metric("Receipt-time eligible", f"{AUDIT['receipt_eligible']}/{AUDIT['a1_total']}")
        r[2].metric("Individual decisions changed", str(AUDIT["changed"]))
        st.markdown("**62 resource-only + 4 receipt-only = 66 changed decisions.** "
                    "The sets are not nested: 184 − 126 = 58 is the difference between totals, not the number of changes.")
        st.caption("122 eligible under both rules · 594 under neither (derived from the supplied counts). "
                   "782 paired forecasts · 13 nights · 11 poles · parser-usable subset.")
        st.divider()
        st.markdown("**A2 · Mutable reconstruction**")
        r = st.columns(3)
        r[0].metric("Forecasts audited", str(AUDIT["a2_forecasts"]))
        r[1].metric("Predictions that differed", f"{AUDIT['a2_changed']}/{AUDIT['a2_comparisons']}")
        r[2].metric("Nights in this subset", str(AUDIT["a2_nights"]))
        st.caption("348 model comparisons across 87 forecasts. A changed prediction is not automatically a better prediction.")
    st.warning("Scope matters: these findings describe particular audited research subsets from one deployment. "
               "They are not rates that generalise to all AI, all industrial sites or the whole fleet. "
               "A1 is parser-conditioned; A2 is a limited retrospective subset covering only three nights.")

st.divider()
st.caption("SETA research by Salaheddine Chouikh, Nouh Elmitwally and Faisal Saeed. "
           "Independent educational application · synthetic exercises · no live infrastructure connection.")
with st.expander("Presenter quick guide & offline backup"):
    st.markdown("**Minutes 0–5:** Start Comfortable. Ask if the light will last. Choose Close call; "
                "raise reserve from 10% to 15%. Choose Impossible and try removing the reserve. "
                "Show that the minimum itself needs more energy. Reset.\n\n"
                "**Minutes 5–10:** Open Catch the Data Leakage. Ask the audience before revealing the "
                "20:00 / 20:10 / 20:20 verdict. Move receipt to 20:10; equality passes. "
                "Toggle the reconstructed input, then show the separate fixed research panel.\n\n"
                "**Offline:** Install the requirements and launch this app on your laptop before the event. "
                "Once running locally, both experiments work without internet. Keep the supplied screenshots "
                "open as a second fallback; external paper and GitHub links require connectivity.")
