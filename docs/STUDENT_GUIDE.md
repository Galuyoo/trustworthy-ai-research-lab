# Student guide

Use the [live lab](https://trustworthy-ai-lab.streamlit.app/) or [run it locally](../README.md#local-installation-and-offline-use). All inputs and outcomes are synthetic. SOC means battery state of charge. pp means percentage points.

## Information availability and forecasting

1. Reset the evidence experiment. Compare the timestamps admitted by the receipt-time and observation-time rules. Which rule can a live service implement when readings arrive with a delay?
2. Move receipt to the cutoff, then one minute after it. Record the input, forecast and error under both rules. Why does a lower replay error in the second case give a misleading impression of live accuracy?
3. Move the observation and receipt until both are after the cutoff. Does the same rule always make one forecast look better? What would a production system need to record to support a reliable replay?

## Energy feasibility and planning reserves

1. Choose **Close call**. Vary the reserve and locate the largest whole-percentage reserve that still meets the minimum. Verify it using the starting Wh, the reserve percentage and the required Wh.
2. Choose **Impossible** with zero reserve. Raise battery energy until the full night is feasible. Can a perfect prediction fill the original shortfall? What could an engineer change to reduce it?
3. Compare keeping a reserve with spending the full budget. What benefit would the reserve provide if the battery delivered less energy than expected? What service might be lost in return?

## Fixed and adaptive strategies

1. Select **Mixed** and **Start paused**. Advance through the first two nights. Write down each adaptive overnight budget and compare it with the standard fixed plan. Why do the adaptive budgets differ?
2. Reset and compare **Mixed**, **Cloudy** and **Sunny**. Can one fixed plan meet both the reserve and dusk target in every scenario? Use the graph to support your answer.
3. In **Advanced settings**, increase **Forecast recharge reduction** and repeat a night. Compare dashed forecasts with the later solid outcomes. Which constraints change the chosen plan? When does a more conservative forecast leave more charge than expected at dusk?
