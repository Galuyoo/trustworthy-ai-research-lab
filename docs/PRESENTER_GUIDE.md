# Ten-minute presenter guide

## Before the talk

Open the live app early to wake it if the cloud host has put it to sleep. Keep a local copy running on your laptop and save the supplied screenshots locally. Rehearse at the projector's screen size. Both experiments work without internet once Python and requirements are installed.

## 0:00–5:00 — Can You Save the Light?

1. Start **Comfortable**. Ask: “Can this light last twelve hours?” Point out the required floor and optional target.
2. Click **Close call**. Minimum needs 192 Wh; usable after reserve is 198 Wh, so only 6 Wh remain above the floor.
3. Increase **reserve from 10% to 15%**. Now usable energy is 187 Wh: 5 Wh short. Ask why a more conservative plan can refuse service that nominal energy could support.
4. Click **Impossible**. Remove the reserve. Even then, 120 Wh cannot meet the 192 Wh minimum requirement. The lamp switches off rather than silently violating the brightness floor.
5. Say: “Prediction accuracy cannot create energy.” Click **Reset light**.

## 5:00–10:00 — Catch the Data Leakage

1. Open the second tab. At 20:00 the observation happens, 20:10 the forecast is issued, and 20:20 the observation arrives.
2. Ask: “Could the model have used this?” Toggle **Reveal the verdict**.
3. Move **Actual receipt time to 20:10**. Equality passes under this toy's explicitly inclusive rule. Move it after cutoff again.
4. Toggle **Use the later reconstructed input**. The input changes; the rule and outcome do not. Apparent error changes from 13 to 1 percentage point. This is a synthetic example, not an authentic audit row.
5. Scroll to the purple research panel. Explain **62 + 4 = 66**, while **184 − 126 = 58**. Mention the limited three-night A2 subset and avoid generalising these findings.
6. Finish: “Trust the decision—and check what the system actually knew.” Show the public source and paper links.

## Internet failure fallback

- Best: run `python -m streamlit run streamlit_app.py` locally after installing `requirements.txt` in advance. Rehearse with Wi-Fi off. App calculations and charts require no external services; links do.
- If Python cannot run: show the supplied screenshots and narrate the exact preset values above. Do not call screenshots interactive or claim a live app connection.
- If time is short: show Close call at 10%/15% reserve, then the default late-arrival example. Skip reconstruction and explain the fixed audit scope briefly.
