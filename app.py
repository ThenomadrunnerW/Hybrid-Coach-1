import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from io import StringIO
from datetime import datetime, timedelta
import numpy as np

# --- CONFIG ---
st.set_page_config(page_title="Hybrid Coach Pro V9", layout="wide")

# --- INITIALISATIE ---
if 'logs' not in st.session_state:
    st.session_state.logs = pd.DataFrame(columns=['Datum', 'Type', 'KM', 'Duur', 'HR', 'RunningIndex', 'Pijn', 'Gewicht', 'Load'])

# --- SIDEBAR & ZONES ---
st.sidebar.header("🛡️ Wladimir Performance Dashboard")
weight = st.sidebar.number_input("Gewicht (kg)", value=76.0)
injury_score = st.sidebar.slider("Achilles Pijn (0-10)", 0, 10, 0)

z_info = {
    "Z1 (Herstel)": "90 - 124 bpm",
    "Z2 (Basis)": "125 - 140 bpm",
    "Z3 (Tempo)": "141 - 155 bpm",
    "Z4 (Threshold)": "156 - 175 bpm",
    "Z5 (Max)": "176 - 199 bpm"
}

# --- CALCULATIE: TRAINING LOAD ---
def calculate_load(row):
    # Simpele load score: KM * (AvgHR / MaxHR) of Duration voor fietsen
    max_hr = 199
    if row['Type'] == 'RUNNING':
        return row['KM'] * (row['HR'] / max_hr) * 10
    else: # Fietsen of Kracht
        # Probeer duur om te zetten naar minuten
        try:
            h, m, s = map(int, row['Duur'].split(':'))
            mins = h * 60 + m
            return mins * (row['HR'] / max_hr) * 0.5
        except:
            return 20 # Default voor kracht

# --- TABS ---
tabs = st.tabs(["🚀 Daily Coach", "🔮 Toekomst Planner", "📈 Fitness vs Fatigue", "💪 Kracht Info", "📂 Data"])

# Berekening voor AI Stats
runs = st.session_state.logs[st.session_state.logs['Type'] == 'RUNNING']
current_ri = runs['RunningIndex'].tail(5).mean() if not runs.empty else 57.0
pred_5k = 26 - (current_ri - 50) * 0.5

with tabs[0]:
    st.header(f"Focus: {datetime.now().strftime('%d %B')}")
    c1, c2, c3 = st.columns(3)
    c1.metric("Sub-18 5K Potentie", f"{int(pred_5k)}:{(pred_5k%1*60):02.0f} min")
    c2.metric("Running Index", f"{current_ri:.1f}")
    c3.metric("Doel Gewicht", "73.0 kg")

    st.markdown(f"""
    <div style="background-color:rgba(255, 75, 75, 0.1); padding:20px; border-radius:10px; border-left: 5px solid #FF4B4B;">
        <h3>🏃‍♂️ Vandaag: Lydiard Z2 Run (10:1)</h3>
        <p><b>Zones:</b> 125 - 140 bpm | <b>Mobiliteit:</b> 10 min Achilles/Enkel focus</p>
    </div>
    """, unsafe_allow_html=True)

with tabs[1]:
    st.header("📅 De Architect: 4-Weken Schema")
    base_v = 24.0
    strength_cycle = ["Sessie A", "Sessie B", "Sessie C", "Sessie D"]
    
    for w in range(1, 5):
        is_del = (w == 4)
        vol = base_v * (1.1 ** (w-1)) if not is_del else base_v * 1.1**2 * 0.7
        
        with st.expander(f"Week {w}: {'🚀 Bouwen' if not is_del else '📉 Deload'} ({vol:.1f} km)"):
            # Bepaal kracht sessies voor deze week (roulatie)
            s1 = strength_cycle[(w*2-2) % 4]
            s2 = strength_cycle[(w*2-1) % 4]
            
            plan_df = pd.DataFrame({
                "Dag": ["Maandag", "Dinsdag", "Woensdag", "Donderdag", "Vrijdag", "Zaterdag", "Zondag"],
                "Focus": ["🚲 Fiets Z1", "🏃 Run Z2", f"💪 {s1}", "🏃 Run Z2", "🚲 Fiets Z1", "🏃 Lange Loop", f"💪 {s2}"],
                "Uitleg": [
                    "Actief herstel, vetverbranding.",
                    "Bouwen van capillaire dichtheid.",
                    "Zie Kracht Tab voor details.",
                    "9:1 of 10:1 ratio toepassen.",
                    "Woon-werk rit 125-135 bpm.",
                    "Lydiard's belangrijkste wekelijkse prikkel.",
                    "Core & herstel kracht."
                ],
                "HR Zone": ["Z1", "Z2", "Power", "Z2", "Z1", "Z2", "Stability"]
            })
            st.table(plan_df)

