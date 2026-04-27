import streamlit as st
import pandas as pd
import plotly.express as px
from io import StringIO
from datetime import datetime, timedelta

# --- CONFIG ---
st.set_page_config(page_title="Hybrid Pro Coach AI", layout="wide")

# --- INITIALISATIE ---
if 'logs' not in st.session_state:
    st.session_state.logs = pd.DataFrame(columns=['Datum', 'Type', 'KM', 'Duur', 'HR', 'RunningIndex', 'Pijn', 'Gewicht'])

# --- SIDEBAR ---
st.sidebar.header("🛡️ Coach Settings")
curr_weight = st.sidebar.number_input("Gewicht (kg)", value=76.0)
target_ri = 65 # Target voor Sub-18 5K

# --- CALCULATIE FUNCTIES ---
def calculate_race_times(ri):
    # Formules gebaseerd op Daniels/Polar data mapping
    if ri == 0: return None
    vdot = ri # RI is een goede proxy voor VDOT
    times = {
        "5K": 480 / (ri * 0.08), # Simpele lineaire benadering
        "10K": 1000 / (ri * 0.08),
        "Marathon": 4500 / (ri * 0.08)
    }
    # Verfijning (RI 57 ~ 19:15, RI 65 ~ 17:30)
    five_k_mins = 26 - (0.12 * ri * 1.5) # Empirische curve
    return {
        "5K": str(timedelta(minutes=26 - (ri-50)*0.45))[:7],
        "10K": str(timedelta(minutes=54 - (ri-50)*0.95))[:7],
        "Marathon": str(timedelta(minutes=220 - (ri-50)*4.2))[:7]
    }

def get_training_paces(ri):
    # Zone 2 tempo: ~70-75% van 5k tempo
    # Threshold tempo: ~88-92% van 5k tempo
    base_pace_sec = (26 - (ri-50)*0.45) * 60 / 5
    z2_pace = base_pace_sec * 1.35
    threshold_pace = base_pace_sec * 1.08
    return {
        "Zone 2 (Easy)": f"{int(z2_pace//60)}:{int(z2_pace%60):02d} min/km",
        "Threshold": f"{int(threshold_pace//60)}:{int(threshold_pace%60):02d} min/km"
    }

# --- PARSER ---
def parse_polar(file):
    stringio = StringIO(file.getvalue().decode("utf-8"))
    df_raw = pd.read_csv(stringio, skiprows=0)
    ri = df_raw.iloc[0]['Running index']
    return {
        'Datum': df_raw.iloc[0]['Date'],
        'Type': df_raw.iloc[0]['Sport'],
        'KM': round(float(df_raw.iloc[0]['Total distance (km)']), 2),
        'Duur': df_raw.iloc[0]['Duration'],
        'HR': int(df_raw.iloc[0]['Average heart rate (bpm)']),
        'RunningIndex': int(ri) if pd.notnull(ri) else 0,
        'Pijn': 0, 'Gewicht': curr_weight
    }

# --- UI ---
st.title("🚀 Wladimir's AI Hybrid Coach")

tabs = st.tabs(["🎯 Voorspellingen", "📈 Progressie", "📅 Plan", "💪 Kracht", "📂 Data"])

# Bereken gemiddelde RI van de laatste 5 runs
runs = st.session_state.logs[st.session_state.logs['Type'] == 'RUNNING']
current_ri = runs['RunningIndex'].tail(5).mean() if not runs.empty else 57.0

with tabs[0]:
    st.header("🏁 Race Voorspellingen & Tempo's")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Jouw Huidige Potentie")
        st.write(f"Gebaseerd op Running Index: **{current_ri:.1f}**")
        preds = calculate_race_times(current_ri)
        st.metric("5K Race (Nu)", preds["5K"])
        st.metric("10K Race (Nu)", preds["10K"])
        st.metric("Marathon (Nu)", preds["Marathon"])

    with col2:
        st.subheader("Target: Sub-18 min 5K")
        ri_gap = target_ri - current_ri
        weeks_needed = int(ri_gap / 0.3) # Gemiddelde RI winst van 0.3 per week
        st.metric("Weken tot Sub-18", f"± {weeks_needed} weken")
        
        st.write("**Jouw Trainingstempo's:**")
        paces = get_training_paces(current_ri)
        for zone, pace in paces.items():
            st.info(f"**{zone}:** {pace}")

with tabs[1]:
    st.header("Analyse & Trends")
    if not runs.empty:
        fig = px.line(runs, x='Datum', y='RunningIndex', title='Conditie Groei (Running Index)')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("Upload runs om progressie te zien.")

with tabs[2]:
    st.header("Lydiard 24-Weken Roadmap")
    st.write(f"Huidige Status: **Week {24-weeks_needed if weeks_needed < 24 else 1}**")
    
    phase = "Aerobe Basis" if weeks_needed > 12 else "Heuvel Fase"
    st.success(f"Huidige Fase: **{phase}**")
    
    st.table(pd.DataFrame({
        "Fase": ["Aerobe Basis", "Heuvel Kracht", "Anaerobe Fase", "Taper"],
        "Duur": ["12-16 weken", "4 weken", "4 weken", "2 weken"],
        "Focus": ["Volume & Hart", "Pezen & Kracht", "Snelheid", "Frisheid"]
    }))

with tabs[3]:
    st.header("Hyrox & Home Gym")
    st.write("Jouw uitrusting is ideaal voor 'Concurrent Training'.")
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Sessie A")
        st.write("1. Single Leg RDL (20kg)")
        st.write("2. Goblet Squat (20kg)")
        st.write("3. Isometric Calf Raise (3x45s)")
    with col_b:
        st.subheader("Mobiliteit")
        st.write("Focus op Dorsiflexie (Board)")
        st.write("Hip Hinge flow")

with tabs[4]:
    uploaded = st.file_uploader("Upload Polar CSV", type="csv")
    if uploaded:
        data = parse_polar(uploaded)
        if st.button("Opslaan"):
            st.session_state.logs = pd.concat([st.session_state.logs, pd.DataFrame([data])], ignore_index=True)
            st.success("Data verwerkt!")
    st.dataframe(st.session_state.logs)
