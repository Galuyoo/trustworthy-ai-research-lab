# Synthetic assumptions and research limitations

## Energy budget

Units: energy in watt-hours (Wh), electrical power in watts (W), time in hours (h), brightness as percent of this toy lamp's maximum.

Let E be starting usable battery energy, H night duration, m minimum brightness, r reserve percent, d desired brightness. Power at 100% is fixed at 40 W. The model assumes P(b) = 40 × b/100. R = E × r/100 is withheld; B = E − R is available to the plan. Minimum energy is F = 40 × m/100 × H.

- **Physically feasible under the toy assumptions:** E >= F.
- **Feasible with the chosen reserve:** B >= F.
- When feasible, constant brightness is max(m, min(max(m,d), 100B/(40H))). Optional brightness is allocated only after protecting the all-night minimum.
- Otherwise, brightness is m until t_stop = B/(40m/100), then zero. Zero is explicitly labelled unmet service, never an acceptable dimming allocation. This deliberately shows one best-duration allocation at the floor, not an all-night feasible controller.
- Remaining energy at time t is E − 40 × b/100 × min(t,t_stop). The reserve remains in the battery. Used energy + remaining energy = starting energy.
- Planning energy gap: max(0,F−B). Physical energy gap without reserve: max(0,F−E). Unserved duration is max(0,H−t_stop).

This assumes no charging, losses, standby load, temperature, ageing, nonlinear dimming, voltage limits or stochastic error. Reserve is a planning assumption, not a confidence interval or calibrated uncertainty model. Available battery energy already means usable energy; nominal capacity and state of charge are not inferred.

The drawing and chart values are synthetic. The paper's trained runtime model, NASA laboratory discharge data, experimental horizons, research uncertainty procedure and numerical outcomes are not reproduced. This app is not field validation, a deployed controller, a savings estimate or operational advice.

## Timestamp eligibility

Toy timestamps share one date, one clock and minute resolution. A record passes a rule iff that rule's timestamp is **less than or equal to** the forecast cutoff. Receipt precisely at cutoff is assumed available; real systems may need explicit ordering or ingestion/processing latency at equal timestamps. Availability alone does not establish feature validity, freshness or usefulness.

Observation time <= cutoff and receipt time <= cutoff are evaluated separately. Receipt < observation is shown as a clock-inconsistent sensor event, not quietly accepted as a physical history. Real resource-status timestamps need not have the same semantics as a sensor event timestamp. The toy does not reproduce the full A1 inclusion protocol, parser, matching or freshness rules, and its inconsistent-clock state does not explain the real receipt-only cases.

## Live and replay forecast comparison

Both rules fall back to the earlier 70% SOC reading when the new 58% reading fails their cutoff. The simulated live rule uses receipt time, and the replay rule uses observation time. The rule predicts input minus 10 percentage points against a fixed synthetic outcome of 47%. If the reading was observed before cutoff but arrived afterward, the replay reports 1 pp of absolute error and the live forecast reports 13 pp. If both rules allow or exclude the new reading, the scores match. The example illustrates how leakage can make a replay look better; a different outcome could make the replay look worse.

## Sources and attribution

Published research: https://doi.org/10.1016/j.seta.2026.105315


All application logic was written separately for this educational project. No production code, trained models, private datasets, credentials or proprietary artwork were copied. No external data is loaded at runtime.
