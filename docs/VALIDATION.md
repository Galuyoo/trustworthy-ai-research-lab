# Validation and deployment checkpoint

Verified 7 November 2026, Python 3.12.14, Streamlit 1.67.0 and Altair 6.3.0.

| Check | Result |
| --- | --- |
| Calculation and Streamlit application tests | 308 passed |
| All three energy presets, reserve tipping point and reset | Passed |
| Energy conservation, bounds, explicit infeasibility | Passed over 288 input combinations plus targeted cases |
| Timestamp crossings and inclusive equality | Passed |
| Reconstruction changes only synthetic inputs; audit counts fixed | Passed |
| App launches from local source | Passed; fresh server/browser session |
| Desktop browser, 1440 × 1150 | Passed; preset and reveal controls, no horizontal overflow |
| Mobile browser, 390 × 844 | Passed; responsive stacking, controls and timeline |
| Browser JavaScript errors | None observed |
| External runtime dependencies | External requests blocked in browser tests; none requested |
| Public profile, research repository and DOI links | HTTP 200; DOI resolved to the publisher |
| Secret-pattern scan and manual publication review | No credentials, private telemetry or proprietary source files present |
| Streamlit Community Cloud | **Pending sign-in and deployment; no live URL claimed** |

The calculation tests include 0 Wh, exact feasibility, 100% reserve at model level, and minimum brightness higher than the optional desired target. UI tests cover resets and changes to synthetic controls without changing historical audit facts. Browser tests use a newly started local Streamlit process, with all non-local requests blocked, to verify that the application runs independently of external services. Screenshots show the rendered application, not design mockups.

Source scope: original educational code, tiny synthetic examples, and explicitly authorised aggregate counts. No production services, collectors, controllers, training runs or frozen artifacts were touched. The original public research repository and presentation plans were read only.

## Remaining deployment step

Sign in to Streamlit Community Cloud and, if needed, authorise access to this public GitHub repository. Deploy `main` / `streamlit_app.py`, Python 3.12, without secrets. Then verify the actual public URL in a fresh unauthenticated browser, both experiments and the source link before recording deployment as complete. Community Cloud was observed at its sign-in screen; its terms/access prompts must be completed by the account holder.

## Offline fallback

See `PRESENTER_GUIDE.md`. Install dependencies before the event and launch locally. The source is self-contained but the ZIP does not include Python or third-party packages. Save the supplied screenshots locally as an additional fallback.
