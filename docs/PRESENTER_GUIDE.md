# Presenter walkthroughs

## Before either demonstration

Open the app early to wake the hosting service. Use **Presentation mode** and click **Start over**: the system introduction opens, Comfortable is restored, the night view is at 35%, and both evidence examples reset. Your presentation and motion preferences stay unchanged. Every section is available from the three tabs. Moving between them preserves the experiment inputs.

Rehearse at the actual projector resolution. At 1280 × 720 the core energy controls, night visual and budget fit on screen; the transition and deeper charts require a short scroll. On mobile the controls stack. Use the arrow keys on a focused slider for precise adjustments. The main interactions work with motion disabled and with an operating-system reduced-motion preference.

The introductory signal makes only two gentle passes. It illustrates data moving toward a forecast, not live infrastructure or physical actuation. There is no automatic playback to manage: move the night scrubber deliberately.

## BCU · 10 minutes

| Time | Action | Question or takeaway |
| --- | --- | --- |
| 0:00–1:00 | Start at **The system**. Select Sensors, Telemetry, Forecast, Proposed plan in the workflow. | “A streetlight must serve a night. We need both a feasible decision and evidence the system really had.” Explain that this is a conceptual, synthetic teaching app. |
| 1:00–2:00 | **Begin the night**. Keep Comfortable. Move the night scrubber toward dawn. | “Can this light serve all twelve hours?” The lamp delivers 80%; 384 Wh is consumed and 96 Wh remains at dawn, including the 48 Wh reserve. The lamp turns off at dawn because service is complete. |
| 2:00–3:30 | Choose **Close call**, then increase reserve from **10% to 15%**. | Minimum needs 192 Wh. The usable budget falls from 198 to 187 Wh: margin +6 becomes −5 Wh. Nominal energy could cover the minimum, but this chosen reserve cannot. The red interval is unmet service. |
| 3:30–4:30 | Choose **Impossible**, remove reserve, then move the scrubber late into the night. Optionally open the full-night charts. | 120 Wh cannot meet a 192 Wh requirement, even with no reserve. At the 40% floor it serves 7.5 of 12 hours, leaving 4.5 unserved. “Prediction accuracy cannot create energy.” |
| 4:30–5:00 | Read the bridge and click **Follow the measurement**. | “We’ve assumed we know the battery state. But what if that measurement arrived too late?” |
| 5:00–6:30 | Keep 20:00 observation, 20:10 issue, 20:20 receipt. Ask before toggling **Reveal the verdict**. | Observation time passes; receipt time fails. Earlier observation does not establish earlier availability. |
| 6:30–7:30 | Click **Receive at cutoff**, then move receipt one minute later. | Equality passes under this toy’s inclusive rule. After cutoff, the receipt verdict changes. Real systems also need explicit ingestion/order semantics. |
| 7:30–8:30 | Expand the second trap. Toggle **Use the later reconstructed input**. | Frozen 70% input → 60% prediction; later 58% input → 48% prediction; fixed invented outcome 47%. The error changes 13 → 1 pp because the input changed. This is not a model improvement, and reconstruction need not improve accuracy. |
| 8:30–9:30 | Expand **Actual research · fixed historical audit results**. | Distinguish the fixed authentic counts from the toys. A1: 62 + 4 = 66 changed decisions; 184 − 126 = 58 is only the difference in totals. A2: 345/348 predictions differed in a limited three-night retrospective subset. Do not generalise those rates. |
| 9:30–10:00 | Return to the plan or finish on the integrity lesson. | “Trust the decision. Preserve what the system knew.” Acknowledge Nouh Elmitwally and Faisal Saeed; the footer links the published SETA paper and public research code. |

## Agamine technical discussion · 5 minutes

| Time | Action | Technical focus |
| --- | --- | --- |
| 0:00–0:40 | Introduce the five-stage workflow. | Separate sensing, telemetry receipt, forecast issuance, proposed decisions and actual actuation. This public app has no operational connection or company endorsement. |
| 0:40–2:00 | Close call, 10% → 15% reserve; Impossible, reserve → 0%. | Distinguish physical feasibility from feasibility under a planning reserve. Expose the minimum service, energy shortfall and unserved interval rather than hiding a violation in a dimming value. |
| 2:00–3:00 | Follow the measurement; reveal the original timeline and test equality. | Define point-in-time eligibility, receipt latency and ordering at cutoff. A historical timestamp does not prove operational availability. |
| 3:00–4:00 | Show frozen versus reconstructed inputs. | Freeze issued features and predictions. Keep later reconstruction separately identifiable; changed inputs can change both predictions and scores. |
| 4:00–5:00 | Open the fixed research panel and state its scope. | A1 has non-nested sets; A2 covers only three retrospective nights. Discuss what evidence a prospective deployment must preserve. Do not infer whole-fleet reliability or operational performance from these counts. |

## Recovery and offline backup

- **Reset light** changes only the energy experiment, including its scrubber.
- **Reset evidence** restores the original timeline and both evidence toggles; it keeps the lighting inputs.
- **Start over** resets both experiments and returns to the introduction without changing presentation/motion preferences.
- If short on time, show Close call 10%/15% and the default late-arrival verdict. Skip the deeper panels.
- Install `requirements.txt` in advance and run `python -m streamlit run streamlit_app.py` locally. Once installed, the interactive app needs no network services; public links require internet.
- Keep the supplied actual screenshots as a fallback. Describe them as saved views, not a live simulation.
