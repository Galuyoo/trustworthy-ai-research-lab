# Trustworthy AI Lab

A continuous, ten-minute interactive research journey for **From Engineering to Trustworthy AI: What Real Systems Taught Me** — Salaheddine Chouikh, invited BCU guest presentation, 30 November 2026.

A lightweight Streamlit teaching app. No sign-in in the app, database, external API, live telemetry, training, or research infrastructure is required. Dependencies are Streamlit and Altair; all calculations are deterministic and use tiny in-memory examples.

## Explore the story

- **The system.** Follow a measurement from streetlight and sensors through telemetry and forecasting to a proposed lighting plan. The illustrated signal is conceptual; it has no operational connection.

- **Can You Save the Light?** Adjust energy, night length, the lighting floor and a planning reserve. Scrub through the night and see the lamp, remaining energy, brightness plan and explicit unmet service. Try Comfortable, Close call and Impossible.
- **Catch the Data Leakage.** Move observation, forecast and receipt times, then reveal eligibility. Compare an invented frozen input with a later reconstruction, separately from fixed historical audit aggregates.

## Run locally (Python 3.12)

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run streamlit_app.py
```

Open the local URL printed by Streamlit. Install the dependencies before travelling; after installation, the app works offline. Paper and GitHub links require internet.

## Run tests

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

Tests cover exact preset outcomes, energy conservation, feasibility boundaries, inclusive cutoff rules, immutable research counts, the night scrubber, navigation, mode changes and independent/global reset actions.

Presentation mode folds deeper explanations without changing controls or results. All tabs retain their state. Animation is finite, optional and respects reduced motion. No custom JavaScript, external fonts or additional production dependencies are used.

## Deployment and review

The existing live app is [trustworthy-ai-lab.streamlit.app](https://trustworthy-ai-lab.streamlit.app/). This redesign is reviewed on `feature/premium-research-journey`; do not merge or replace the live app before review.

For a separate preview, create a new Streamlit Community Cloud app using this repository, branch `feature/premium-research-journey`, entrypoint `streamlit_app.py`, Python 3.12 and a separate available app URL. No secrets are needed.

The original app tracks `main`. See [validation](docs/VALIDATION.md) for verified test and deployment status.

## Scientific scope

**Every user-controlled example is synthetic.** Experiment 1 is an educational energy budget inspired by the published SETA paper; it neither reproduces the trained battery model nor the paper's numerical experiments. The original research used NASA laboratory battery discharge data and simulation-based evaluation with its own horizon definitions. No field validation or measured savings are claimed.

Experiment 2's timeline and reconstructed forecast are invented. Its purple research panel separately presents author-authorised historical aggregates: A1 782 paired forecasts, 184 resource-status eligible, 126 receipt-time eligible, 66 differing decisions (62 resource-only, 4 receipt-only); A2 87 forecasts, 348 model comparisons and 345 changed predictions across three nights. These findings apply to the particular audited subsets. Acceptance/publication of the second investigation is not asserted.

See [assumptions and limitations](docs/METHODS_AND_LIMITATIONS.md) and the [BCU and Agamine presenter walkthroughs](docs/PRESENTER_GUIDE.md).

## Public research

- [Salaheddine's GitHub](https://github.com/Galuyoo)
- [Published SETA paper](https://doi.org/10.1016/j.seta.2026.105315)
- [Original research code](https://github.com/Galuyoo/offgrid-streetlight-dimming-control)

Chouikh, S., Elmitwally, N., & Saeed, F. (2026). *Energy reliability and feasibility analysis for battery-constrained off-grid solar street lighting: an uncertainty-aware dimming control framework.* Sustainable Energy Technologies and Assessments, 93, 105315.

Acknowledgements: Nouh Elmitwally and Faisal Saeed, coauthors of the SETA paper. This independent teaching project contains no proprietary industrial assets or private observations.
