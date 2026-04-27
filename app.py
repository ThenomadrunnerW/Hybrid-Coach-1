import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from io import StringIO
from datetime import datetime, timedelta
import numpy as np
import random

# --- CONFIG ---
st.set_page_config(page_title="Wladimir Hybrid Pro V12", layout="wide", page_icon="⚡")

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .hero-text {
        text-align: center;
        background: linear-gradient(90deg, #FF4B4B 0%, #FF8F8F 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 45px;
        font-weight: 800;
        margin-bottom: 0px;
    }
    .quote-box {
        background-color: rgba(255, 255, 255, 0.05);
        padding: 25px;
        border-radius: 15px;
        border: 1px solid #4a4a4a;
        font-style: italic;
        text-align: center;
        margin: 20px 0;
    }
    .coach-note {
        background-color: rgba(0, 192, 242, 0.1);
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #00C0F2;
    }
</style>
""", unsafe_allow_html=True)

# --- INITIALISATIE ---
if 'logs' not in st.session_state:
    st.session_state.logs = pd.DataFrame(columns=['Datum', 'Type', 'KM', 'Duur', 'HR', 'RunningIndex', 'Pijn', 'Gewicht'])

# --- SIDEBAR & DATA INPUT ---
st.sidebar.header("🛡️ Dashboard Control")
weight = st.sidebar.number_input("Huidig Gewicht (kg)", value=76.0)
injury_score = st.sidebar.slider("Achilles Gevoeligheid (0-10)", 0, 10, 0)
target_date = datetime(2024, 12, 31)
days_to_go = (target_date - datetime.now()).days

# Backup functie
if not st.session_state.logs.empty:
    csv = st.session_state.logs.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button("💾 Download Backup", data=csv, file_name="hybrid_coach_data.csv")

# --- MOTIVATIE ENGINE ---
quotes = [
    {"text": "Stay hard! Don't let your mind tell you that you're done.", "author": "David Goggins"},
    {"text": "Nobody cares, work harder. Keep hammering.", "author": "Cameron Hanes"},
    {"text": "The comfort zone is a beautiful place, but nothing ever grows there.", "author": "Joe Rogan"},
    {"text": "When you want to succeed as bad as you want to breathe, then you'll be successful.", "author": "Eric Thomas"},
    {"text": "Be the person that shows up regardless of how you feel.", "author": "Cameron Hanes"},
    {"text": "You are in danger of living a life so comfortable and soft, that you will die without ever realizing your true potential.", "author": "David Goggins"}
]
selected_quote = random.choice(quotes)

# --- APP HEADER ---
st.markdown("<div class='hero-text'>HYBRID PERFORMANCE PORTAL</div>", unsafe_allow_html=True)
st.markdown(f"<div class='quote-box'>\"{selected_quote['text']}\" <br><b>- {selected_quote['author']}</b></div>", unsafe_allow_html=True)

# --- COACH NOTE LOGICA ---
with st.container():
    st.markdown("<div class='coach-note'>", unsafe_allow_html=True)
    st.subheader("📋 Coach's Note")
    if injury_score > 2:
        st.write("⚠️ **HERSTEL FOCUS:** De achilles vraagt aandacht. Geen explosieve sprints. Focus op de 9:1 ratio en 15 min mobility board vandaag.")
    elif weight > 73:
        st.write(f"⚖️ **GEWICHTSBEHEERSING:** Je zit op {weight}kg. Focus op eiwitrijke voeding (150g+) en timing van koolhydraten rondom je runs. 73kg is het doel voor die Sub-18.")
    else:
        st.write("🚀 **ALL SYSTEMS GO:** Pezen zijn stabiel en gewicht is on point. Tijd om die aerobe motor van Lydiard uit te bouwen.")
    st.markdown("</div>", unsafe_allow_html=True)

st.write("") 

# --- CALCULATIES ---
runs = st.session_state.logs[st.session_state.logs['Type'] == 'RUNNING']
current_ri = runs['RunningIndex'].tail(5).mean() if not runs.empty else 57.0
z2_pace_min_km = 8.5 - (current_ri - 40) * 0.15 
z2_pace_seconds = z2_pace_min_km * 60

# --- TABS ---
tabs = st.tabs(["🚀 Daily Coach", "🔮 Planner", "💪 Kracht (A-D)", "📊 Analytics", "📂 Data"])

with tabs[0]:
    c1, c2, c3 = st.columns(3)
    c1.metric("Target RI", "65.0", f"Nu: {current_ri:.1f}")
    c2.metric("Target Gewicht", "73.0 kg", f"{weight-73:.1f} te gaan")
    c3.metric("Countdown 5K", f"{days_to_go} Dagen")

    st.divider()
    st.subheader("Training Vandaag")
    st.info(f"**Lydiard Zone 2 Run** | HR: 125-140 bpm | Ratio: 10:1 | Geschat tempo: {int(z2_pace_min_km)}:{(int((z2_pace_min_km%1)*60)):02d}/km")

with tabs[1]:
    st.header("🔮 De Architect: 4-Weken Planning")
    base_v = 24.0
    strength_cycle = ["Sessie A", "Sessie B", "Sessie C", "Sessie D"]
    for w in range(1, 5):
        is_del = (w == 4)
        vol = base_v * (1.1 ** (w-1)) if not is_del else base_v * 1.1**2 * 0.7
        s1, s2 = strength_cycle[(w*2-2) % 4], strength_cycle[(w*2-1) % 4]
        with st.expander(f"Week {w}: {'🚀 Build' if not is_del else '📉 Deload'} ({vol:.1f} km)"):
            plan_df = pd.DataFrame({
                "Dag": ["Ma", "Di", "Wo", "Do", "Vr", "Za", "Zo"],
                "Sessie": ["🚲 Fiets Z1", "🏃 Run Z2", f"💪 {s1}", "🏃 Run Z2", "🚲 Fiets Z1", "🏃 Lange Loop", f"💪 {s2}"],
                "Volume": ["45m", f"{vol*0.25:.1f}km", "Stability", f"{vol*0.25:.1f}km", "45m", f"{vol*0.5:.1f}km", "Power"]
            })
            st.table(plan_df)

with tabs[2]:
    st.header("💪 Home Gym Roulatie")
    colA, colB = st.columns(2)
    with colA:
        st.subheader("🦵 Sessie A: Legs & Stability")
        st.write("- SL RDL (20kg): 3x12 | Iso Calf Raise: 5x45s | Good Mornings: 3x12 | Tibialis Raise: 3x20 | Glute Bridge: 3x20 | Copenhagen Plank: 3x30s")
        st.subheader("👕 Sessie B: Upper Power")
        st.write("- Pull-ups: 4xMax | Dips: 4xMax | Barbell Row: 4x10 | Overhead Press: 3x12 | Diamond Pushups: 3xMax | Face Pulls: 3x20")
    with colB:
        st.subheader("🦵 Sessie C: Legs & Force")
        st.write("- Goblet Squat: 4x12 | Bulgarian Split Squat: 3x10 | KB Swings: 4x20 | Walking Lunges: 3x20 | Explosive Calf: 3x15 | Wall Sit: 3x60s")
        st.subheader("⚖️ Sessie D: Core & Mobility")
        st.write("- Ab-Roller: 4x12 | Russian Twists: 3x40 | Deadbugs: 3x15 | Leg Raises: 3x12 | Plank Taps: 3x60s | Board Stretch: 10 min")

with tabs[3]:
    st.header("📈 Performance Analyse")
    if not st.session_state.logs.empty:
        df = st.session_state.logs.copy()
        df['Datum'] = pd.to_datetime(df['Datum'])
        df = df.sort_values('Datum')
        fig = px.line(df[df['Type']=='RUNNING'], x='Datum', y='RunningIndex', title="VO2max Ontwikkeling", markers=True)
        st.plotly_chart(fig, use_container_width=True)
        
        # PMC Grafiek (Snel overzicht)
        st.write("**Fitness vs Fatigue** (Blauw = Conditie, Rood = Moeheid)")
        # [Korte versie voor performance]
        st.info("Blijf data uploaden om je Fitness-curve te zien groeien.")
    else:
        st.warning("Upload data om grafieken te zien.")

with tabs[4]:
    st.header("📂 Data Import")
    uploaded = st.file_uploader("Polar CSV", type="csv")
    if uploaded:
        try:
            stringio = StringIO(uploaded.getvalue().decode("utf-8"))
            df_raw = pd.read_csv(stringio)
            ri = df_raw.iloc[0]['Running index']
            new_data = {'Datum': df_raw.iloc[0]['Date'], 'Type': df_raw.iloc[0]['Sport'], 'KM': round(float(df_raw.iloc[0]['Total distance (km)']), 2), 'Duur': df_raw.iloc[0]['Duration'], 'HR': int(df_raw.iloc[0]['Average heart rate (bpm)']), 'RunningIndex': int(ri) if pd.notnull(ri) else 0, 'Pijn': injury_score, 'Gewicht': weight}
            if st.button("Sessie Opslaan"):
                st.session_state.logs = pd.concat([st.session_state.logs, pd.DataFrame([new_data])], ignore_index=True)
                st.success("Sessie opgeslagen!")
        except: st.error("Fout in bestand.")
    
    st.subheader("History")
    st.dataframe(st.session_state.logs.sort_values('Datum', ascending=False), use_container_width=True)
