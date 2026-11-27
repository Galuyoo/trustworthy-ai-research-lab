# Presenter guide

Open the [Reliable AI Lab](https://trustworthy-ai-lab.streamlit.app/) and the local copy before the session. Use slide 28 to introduce the demonstrations. The existing QR is for optional access.

## 16:25–16:32 · Information availability and data leakage

1. Open **Information availability** and enable **Projector view** if useful.
2. Reset to observation 20:00, forecast cutoff 20:10 and receipt 20:20. Point to the timeline and the comparison directly beneath it. The live forecast has **13 pp** absolute error. The replay has **1 pp** because its observation-time rule admits a reading that arrived late.
3. Move **Receipt time** to **20:10**. The reading now arrives by the cutoff, so both forecasts can use it and score **1 pp**.
4. Click **Reset evidence**, then **Next: battery energy**.

## 16:32–16:37 · Battery energy feasibility

1. Choose **Close call**. The battery starts with **220 Wh**. With a **10%** reserve, **198 Wh** is usable against **192 Wh** required.
2. Raise the reserve to **15%**. The usable budget falls to **187 Wh**, a **5 Wh** planning shortfall.
3. Choose **Impossible**, then set reserve to **0%**. The **120 Wh** battery serves **7.5 of the required 12 hours**. The brightness plot shows when service stops.
4. Click **Reset light**, then **Next: Lab 2**.

## 16:37–16:45 · Adaptive energy management

1. On **Mixed**, click **Reset example**, then **Start paused**. Use **Projector view** as needed. The graph holds at **Observe**.
2. Compare the three fixed lighting strategies with the adaptive strategy. Point out that the model tracks state-of-charge changes in percentage points.
3. Use **Next stage** at each step. On **Observe**, identify the 68% starting charge, expected 45 pp recharge and the reserve. At **Forecast**, the standard fixed plan predicts 49% at dawn and 94% at dusk. At **Choose plan**, explain the 32 pp loss cap and the revised 36% dawn and 81% dusk forecasts.
4. **Night discharge** reveals the solid simulated dawn at 36%. **Day recharge** reveals the simulated dusk at 81%, which becomes the next starting charge.
5. Click **Next stage** to begin the second night at Observe. Walk through the same stages. Expected recharge is now 10 pp, so the adaptive plan budgets 21 pp overnight and forecasts 60% at dawn and 70% at dusk. Compare forecasts and simulated outcomes.
6. If time permits, select Cloudy or Sunny and compare the trajectories. Pause remains available during **Run nights**. **Resume** continues automatic playback at the selected speed.

## 16:45–17:00 · Conclusion and Q&A

Return to PowerPoint at slide 29. If time is short, demonstrate the first rolling night and use the second night’s starting charge to close the example.

## Offline

Before leaving for the venue, install the dependencies and start the local app using the [README](../README.md#local-installation-and-offline-use). Open the standalone HTML in a browser if the local Streamlit app is unavailable. The screenshots in the README provide a static fallback.
