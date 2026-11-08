"""One research story: physical service, proposed plan, point-in-time evidence."""
from datetime import time, timedelta
from pathlib import Path
import streamlit as st
from lab_models import AUDIT, PRESETS, Scenario, clock, eligible, plan_energy, reconstruction_example
from lab_charts import energy_charts, event_timeline
from lab_state import (JOURNEY, STAGES, initialise, set_energy, reset_evidence,
                       start_over, go_to, receive_at_cutoff)
from lab_views import streetlight, night_scene, service_strip, verdict

st.set_page_config(page_title="Trustworthy AI Lab · Salaheddine Chouikh", page_icon="💡", layout="wide")
st.html(Path(__file__).with_name("styles.css"))
initialise()
if not st.session_state.motion:
    st.html('<style>*,*::before,*::after{animation:none!important;transition:none!important;scroll-behavior:auto!important}</style>')

with st.container(key="masthead_controls"):
    brand, mode, reset = st.columns([3, 1.15, .85], vertical_alignment="center")
    with brand:
        st.html('<div class="masthead"><div class="brand-mark" aria-hidden="true">◈</div><div>'
                '<div class="wordmark">Trustworthy AI Lab<span class="good">.</span></div>'
                '<div class="brand-note">Salaheddine Chouikh · independent research exhibit</div></div></div>')
    mode.toggle("Presentation mode", key="presentation", help="Keep explanations folded for a short demonstration. Controls and results stay the same.")
    reset.button("↺ Start over", on_click=start_over, width="stretch")

system_tab, energy_tab, evidence_tab = st.tabs(JOURNEY, key="journey", on_change="rerun")


def section(number, title, subtitle):
    st.html(f'<div class="section-top"><span class="section-number">{number}</span><div>'
            f'<h2>{title}</h2><p>{subtitle}</p></div></div>')


with system_tab:
    left, right = st.columns([1.1, 1], gap="large", vertical_alignment="center")
    with left:
        st.html('<div class="hero-copy"><div class="eyebrow">From engineering to trustworthy AI</div>'
                '<h1>A forecast is only<br>part of <span>the story.</span></h1>'
                '<p>A streetlight has a limited battery and a whole night to serve. '
                'Can its proposed plan deliver—and can we trust the evidence behind it?</p></div>')
        st.button("Begin the night →", type="primary", on_click=go_to, args=(1,))
        st.caption("One system · two experiments · ten minutes")
    with right:
        st.html('<div class="hero-visual">' + streetlight(signal=True, motion=st.session_state.motion) +
                '<div class="hero-caption"><span>Physical service</span><span class="good">Evidence → proposed plan</span></div></div>')
    st.html('<div class="eyebrow" style="margin-top:14px">Follow one measurement through the system</div>')
    st.segmented_control("Conceptual workflow", STAGES, key="stage", selection_mode="single",
                         required=True, label_visibility="collapsed", width="stretch")
    explanations = {
        "Streetlight": ("A real constraint: light until dawn.", "The battery stores energy. The lamp uses it. A plan must respect the minimum service the night requires."),
        "Sensors": ("A measurement describes the battery.", "A sensor observes a value at a particular time. That event time is only one part of its history."),
        "Telemetry": ("The value still has to arrive.", "Receipt is when the monitoring system gets the observation. A delayed reading can arrive after a forecast was issued."),
        "Forecast": ("An estimate of what happens next.", "A forecast uses evidence available at issue time. An accurate estimate cannot create energy or justify using future evidence."),
        "Proposed plan": ("A proposal, with an explicit feasibility check.", "The plan allocates brightness within the energy budget. These teaching examples simulate proposals; they do not actuate a controller."),
    }
    title, text = explanations[st.session_state.stage]
    st.html(f'<div class="stage-detail"><div class="stage-number">0{STAGES.index(st.session_state.stage)+1}</div>'
            f'<div><strong>{title}</strong><p>{text}</p></div></div>')
    st.html('<p class="intro-note">Conceptual workflow · invented interactive values · no live telemetry or physical control. '
            'Fixed historical research counts are clearly labelled inside the evidence experiment.</p>')
    st.toggle("Animate the introductory data signal", key="motion", help="Two gentle passes show data travelling to the forecast. Your device’s reduced-motion preference is also respected.")