with tabs[2]:
    st.header("📈 Performance Management Chart")
    if not st.session_state.logs.empty:
        df = st.session_state.logs.copy()
        df['Datum'] = pd.to_datetime(df['Datum'])
        df = df.sort_values('Datum')
        
        # Bereken Load als dat nog niet gedaan is
        df['Load'] = df.apply(calculate_load, axis=1)
        
        # PMC Berekening (Exponential Moving Averages)
        df = df.set_index('Datum').resample('D').sum().fillna(0)
        df['Fitness (CTL)'] = df['Load'].ewm(span=42).mean()
        df['Fatigue (ATL)'] = df['Load'].ewm(span=7).mean()
        df['Form (TSB)'] = df['Fitness (CTL)'] - df['Fatigue (ATL)']
        
        fig_pmc = go.Figure()
        fig_pmc.add_trace(go.Scatter(x=df.index, y=df['Fitness (CTL)'], name='Fitness (Conditie)', line=dict(color='blue', width=3)))
        fig_pmc.add_trace(go.Scatter(x=df.index, y=df['Fatigue (ATL)'], name='Fatigue (Vermoeidheid)', line=dict(color='red', width=1, dash='dot')))
        fig_pmc.add_trace(go.Bar(x=df.index, y=df['Form (TSB)'], name='Form (Frisheid)', marker_color='orange', opacity=0.3))
        
        fig_pmc.update_layout(title="Fitness vs Fatigue Trend", xaxis_title="Datum", yaxis_title="Stress Score")
        st.plotly_chart(fig_pmc, use_container_width=True)
        
        st.info("**Hoe te lezen?** Blauwe lijn omhoog = conditie groeit. Gele balken te laag (onder -30)? = Neem rust. Gele balken positief? = Tijd voor een PR poging!")
    else:
        st.warning("Upload meer data om je fitness-trends te zien.")

with tabs[3]:
    st.header("💪 Kracht Roulatie Details")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Sessie A: Legs & Stability")
        st.write("- SL RDL (20kg), Iso Calf Raise (Board), Good Mornings, Tibialis Raise, Glute Bridge, Copenhagen Plank")
        st.subheader("Sessie B: Upper Body Power")
        st.write("- Weighted Pullups, Dips, Barbell Row, Overhead Press, Diamond Pushups, Face Pulls")
    with c2:
        st.subheader("Sessie C: Legs & Force")
        st.write("- Goblet Squat (20kg), Bulgarian Split Squat, KB Swings, Walking Lunges, Explosive Calf Raise, Wall Sit")
        st.subheader("Sessie D: Core & Mobility")
        st.write("- Ab-Roller, Russian Twists, Deadbugs, Leg Raises, Plank Taps, Mobility Board Stretch")

with tabs[4]:
    st.header("📂 Data Import")
    uploaded = st.file_uploader("Upload Polar Flow CSV", type="csv")
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
            if st.button("Opslaan"):
                st.session_state.logs = pd.concat([st.session_state.logs, pd.DataFrame([new_data])], ignore_index=True)
                st.success("Sessie verwerkt!")
        except: st.error("Fout in bestand.")
    st.dataframe(st.session_state.logs.sort_values('Datum', ascending=False), use_container_width=True)
