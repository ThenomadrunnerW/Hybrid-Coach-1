import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from io import StringIO
from datetime import datetime, timedelta
import numpy as np

# --- CONFIG ---
st.set_page_config(page_title="Hybrid Coach Pro V11", layout="wide")

# --- INITIALISATIE ---
if 'logs' not in st.session_state:
    st.session_state.logs = pd.DataFrame(columns=['Datum', 'Type', 'KM', 'Duur', 'HR', 'RunningIndex', 'Pijn', 'Gewicht'])

# --- SIDEBAR ---
st.sidebar.header("🛡️ Coach & Backup")
weight = st.sidebar.number_input("Gewicht (kg)", value=76.0)
injury_score = st.sidebar.slider("Achilles Pijn", 0, 10, 0)

if not st.session_state.logs.empty:
    csv = st.session_state.logs.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button("💾 Download Backup CSV", data=csv, file_name="wladimir_coach_backup.csv", mime="text/csv")

# --- CALCULATIE: TEMPO & DUUR ---
runs = st.session_state.logs[st.session_state.logs['Type'] == 'RUNNING']
current_ri = runs['RunningIndex'].tail(5).mean() if not runs.empty else 57.0

# Bereken Zone 2 tempo (sec per km)
z2_pace_min_km = 8.5 - (current_ri - 40) * 0.15 
z2_pace_seconds = z2_pace_min_km * 60

def get_duration_str(km, pace_sec):
    total_seconds = km * pace_sec
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    if hours > 0: return f"{hours}u {minutes}m"
    return f"{minutes} min"

def calculate_load(row):
    max_hr = 199
    if row['Type'] == 'RUNNING':
        return float(row['KM']) * (float(row['HR']) / max_hr) * 10
    else:
        return 25.0 # Flat load voor kracht/fietsen als duur onbekend is

# --- TABS ---
tabs = st.tabs(["🚀 Coach", "🔮 Toekomst Planner", "💪 Kracht Info", "📈 Fitness & Voortgang", "📂 Data"])

with tabs[0]:
    st.header(f"Focus: {datetime.now().strftime('%d %B')}")
    st.write(f"Huidig geschat Z2 tempo: **{int(z2_pace_min_km)}:{(int((z2_pace_min_km%1)*60)):02d} /km**")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""<div style="border-left: 5px solid #FF4B4B; background-color:rgba(255, 75, 75, 0.1); padding:20px; border-radius:10px;">
        <h3>🏃‍♂️ Vandaag: Lydiard Z2</h3>
        <p><b>HR Range:</b> 125 - 140 bpm</p>
        <p><b>Protocol:</b> 10:1 (Lopen:Wandelen)</p>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.info(f"**Sub-18 Doel:** Running Index moet naar 65 (Nu: {current_ri:.1f}). Focus op vetverbranding en pees-sterkte.")

with tabs[1]:
    st.header("📅 De Architect: 4-Weken Planner")
    base_v = 24.0
    strength_cycle = ["Sessie A", "Sessie B", "Sessie C", "Sessie D"]
    
    for w in range(1, 5):
        is_del = (w == 4)
        vol = base_v * (1.1 ** (w-1)) if not is_del else base_v * 1.1**2 * 0.7
        s1 = strength_cycle[(w*2-2) % 4]
        s2 = strength_cycle[(w*2-1) % 4]
        
        with st.expander(f"Week {w}: {'🚀 Bouw' if not is_del else '📉 Deload'} - Totaal {vol:.1f} km"):
            days = ["Ma", "Di", "Wo", "Do", "Vr", "Za", "Zo"]
            workouts = ["Fiets Z1", "Run Z2", s1, "Run Z2", "Fiets Z1", "Lange Loop", s2]
            kms = [0, vol*0.25, 0, vol*0.25, 0, vol*0.5, 0]
            
            durations = []
            for i, workout in enumerate(workouts):
                if "Run" in workout or "Lange Loop" in workout:
                    durations.append(get_duration_str(kms[i], z2_pace_seconds))
                elif "Fiets" in workout: durations.append("45 min")
                else: durations.append("60 min")

            st.table(pd.DataFrame({
                "Dag": days, "Sessie": workouts, "Volume": [f"{k:.1f} km" if k > 0 else "-" for k in kms],
                "Duur": durations, "Zone": ["Z1", "Z2", "Power", "Z2", "Z1", "Z2", "Stability"]
            }))

