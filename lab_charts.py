"""Small native Altair charts, with explicit units and accessible descriptions."""
import altair as alt
from lab_models import EnergyPlan, clock

TEAL = "#087f8c"
RED = "#c23d49"
GOLD = "#b46b0c"
NAVY = "#183247"


def style(chart):
    return (chart.configure_view(strokeWidth=0)
            .configure_axis(labelFontSize=13, titleFontSize=13, gridColor="#e7e9e8",
                            titleColor=NAVY, labelColor=NAVY)
            .configure_legend(labelFontSize=12, title=None, orient="bottom"))


def energy_charts(plan: EnergyPlan):
    h = plan.scenario.night_h
    x = alt.X("hour:Q", title="Hours since nightfall", scale=alt.Scale(domain=[0, h]),
              axis=alt.Axis(tickCount=6))
    brightness = [{"hour": 0, "brightness": plan.brightness_pct}]
    if plan.unmet_h > 1e-9:
        brightness += [{"hour": plan.service_h, "brightness": 0}, {"hour": h, "brightness": 0}]
    else:
        brightness += [{"hour": h, "brightness": plan.brightness_pct}]
    base = alt.Chart(alt.Data(values=brightness))
    actual = base.mark_area(interpolate="step-after", color=TEAL, opacity=0.22).encode(
        x=x, y=alt.Y("brightness:Q", title="Brightness (%)", scale=alt.Scale(domain=[0, 105])))
    line = base.mark_line(interpolate="step-after", color=TEAL, strokeWidth=3).encode(
        x=x, y="brightness:Q", tooltip=[alt.Tooltip("brightness:Q", format=".1f", title="Delivered (%)")])
    refs = alt.Chart(alt.Data(values=[
        {"value": plan.scenario.minimum_pct, "label": "Required minimum"},
        {"value": plan.desired_pct, "label": "Desired target"},
    ])).mark_rule(strokeDash=[6, 5]).encode(
        y="value:Q", color=alt.Color("label:N", scale=alt.Scale(
            domain=["Required minimum", "Desired target"], range=[RED, GOLD])),
        tooltip=["label:N", alt.Tooltip("value:Q", title="Brightness (%)")])
    layers = [actual, line, refs]
    if plan.unmet_h > 1e-9:
        gap = alt.Chart(alt.Data(values=[{"start": plan.service_h, "end": h}])).mark_rect(
            color=RED, opacity=0.13).encode(x="start:Q", x2="end:Q")
        layers.insert(0, gap)
    top = alt.layer(*layers).properties(height=170,
        description="Synthetic brightness plan. Dashed lines show minimum and desired brightness. Red shading is unmet service.")
    points = sorted(set([0.0, h, plan.service_h] + [h * i / 48 for i in range(49)]))
    battery = alt.Chart(alt.Data(values=[{"hour": t, "energy": plan.remaining_at(t)} for t in points]))
    area = battery.mark_area(color=TEAL, opacity=0.13).encode(
        x=x, y=alt.Y("energy:Q", title="Battery energy (Wh)", scale=alt.Scale(domain=[0, max(50, plan.scenario.energy_wh * 1.08)])))
    trace = battery.mark_line(color=TEAL, strokeWidth=3).encode(x=x, y="energy:Q",
        tooltip=[alt.Tooltip("hour:Q", format=".2f", title="Hour"), alt.Tooltip("energy:Q", format=".1f", title="Remaining (Wh)")])
    reserve = alt.Chart(alt.Data(values=[{"reserve": plan.reserve_wh, "label": "Held reserve"}])).mark_rule(
        color=GOLD, strokeDash=[6, 5]).encode(y="reserve:Q", tooltip=["label:N", alt.Tooltip("reserve:Q", title="Wh")])
    bottom = (area + trace + reserve).properties(height=170,
        description="Synthetic remaining battery energy. The dashed amber line is the unspent planning reserve.")
    return style(top), style(bottom)


def event_timeline(observation: int, cutoff: int, receipt: int):
    rows = [
        {"minute": observation, "event": "Observation", "time": clock(observation)},
        {"minute": cutoff, "event": "Forecast issued", "time": clock(cutoff)},
        {"minute": receipt, "event": "Receipt", "time": clock(receipt)},
    ]
    order = ["Observation", "Forecast issued", "Receipt"]
    base = alt.Chart(alt.Data(values=rows)).encode(
        x=alt.X("minute:Q", scale=alt.Scale(domain=[1195, 1265], zero=False, nice=False), title="Same day · shared clock",
                axis=alt.Axis(values=[1200, 1215, 1230, 1245, 1260],
                              labelExpr="floor(datum.value/60) + ':' + (datum.value%60 < 10 ? '0' : '') + datum.value%60")),
        y=alt.Y("event:N", sort=order, title=None, axis=alt.Axis(labelLimit=150)),
        color=alt.Color("event:N", sort=order, scale=alt.Scale(domain=order, range=[TEAL, NAVY, GOLD]), legend=None))
    cutoff_line = alt.Chart(alt.Data(values=[{"minute": cutoff}])).mark_rule(
        color=NAVY, strokeDash=[5, 4], opacity=0.55).encode(
            x=alt.X("minute:Q", scale=alt.Scale(domain=[1195, 1265], zero=False, nice=False)))
    markers = base.mark_point(filled=True, size=220).encode(
        shape=alt.Shape("event:N", scale=alt.Scale(domain=order, range=["circle", "diamond", "square"]), legend=None),
        tooltip=["event:N", "time:N"])
    labels = base.mark_text(dy=-23, fontSize=16, fontWeight="bold").encode(text="time:N")
    return style((cutoff_line + markers + labels).properties(height=215,
        description="Synthetic observation, forecast cutoff and receipt times, shown on separate rows to keep coincident timestamps legible."))
