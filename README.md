# Trustworthy AI Lab

Two interactive experiments for **From Engineering to Trustworthy AI: What Real Systems Taught Me** — Salaheddine Chouikh, invited BCU guest presentation, 30 November 2026.

A lightweight Streamlit teaching app. No sign-in in the app, database, external API, live telemetry, training, or research infrastructure is required. Dependencies are Streamlit and Altair; all calculations are deterministic and use tiny in-memory examples.

## Try the experiments

- **Can You Save the Light?** Adjust energy, night length, the lighting floor and a planning reserve. See the brightness plan, remaining energy, and explicit unmet service. Try Comfortable, Close call and Impossible.
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

Tests cover exact preset outcomes, an energy-conservation grid, feasibility boundaries, inclusive timestamp rules, immutable research counts, and Streamlit widget interactions and resets.

## Streamlit Community Cloud

Deployment target: the public `Galuyoo/trustworthy-ai-research-lab` repository, branch `main`, entrypoint `streamlit_app.py`, Python 3.12. Choose an available short URL such as `trustworthy-ai-lab.streamlit.app` during deployment. No secrets are needed. A proposed URL is not evidence of a live deployment; see `docs/VALIDATION.md` for the actual verified status.

## Scientific scope

**Every user-controlled example is synthetic.** Experiment 1 is an educational energy budget inspired by the published SETA paper; it neither reproduces the trained battery model nor the paper's numerical experiments. The original research used NASA laboratory battery discharge data and simulation-based evaluation with its own horizon definitions. No field validation or measured savings are claimed.

Experiment 2's timeline and reconstructed forecast are invented. Its purple research panel separately presents author-authorised historical aggregates: A1 782 paired forecasts, 184 resource-status eligible, 126 receipt-time eligible, 66 differing decisions (62 resource-only, 4 receipt-only); A2 87 forecasts, 348 model comparisons and 345 changed predictions across three nights. These findings apply to the particular audited subsets. Acceptance/publication of the second investigation is not asserted.

See [assumptions and limitations](docs/METHODS_AND_LIMITATIONS.md) and the [ten-minute presenter guide](docs/PRESENTER_GUIDE.md).

## Public research

- [Salaheddine's GitHub](https://github.com/Galuyoo)
- [Published SETA paper](https://doi.org/10.1016/j.seta.2026.105315)
- [Original research code](https://github.com/Galuyoo/offgrid-streetlight-dimming-control)

Chouikh, S., Elmitwally, N., & Saeed, F. (2026). *Energy reliability and feasibility analysis for battery-constrained off-grid solar street lighting: an uncertainty-aware dimming control framework.* Sustainable Energy Technologies and Assessments, 93, 105315.

Acknowledgements: Nouh Elmitwally and Faisal Saeed, coauthors of the SETA paper. This independent teaching project contains no proprietary industrial assets or private observations.
