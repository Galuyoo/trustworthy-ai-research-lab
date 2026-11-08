"""Session-state callbacks. Navigation never replaces an experiment's inputs."""
from datetime import time
import streamlit as st
from lab_models import PRESETS

JOURNEY = ["The system", "1 · Energy", "2 · Evidence"]
STAGES = ["Streetlight", "Sensors", "Telemetry", "Forecast", "Proposed plan"]


def set_energy(name="Comfortable"):
    p = PRESETS[name]
    st.session_state.update(energy=int(p.energy_wh), night=int(p.night_h),
                            minimum=int(p.minimum_pct), reserve=int(p.reserve_pct),
                            extra=True, night_progress=35)


def reset_evidence():
    st.session_state.update(observation=time(20, 0), cutoff=time(20, 10),
                            receipt=time(20, 20), reveal=False, later=False)


def start_over():
    set_energy()
    reset_evidence()
    st.session_state.update(journey=JOURNEY[0], stage=STAGES[0])


def go_to(index):
    st.session_state.journey = JOURNEY[index]


def receive_at_cutoff():
    st.session_state.receipt = st.session_state.cutoff


def initialise():
    if "energy" not in st.session_state:
        set_energy()
    if "observation" not in st.session_state:
        reset_evidence()
    for key, value in dict(journey=JOURNEY[0], stage=STAGES[0],
                           presentation=True, motion=True).items():
        st.session_state.setdefault(key, value)