with tabs[2]:
    st.header("💪 Home Gym Roulatie (A-B-C-D)")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🦵 Sessie A: Legs & Stability")
        st.write("- **Single Leg RDL:** 3x12 (20kg KB)")
        st.write("- **Isometric Calf Raise:** 5x45s (Board)")
        st.write("- **Barbell Good Mornings:** 3x12 (40kg)")
        st.write("- **Tibialis Raises:** 3x20")
        st.write("- **Glute Bridge:** 3x20")
        st.write("- **Copenhagen Plank:** 3x30s")
        
        st.subheader("👕 Sessie B: Upper Power")
        st.write("- **Weighted Pull-ups:** 4xMax")
        st.write("- **Dips:** 4xMax")
        st.write("- **Barbell Row:** 4x10 (40kg)")
        st.write("- **Overhead Press:** 3x12 (Barbell)")
        st.write("- **Diamond Push-ups:** 3xMax")
        st.write("- **Face Pulls (Bands):** 3x20")

    with c2:
        st.subheader("🦵 Sessie C: Legs & Force")
        st.write("- **Goblet Squat:** 4x12 (20kg KB)")
        st.write("- **Bulgarian Split Squat:** 3x10 per been")
        st.write("- **KB Swings:** 4x20 (20kg)")
        st.write("- **Walking Lunges:** 3x20 stappen")
        st.write("- **Explosive Calf Raise:** 3x15")
        st.write("- **Wall Sit:** 3x60s")
        
        st.subheader("⚖️ Sessie D: Core & Mobility")
        st.write("- **Ab-Roller:** 4x12")
        st.write("- **Russian Twists:** 3x40 (KB)")
        st.write("- **Deadbugs:** 3x15 (Traag)")
        st.write("- **Hanging Leg Raises:** 3x12")
        st.write("- **Plank Taps:** 3x60s")
        st.write("- **Mobility Board Stretch:** 10 min")

with tabs[3]:
    st.header("📈 Performance Analyse")
    if not st.session_state.logs.empty:
        df = st.session_state.logs.copy()
        df['Datum'] = pd.to_datetime(df['Datum'])
        df = df.sort_values('Datum')
        df['Load'] = df.apply(calculate_load, axis=1)
        
        # PMC Grafiek
        pmc_df = df.set_index('Datum').resample('D').sum().fillna(0)
        pmc_df['Fitness'] = pmc_df['Load'].ewm(span=42).mean()
        pmc_df['Fatigue'] = pmc_df['Load'].ewm(span=7).mean()
        pmc_df['Form'] = pmc_df['Fitness'] - pmc_df['Fatigue']
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=pmc_df.index, y=pmc_df['Fitness'], name='Fitness', line=dict(color='blue', width=3)))
        fig.add_trace(go.Scatter(x=pmc_df.index, y=pmc_df['Fatigue'], name='Fatigue', line=dict(color='red', width=1, dash='dot')))
        fig.add_trace(go.Bar(x=pmc_df.index, y=pmc_df['Form'], name='Form', marker_color='orange', opacity=0.3))
        st.plotly_chart(fig, use_container_width=True)
        
        # RI Trend
        if not runs.empty:
            st.plotly_chart(px.line(runs, x='Datum', y='RunningIndex', title="Running Index Trend"), use_container_width=True)
    else:
        st.info("Upload data in de 'Data' tab om grafieken te zien.")

with tabs[4]:
    st.header("📂 Data Import")
    c1, c2 = st.columns(2)
    with c1:
        uploaded = st.file_uploader("Polar CSV", type="csv")
    with c2:
        backup = st.file_uploader("Backup herstellen", type="csv", key="restore")

    if uploaded:
        try:
            stringio = StringIO(uploaded.getvalue().decode("utf-8"))
            df_raw = pd.read_csv(stringio)
            ri = df_raw.iloc[0]['Running index']
            new_data = {
                'Datum': df_raw.iloc[0]['Date'], 'Type': df_raw.iloc[0]['Sport'],
                'KM': round(float(df_raw.iloc[0]['Total distance (km)']), 2),
                'Duur': df_raw.iloc[0]['Duration'], 'HR': int(df_raw.iloc[0]['Average heart rate (bpm)']),
                'RunningIndex': int(ri) if pd.notnull(ri) else 0,
                'Pijn': injury_score, 'Gewicht': weight
            }
            if st.button("Sessie Toevoegen"):
                st.session_state.logs = pd.concat([st.session_state.logs, pd.DataFrame([new_data])], ignore_index=True)
                st.success("Sessie opgeslagen!")
        except: st.error("Fout in bestand.")

    if backup:
        st.session_state.logs = pd.read_csv(backup)
        st.success("Data hersteld!")
    
    st.dataframe(st.session_state.logs.sort_values('Datum', ascending=False), use_container_width=True)
