# Premium journey validation — 8 November 2026

## Scope and status

The original live app at https://trustworthy-ai-lab.streamlit.app/ was inspected before work. The redesign is isolated on `feature/premium-research-journey`, based on `main` commit `9f85ba89d0f27b2180734784bcb59c9c8f21f132`.

`main` and its deployment are preserved. A separate branch preview requires a new Streamlit Community Cloud deployment; a local browser test is not a hosted deployment. The PR reports the final preview status.

## Scientific regression checks

- Baseline: 308 tests passed before edits.
- Redesign: 328 tests passed, including all original tests and 20 new cases.
- `lab_models.py` and `tests/test_models.py` are byte-for-byte unchanged from the base commit.
- The new tests cover energy conservation during the display-only night scrubber, the exact service-stop boundary, zero energy, dawn, invalid progress, navigation/mode state preservation, global and independent resets, and receipt equality against the current cutoff.
- Fixed A1 and A2 counts remain independent of every synthetic control. No research artifacts, trained models, private telemetry, credentials, site identifiers or infrastructure code were added.

Run the Python suite with `python -m pytest -q` after installing `requirements-dev.txt`.

## Actual browser checks

Chromium 153, isolated local Streamlit server, external requests blocked during testing:

| Viewport | Interaction checks | Horizontal overflow | Runtime exceptions |
| --- | --- | --- | --- |
| Desktop, 1440 × 1000 | Passed | None | None |
| Projector, 1280 × 720 | Passed | None | None |
| Mobile, 390 × 844; reduced motion | Passed | None | None |

The browser run exercised the intro CTA, Close call 10% → 15%, Impossible with zero reserve, dawn and unserved-night views, chart expansion, the transition to evidence, reveal, equality and receipt crossing, state preservation in both directions, reconstruction, fixed counts, independent reset, global reset, and presentation/exploration mode. It captured actual app screenshots. No external runtime requests or browser page errors were recorded.

The final implementation uses ordinary Streamlit reruns. Partial fragment reruns were removed after browser testing exposed a mismatch between displayed widget states and computed results. The full rerun route passed the same checks with stable values. Local reserve-change feedback was sub-second in the measured run; cloud cold starts and network latency are not represented by this measurement.

The core energy view fits a 1280 × 720 projector screen. Details, the narrative bridge and research panels intentionally require a short scroll. Mobile stacks content vertically. Keyboard adjustment, native accessible controls, labelled diagram images, text status alongside colours, visible focus styling, finite animation, an explicit motion toggle and reduced-motion CSS are present. This is not a formal accessibility certification or a claim of every-browser coverage.

## Reproduce the browser check

Python dependencies must be installed first. The browser tooling is optional development tooling, not a production dependency:

```bash
npm install --no-save playwright
npx playwright install chromium
node tests/browser_smoke.mjs
```

The script launches and stops its own local server, blocks non-local requests, and writes screenshots plus `browser_test_results.json` to `browser-results/` (gitignored). Set `LAB_PYTHON` to the desired Python executable and `LAB_QA_OUTPUT` to another output directory if needed. This development environment used a packaged Chromium executable; the portable script uses Playwright's installed Chromium.

## Separate preview configuration

Create a **new app**, leaving the existing `main` app unchanged:

- Repository: `Galuyoo/trustworthy-ai-research-lab`
- Branch: `feature/premium-research-journey`
- Main file: `streamlit_app.py`
- Python: 3.12
- URL: a separate available preview subdomain
- Secrets: none

Review the PR and preview before merging. Do not repoint the existing app as a shortcut.
