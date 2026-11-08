"""Small, self-contained illustrations. Display calculations only; no model changes."""
from base64 import b64encode
from dataclasses import dataclass
from html import escape
import math
from lab_models import EnergyPlan

TEAL = "#67e4cf"
AMBER = "#ffd18a"
RED = "#ff8d98"


@dataclass(frozen=True)
class NightFrame:
    hour: float
    remaining_wh: float
    remaining_fraction: float
    brightness_pct: float
    status: str


def night_frame(plan: EnergyPlan, progress: float) -> NightFrame:
    """View a plan at a percentage of the night, without altering the plan."""
    if not math.isfinite(progress) or not 0 <= progress <= 100:
        raise ValueError("Night progress must be between 0 and 100")
    hour = plan.scenario.night_h * progress / 100
    remaining = plan.remaining_at(hour)
    # At the exact service boundary, the lamp is off. At dawn, off is expected.
    status = "Dawn" if progress == 100 else "Serving" if hour < plan.service_h else "Unserved"
    return NightFrame(hour, remaining,
                      remaining / plan.scenario.energy_wh if plan.scenario.energy_wh else 0,
                      plan.brightness_pct if status == "Serving" else 0, status)


def svg_image(svg, alt, css_class=""):
    src = "data:image/svg+xml;base64," + b64encode(svg.encode()).decode()
    return f'<img class="{css_class}" src="{src}" alt="{escape(alt, quote=True)}"/>'