def energy_experiment():
    section("01", "Can you keep the light on until dawn?", "Synthetic energy experiment · change the budget, then move through the night.")
    with st.container(key="presets"):
        buttons = st.columns(4)
        for column, name in zip(buttons, PRESETS):
            column.button(name, on_click=set_energy, args=(name,), width="stretch")
        buttons[3].button("↺ Reset light", on_click=set_energy, width="stretch")
    controls, visual = st.columns([1, 1.85], gap="large")
    with controls:
        st.slider("Available battery energy (Wh)", 0, 600, step=5, key="energy")
        st.slider("Night duration (hours)", 4, 16, key="night")
        st.slider("Minimum required brightness (%)", 10, 100, step=5, key="minimum")
        st.slider("Conservative planning reserve (%)", 0, 40, step=1, key="reserve",
                  help="Share of starting energy held back. A planning choice, not a calibrated uncertainty probability.")
        st.checkbox("Aim for 80% brightness if energy allows", key="extra")
        s = Scenario(st.session_state.energy, st.session_state.night, st.session_state.minimum, st.session_state.reserve)
        plan = plan_energy(s, 80 if st.session_state.extra else s.minimum_pct)
        st.caption(f"40 W toy lamp at 100% · no overnight charging. Required floor **{s.minimum_pct:.0f}%**; optional target **{plan.desired_pct:.0f}%**.")
    with visual:
        if plan.feasible:
            tone, title = "good", "The minimum service is feasible"
            detail = f"{plan.brightness_pct:.1f}% for {s.night_h:.0f} h · {plan.reserve_wh:.0f} Wh held in reserve"
        elif plan.physically_feasible:
            tone, title = "warn", "The reserve makes this plan infeasible"
            detail = f"{plan.planning_gap_wh:.0f} Wh short with this reserve · {plan.unmet_h:.2f} h unserved"
        else:
            tone, title = "bad", "Not enough energy—even at the minimum"
            detail = f"Even with zero reserve: {plan.physical_gap_wh:.0f} Wh short"
        st.html(f'<div class="status-line {tone}"><strong>{title}</strong><span>{detail}</span></div>')
        st.html(night_scene(plan, st.session_state.night_progress))
        st.slider("Move through the simulated night (%)", 0, 100, key="night_progress",
                  help="A display-only scrubber. The energy and lighting plan do not change as you move it.")
        st.html(service_strip(plan, st.session_state.night_progress))
        st.html(f'<div class="budget-row"><div class="budget-item"><span>MINIMUM NEEDS</span><strong>{plan.floor_wh:.0f} Wh</strong></div>'
                f'<div class="budget-item"><span>USABLE AFTER RESERVE</span><strong>{plan.budget_wh:.0f} Wh</strong></div>'
                f'<div class="budget-item"><span>PLANNING MARGIN</span><strong class="{tone}">{plan.budget_wh-plan.floor_wh:+.0f} Wh</strong></div></div>')
    if not plan.feasible:
        st.error(f"Service failure is explicit: after {plan.service_h:.2f} hours the lamp is off, leaving {plan.unmet_h:.2f} hours unserved. "
                 "The red interval fails the required minimum.")
    with st.expander("See the full night · brightness & remaining energy", expanded=not st.session_state.presentation):
        brightness, battery = energy_charts(plan)
        c1, c2 = st.columns(2)
        c1.altair_chart(brightness, width="stretch", theme=None)
        c2.altair_chart(battery, width="stretch", theme=None)
        st.caption(f"Synthetic plan · {plan.consumed_wh:.1f} Wh used + {plan.remaining_wh:.1f} Wh left = {s.energy_wh:.1f} Wh initially. "
                   "Red shading = unmet service. Amber dashed energy line = unspent reserve.")
    with st.expander("The model · equations, assumptions & research limits"):
        st.markdown("**Minimum energy = 40 W × minimum brightness / 100 × night hours.**\n\n"
                    "Planning budget = starting energy × (1 − reserve / 100). If this covers the minimum, allocate "
                    "constant brightness up to the optional target. Otherwise, deliver the floor until the budget runs "
                    "out and mark the rest as unserved. The reserve stays in the battery. The scrubber shows a point "
                    "on that same plan; it does not simulate a different decision.\n\n"
                    "Linear power versus brightness, perfect conversion, no charging, standby load, temperature, ageing "
                    "or stochastic error. Battery bars show a fraction of starting usable energy, not measured SOC or "
                    "nominal capacity. Reserve is not a confidence interval.\n\n"
                    "**Inspired by the published SETA research; not a reproduction.** That paper used NASA laboratory "
                    "battery discharge data and simulation-based evaluation with its own horizons. These invented "
                    "values are not published numerical results, field validation, measured savings or physical actuation.")


