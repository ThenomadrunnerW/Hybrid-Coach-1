import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from io import StringIO
from datetime import datetime, timedelta
import numpy as np

# --- CONFIG ---
st.set_page_config(page_title="Wladimir Hybrid Pro", layout="wide", page_icon="⚡")

# --- CUSTOM CSS VOOR EEN PREMIUM LOOK ---
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 25px;
        border-radius: 10px;
        font-weight: bold;
        background-color: #1e1e1e;
    }
    .hero-text {
        text-align: center;
        padding: 20px;
        background: linear-gradient(90deg, #FF4B4B 0%, #FF8F8F 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 45px;
        font-weight: 800;
    }
    .mission-sub {
        text-align: center;
        color: #808495;
        font-size: 18px;
        margin-bottom: 30px;
    }
</style>
""", unsafe_allow_html=True)

# --- INITIALISATIE (Zelfde als voorheen) ---
if 'logs' not in st.session_state:
    st.session_state.logs = pd.DataFrame(columns=['Datum', 'Type', 'KM', 'Duur', 'HR', 'RunningIndex', 'Pijn', 'Gewicht'])

# --- SIDEBAR (Zelfde als voorheen) ---
st.sidebar.header("🛡️ Dashboard Control")
weight = st.sidebar.number_input("Gewicht (kg)", value=76.0)
injury_score = st.sidebar.slider("Achilles Gevoeligheid", 0, 10, 0)
target_date = datetime(2024, 12, 31)
days_to_go = (target_date - datetime.now()).days

# --- INTRO SECTIE (DE NIEUWE INTRO) ---
st.markdown("<div class='hero-text'>HYBRID PERFORMANCE PORTAL</div>", unsafe_allow_html=True)
st.markdown("<div class='mission-sub'>Optimizing the engine for Sub-18 5K & Sub-3 Marathon | Built for Strength</div>", unsafe_allow_html=True)

intro_col1, intro_col2, intro_col3 = st.columns(3)

with intro_col1:
    st.markdown("""
    <div style='text-align: center; border: 1px solid #4a4a4a; padding: 20px; border-radius: 15px;'>
        <h3>🫁 The Engine</h3>
        <p>Lydiard Aerobic Base<br>Target: RI 65.0</p>
    </div>
    """, unsafe_allow_html=True)

with intro_col2:
    st.markdown("""
    <div style='text-align: center; border: 1px solid #4a4a4a; padding: 20px; border-radius: 15px;'>
        <h3>⚙️ The Machine</h3>
        <p>A-B-C-D Strength<br>Target: 73.0 kg</p>
    </div>
    """, unsafe_allow_html=True)

with intro_col3:
    st.markdown(f"""
    <div style='text-align: center; border: 1px solid #4a4a4a; padding: 20px; border-radius: 15px;'>
        <h3>🏁 The Goal</h3>
        <p>31 December Test<br>{days_to_go} Dagen te gaan</p>
    </div>
    """, unsafe_allow_html=True)

st.write("") # Spacer
st.divider()

# --- Vanaf hier de rest van je code (Tabs etc.) ---
# [Houd de tabs en berekeningen die je al had hieronder aan...]