def streetlight(brightness=80, battery_fraction=.75, signal=False, motion=True, dawn=False):
    """Brightness controls the beam opacity; battery is relative to starting energy."""
    glow = max(0, min(100, brightness)) / 100
    fill = max(0, min(1, battery_fraction)) * 48
    animation = """
      @keyframes packet {0%,15%{opacity:0;transform:translateX(0)} 25%{opacity:1}
        80%{opacity:1} 100%{opacity:0;transform:translateX(98px)}}
      .packet{animation:packet 3.8s ease-in-out 2;}
      @media(prefers-reduced-motion:reduce){.packet{animation:none;}}
    """ if signal and motion else ""
    data_flow = """<path d="M221 119h104" stroke="#387b80" stroke-width="2" stroke-dasharray="4 6"/>
      <circle class="packet" cx="222" cy="119" r="4" fill="#67e4cf"/>
      <rect x="329" y="91" width="95" height="58" rx="10" fill="#112e3d" stroke="#43877e"/>
      <path d="M342 130l16-14 15 6 14-18 19 8" stroke="#67e4cf" stroke-width="2" fill="none"/>
      <text x="377" y="174" text-anchor="middle" fill="#acc2cd" font-size="12">Forecast</text>
    """ if signal else ""
    sky = "#1c3545" if dawn else "#0c1e2d"
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 460 310" role="img">
      <style>text{{font-family:system-ui,sans-serif}}{animation}</style>
      <defs>
        <linearGradient id="beam" x1="0" x2="0" y1="0" y2="1">
          <stop stop-color="#ffd38b" stop-opacity=".68"/>
          <stop offset="1" stop-color="#ffd38b" stop-opacity="0"/>
        </linearGradient>
        <radialGradient id="halo"><stop stop-color="#ffd18a" stop-opacity=".32"/>
          <stop offset="1" stop-color="#ffd18a" stop-opacity="0"/></radialGradient>
        <linearGradient id="pole"><stop stop-color="#8ba6b9"/><stop offset="1" stop-color="#425f73"/></linearGradient>
      </defs>
      <rect width="460" height="310" rx="20" fill="{sky}"/>
      <path d="M26 256h408M26 275h408" stroke="#254353" stroke-width="1"/>
      <path d="M30 57h45M52 35v44M390 39v4M388 41h4M316 56v4M314 58h4" stroke="#466171"/>
      <circle cx="375" cy="46" r="14" fill="#bfced2"/>
      <circle cx="382" cy="40" r="14" fill="{sky}"/>
      <ellipse cx="232" cy="238" rx="101" ry="30" fill="url(#halo)" opacity="{glow:.3f}"/>
      <path d="M214 101h37l66 151H148Z" fill="url(#beam)" opacity="{glow:.3f}"/>
      <rect x="154" y="62" width="9" height="195" rx="3" fill="url(#pole)"/>
      <path d="M158 99v-8q0-9 10-9h63q7 0 7 8" stroke="#9ab3c3" stroke-width="6" fill="none"/>
      <path d="M116 34h91l-17 32H99Z" fill="#163d58" stroke="#7398b1" stroke-width="2"/>
      <path d="M121 35l-15 30m38-30-15 30m38-30-15 30m38-30-15 30M108 49h90" stroke="#456e8a"/>
      <rect x="210" y="91" width="46" height="11" rx="5" fill="{'#ffe2aa' if glow else '#597080'}"/>
      <rect x="137" y="170" width="43" height="58" rx="7" fill="#163242" stroke="#7293a4"/>
      <rect x="149" y="180" width="19" height="5" rx="2" fill="#86a4b3"/>
      <circle cx="159" cy="204" r="6" fill="#67e4cf" opacity=".9"/>
      <circle cx="159" cy="204" r="13" stroke="#67e4cf" stroke-opacity=".28" fill="none"/>
      <path d="M141 257h35" stroke="#8aa5b6" stroke-width="5" stroke-linecap="round"/>
      <rect x="32" y="204" width="61" height="28" rx="5" stroke="#6e9aab" fill="none"/>
      <rect x="94" y="213" width="4" height="10" rx="1" fill="#6e9aab"/>
      <rect x="38" y="210" width="{fill:.2f}" height="16" rx="2" fill="#67e4cf"/>
      <text x="32" y="250" fill="#acc2cd" font-size="12">Energy</text>
      {data_flow}
      <text x="28" y="295" fill="#8faabc" font-size="10" letter-spacing="2">ILLUSTRATIVE · NO LIVE CONNECTION</text>
    </svg>'''
    return svg_image(svg, f"Illustrative solar streetlight: {brightness:.0f}% brightness. No live connection.", "streetlight")


def night_scene(plan, progress):
    frame = night_frame(plan, progress)
    failed = frame.status == "Unserved" or (frame.status == "Dawn" and not plan.feasible)
    tone = "bad" if failed else "good"
    label = "Dawn · service missed" if frame.status == "Dawn" and failed else "Minimum service missed" if failed else "Night complete" if frame.status == "Dawn" else "Minimum service delivered"
    return f'''<div class="night-scene">
      <div class="night-art">{streetlight(frame.brightness_pct, frame.remaining_fraction, dawn=frame.status == "Dawn")}</div>
      <div class="night-readout"><div class="eyebrow">Synthetic night · hour {frame.hour:.2f}</div>
        <div class="lamp-value">{frame.brightness_pct:.1f}<span>%</span></div>
        <div class="muted">brightness now</div>
        <div class="service-label {tone}">{label}</div>
        <div class="battery-label"><strong>{frame.remaining_wh:.1f} Wh</strong> remaining</div>
        <div class="battery-track"><div style="width:{frame.remaining_fraction * 100:.3f}%"></div></div>
        <div class="small muted">{frame.remaining_fraction * 100:.0f}% of starting energy · not battery SOC</div>
      </div></div>'''


def service_strip(plan, progress):
    served = min(100, 100 * plan.service_h / plan.scenario.night_h)
    return f'''<div class="service-track" role="img" aria-label="{plan.service_h:.2f} hours served; {plan.unmet_h:.2f} hours unserved">
       <div class="served" style="width:{served:.3f}%"></div><div class="unserved" style="width:{100-served:.3f}%"></div>
       <div class="time-cursor" style="left:{progress}%"></div></div>
       <div class="track-labels"><span>Nightfall</span><span>{plan.service_h:.2f} h served · {plan.unmet_h:.2f} h unserved</span><span>Dawn</span></div>'''


def verdict(label, ok, stamp, cutoff, revealed):
    tone = ("good" if ok else "bad") if revealed else "muted"
    value = ("Eligible" if ok else "Not eligible") if revealed else "Your prediction?"
    detail = f'{stamp} {"≤" if ok else ">"} cutoff {cutoff}' if revealed else "Reveal to test this cutoff rule"
    return f'<div class="verdict {tone}"><div class="small">{label}</div><strong>{value}</strong><span>{detail}</span></div>'