with energy_tab:
    energy_experiment()
    st.html('<div class="bridge"><div class="signal" aria-hidden="true">◇</div><div><div class="eyebrow">Follow the telemetry</div>'
            '<p>We’ve assumed we know the battery state.<br><strong>But what if that measurement arrived too late?</strong></p>'
            '<div class="small">Same streetlight. Same decision. Now inspect what the system actually knew.</div></div></div>')
    st.button("Follow the measurement →", type="primary", on_click=go_to, args=(2,))


def evidence_experiment():
    section("02", "Could the model have used this measurement?", "Inside the same telemetry path · one observation, three times, two cutoff rules.")
    a, b, c = st.columns(3)
    for col, label, key in [(a, "Observation time", "observation"), (b, "Forecast issue / cutoff", "cutoff"),
                            (c, "Actual receipt time", "receipt")]:
        col.slider(label, min_value=time(20, 0), max_value=time(21, 0), step=timedelta(minutes=1), format="HH:mm", key=key)
    obs, cut, rec = [st.session_state[k].hour * 60 + st.session_state[k].minute for k in ("observation", "cutoff", "receipt")]
    st.altair_chart(event_timeline(obs, cut, rec), width="stretch", theme=None)
    controls = st.columns([1.55, 1, 1], vertical_alignment="center")
    controls[0].toggle("Reveal the verdict", key="reveal")
    controls[1].button("Receive at cutoff", on_click=receive_at_cutoff, width="stretch")
    controls[2].button("↺ Reset evidence", on_click=reset_evidence, width="stretch")
    resource_ok, receipt_ok = eligible(obs, cut), eligible(rec, cut)
    for col, label, ok, stamp in zip(st.columns(2), ["Observation / resource-time rule", "Receipt-time rule"],
                                    [resource_ok, receipt_ok], [obs, rec]):
        with col:
            st.html(verdict(label, ok, clock(stamp), clock(cut), st.session_state.reveal))
    if rec < obs:
        st.warning("Receipt is earlier than observation: inconsistent for one sensor event on a shared clock. "
                   "The comparisons still apply, but this is not a physically consistent history. A real resource-status clock may have different semantics.")
    if st.session_state.reveal:
        if resource_ok and not receipt_ok:
            st.error("The rules disagree. The system had not received this observation when the forecast was issued.")
        elif receipt_ok and not resource_ok:
            st.warning("The rules disagree. Receipt passes while observation fails. Check the clock-consistency warning above.")
        elif receipt_ok:
            st.success("The rules agree: both timestamps pass the cutoff. Availability alone does not establish quality or usefulness.")
        else:
            st.info("The rules agree: neither timestamp passes the cutoff.")
    else:
        st.info("Ask the audience first. Could this observation have informed the forecast? Reveal, then move the receipt time.")
    st.caption("Synthetic example · one date, one clock, minute resolution. Inclusive rule: timestamp ≤ cutoff. At equality, availability is assumed.")
    with st.expander("A second trap · what was issued then, and what is reconstructed later?", expanded=not st.session_state.presentation):
        st.caption("SYNTHETIC EXAMPLE · invented SOC values, forecast and outcome")
        st.toggle("Use the later reconstructed input", key="later")
        st.html('<div class="reconstruction">'
                f'<div class="record {"" if st.session_state.later else "selected"}"><div class="eyebrow">Frozen at issue time</div><strong>70% → 60%</strong><span>Input SOC → predicted later SOC</span></div>'
                f'<div class="record {"selected" if st.session_state.later else ""}"><div class="eyebrow">Later reconstruction</div><strong>58% → 48%</strong><span>A different input → a different prediction</span></div></div>')
        toy = reconstruction_example(st.session_state.later)
        m = st.columns(3)
        m[0].metric("Selected prediction", f"{toy.prediction_soc:.0f}%")
        m[1].metric("Fixed invented outcome", "47%")
        m[2].metric("Absolute error", f"{toy.absolute_error_pp:.0f} pp")
        st.caption("The rule always subtracts 10 percentage points. Changing the input changes the apparent error from 13 to 1 pp. "
                   "This does not correct the originally issued forecast or train a better model. Later reconstruction need not improve accuracy.")
    with st.expander("Actual research · fixed historical audit results", expanded=not st.session_state.presentation):
        st.html('<div class="research-heading">Authentic aggregates · separate from the synthetic exercises</div>')
        st.markdown("**A1 · Which evidence was eligible?**")
        r = st.columns(3)
        r[0].metric("Resource-status eligible", f"{AUDIT['resource_eligible']}/{AUDIT['a1_total']}")
        r[1].metric("Receipt-time eligible", f"{AUDIT['receipt_eligible']}/{AUDIT['a1_total']}")
        r[2].metric("Individual decisions changed", str(AUDIT["changed"]))
        st.markdown("**62 resource-only + 4 receipt-only = 66 changes.** The sets are not nested. "
                    "184 − 126 = 58 is the difference in totals, not the number of changed decisions.")
        st.caption("122 under both rules · 594 under neither (derived). 782 paired forecasts · 13 nights · 11 poles · parser-usable subset. "
                   "The toy sensor clock does not reproduce the original resource-status protocol or explain its four receipt-only cases.")
        st.markdown("**A2 · Does later reconstruction change predictions?**")
        r = st.columns(3)
        r[0].metric("Forecasts audited", str(AUDIT["a2_forecasts"]))
        r[1].metric("Predictions that differed", f"{AUDIT['a2_changed']}/{AUDIT['a2_comparisons']}")
        r[2].metric("Nights in this subset", str(AUDIT["a2_nights"]))
        st.caption("348 model comparisons across 87 forecasts. A changed prediction is not automatically a better prediction.")
        st.warning("Scope matters: specific audited subsets from one deployment. A1 is parser-conditioned; A2 is a limited three-night retrospective subset. "
                   "These are not universal or whole-fleet rates. Publication or acceptance of this second investigation is not asserted.")
    with st.expander("Timing assumptions & the integrity lesson"):
        st.markdown("**Happening earlier does not mean being available earlier.** Freeze the inputs and prediction at issue time. "
                    "Preserve a later reconstruction as a separate object.\n\n"
                    "The toy compares observation time and receipt time separately against an inclusive cutoff. Real systems need explicit ordering "
                    "and ingestion latency at equal timestamps. Availability is not proof of freshness, validity or usefulness. "
                    "This toy does not reproduce A1 matching, parsing or freshness rules. Its clock-inconsistent case must not be used to explain real receipt-only cases.")


with evidence_tab:
    evidence_experiment()
    st.html('<div class="takeaway"><strong>Trust the decision. Preserve what the system knew.</strong><br>'
            'Energy feasibility and evidence integrity belong in the same research story.</div>')
    st.button("← Return to the lighting plan", on_click=go_to, args=(1,))

st.html('<div class="footer"><div class="footer-links">'
        '<a href="https://doi.org/10.1016/j.seta.2026.105315" target="_blank" rel="noopener">Published SETA paper ↗</a> &nbsp;·&nbsp; '
        '<a href="https://github.com/Galuyoo/offgrid-streetlight-dimming-control" target="_blank" rel="noopener">Research code ↗</a> &nbsp;·&nbsp; '
        '<a href="https://github.com/Galuyoo/trustworthy-ai-research-lab" target="_blank" rel="noopener">Exhibit source ↗</a></div>'
        'SETA research: Salaheddine Chouikh, Nouh Elmitwally & Faisal Saeed.<br>'
        'Independent teaching demonstration · synthetic interactive values · no company endorsement, live telemetry or physical control.</div>')
