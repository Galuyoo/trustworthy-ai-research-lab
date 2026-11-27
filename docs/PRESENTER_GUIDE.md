# Using AI to Support Engineering

Open the public Reliable AI Lab and keep the local copy ready. The presenter operates both labs. Use the existing QR for optional access.

## 16:25–16:35 · Lab 1

1. Open **Information availability**. Keep observation 20:00, forecast 20:10 and receipt 20:20. Point to the table below the timeline. The replay uses the late reading and scores 1 pp of error, while the live forecast scores 13 pp.
2. Move receipt to 20:10. The reading is now available to both forecasts and both score 1 pp. Click **Reset evidence**.
3. Open **Battery energy feasibility**. Choose **Close call**. The minimum needs 192 Wh and 198 Wh remain after a 10% reserve.
4. Raise the reserve to 15%. Show 187 Wh available and a 5 Wh shortfall.
5. Choose **Impossible** and set reserve to 0%. The 120 Wh battery serves 7.5 of the 12 hours. Click **Reset light**.

The timeline is a synthetic information-availability example. The battery exercise is synthetic and inspired by the published SETA battery-runtime and dimming research.

## 16:35–16:45 · Lab 2

1. Open **From Predictions to Decisions**. Use **Projector view** below the graph to enlarge the plot.
2. On Mixed, click **Reset example**, **Run nights** and **Pause** at Observe. Point out the 68% starting charge and expected recharge in the playback status below the buttons.
3. Advance through **Forecast** and **Choose plan**. Compare the fixed candidate forecast with the revised dashed adaptive forecast.
4. Advance through **Night discharge** and **Day recharge**. Compare the solid synthetic outcomes with the forecast. The first simulated dusk value becomes the next starting charge.
5. If time allows, compare Cloudy or Sunny. Click **Reset example** and return to the closing slide.

The simulator illustrates general engineering principles with synthetic values. SOC-loss budgets are percentage points.

## Offline

Run the local Streamlit app with Python and its dependencies already installed. The standalone simulator also opens directly in a browser. Both labs have screenshot fallbacks in the lecture pack.
