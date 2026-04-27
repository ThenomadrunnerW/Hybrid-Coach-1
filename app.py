import streamlit as st
import pandas as pd
import plotly.express as px
from io import StringIO
from datetime import datetime, timedelta

# --- CONFIG ---
st.set_page_config(page_title="Hybrid Pro Coach V7", layout="wide")

# --- CUSTOM CSS VOOR DARK MODE ---
st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { border-radius: 4px; padding: 10px; }
    .coach-box { padding: 20px; border-radius: 10px; border-left: 5px solid #FF4B4B; background-color: rgba(255, 75, 75, 0.1); margin-bottom: 20px; }
    .info-box { padding: 20px; border-radius: 10px; border-left: 5px solid #00C0F2; background-color: rgba(0, 192, 242, 0.1); margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# --- INITIALISATIE ---
if 'logs' not in st.session_state:
    st.session_state.logs = pd.DataFrame(columns=['Datum', 'Type', 'KM', 'Duur', 'HR', 'RunningIndex', 'Pijn', 'Gewicht', 'Ratio'])

# --- SIDEBAR ---
st.sidebar.header("🛡️ Status")
curr_weight = st.sidebar.number_input("Gewicht (kg)", value=76.0)
injury_score = st.sidebar.slider("Achilles Pijn (0-10)", 0, 10, 0)
st.sidebar.divider()
st.sidebar.write("**Z2 Range:** 125 - 140 bpm")

# --- LOGICA: KM & RATIO PROGRESSIE ---
today = datetime.now()
last_week_date = today - timedelta(days=7)

if not st.session_state.logs.empty:
    st.session_state.logs['Datum'] = pd.to_datetime(st.session_state.logs['Datum'])
    last_week_runs = st.session_state.logs[(st.session_state.logs['Datum'] > last_week_date) & (st.session_state.logs['Type'] == 'RUNNING')]
    last_week_vol = last_week_runs['KM'].sum() if not last_week_runs.empty else 22.0
else:
    last_week_vol = 22.0

week_limit = round(last_week_vol * 1.1, 1)
current_ratio = "10:1" if injury_score <= 1 else "9:1"

# --- TABS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🚀 Coach", "📅 Roadmap", "💪 Kracht (A-D)", "📈 Progressie", "📂 Data"])

with tab1:
    st.header(f"Plan voor {today.strftime('%d %B')}")
    st.markdown(f"""
    <div class="coach-box">
        <h3>🚀 Bouw Week: Aerobe Flow</h3>
        <p><b>Hardloop Protocol:</b> <span style='color:#FF4B4B; font-weight:bold;'>{current_ratio}</span> (Focus op relaxte ademhaling)</p>
        <p><b>Weeklimiet:</b> {week_limit} km | <b>Dagdoel:</b> ± {round(week_limit/3, 1)} km</p>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Diesel Status: Bevestigd")
        st.write("Jouw RI stijgt bij langere sessies. Dit betekent dat je efficiënter wordt naarmate de run vordert. Focus op een hele rustige eerste 2km.")
    with c2:
        st.subheader("Mobiliteit van de dag")
        st.info("Tibialis Raises: 3 x 20 herhalingen (tegen een muur staan, tenen optrekken). Dit ontlast je achillespees direct.")

with tab2:
    st.header("📅 Roadmap naar 31 December")
    st.write("Fase 1: Aerobe Fundering (Continuïteit bouwen)")
    roadmap = pd.DataFrame({
        "Periode": ["Nu - Mei", "Juni - Juli", "Aug - Sept", "Okt - Nov", "December"],
        "Focus": ["Ratio naar 20:1", "Continu lopen", "Lydiard Heuvels", "Anaerobe Snelheid", "Taper & PR"],
        "KM per week": ["22 - 30 km", "30 - 45 km", "40 - 50 km", "45 - 55 km", "Race Prep"]
    })
    st.table(roadmap)

with tab3:
    st.header("💪 Expanded Strength Rotation")
    st.info("Voer de oefeningen beheerst uit. Bij kracht: focus op de spier, niet op het gooien van gewicht.")
    
    col_a, col_b = st.columns(2)
    with col_a:
        with st.expander("🦵 Sessie A: Legs (Posterior Chain & Enkel Control)"):
            st.write("1. **Single Leg RDL:** 3 x 12 (KB)")
            st.write("2. **Barbell Good Mornings:** 3 x 12 (Licht/40kg)")
            st.write("3. **Isometric Calf Raise:** 5 x 45s (Houd vast op board)")
            st.write("4. **Tibialis Raises:** 3 x 20 (Lichaamsgewicht)")
            st.write("5. **Glute Bridges:** 3 x 20 (Eventueel met gewicht op heupen)")
            st.write("6. **Copenhagen Plank:** 3 x 30s per kant (Lies-sterkte)")

        with st.expander("👕 Sessie B: Upper Body (Hyrox Power & Push/Pull)"):
            st.write("1. **Weighted Pull-ups:** 4 x Max")
            st.write("2. **Dips:** 4 x Max")
            st.write("3. **Barbell Row:** 4 x 10 (40kg)")
            st.write("4. **Overhead Press:** 3 x 12 (Barbell)")
            st.write("5. **Diamond Push-ups:** 3 x Max (Parallettes)")
            st.write("6. **Band Face Pulls:** 3 x 20 (Houding/Schouders)")

    with col_b:
        with st.expander("🦵 Sessie C: Legs (Quad Dominant & Explosief)"):
            st.write("1. **Goblet Squat:** 4 x 12 (20kg KB)")
            st.write("2. **Bulgarian Split Squat:** 3 x 10 per been (Focus op diepte)")
            st.write("3. **KB Swings:** 4 x 20 (Explosieve heupinzet)")
            st.write("4. **Walking Lunges:** 3 x 20 stappen (DBs in handen)")
            st.write("5. **Explosive Calf Raises:** 3 x 15 (Snel omhoog, 3 sec omlaag)")
            st.write("6. **Wall Sit:** 3 x 60 seconden")

        with st.expander("⚖️ Sessie D: Core & Hybrid Stability"):
            st.write("1. **Ab-Roller:** 4 x 12")
            st.write("2. **Russian Twists:** 3 x 40 (KB)")
            st.write("3. **Deadbugs:** 3 x 15 (Langzaam en gecontroleerd)")
            st.write("4. **Hanging Leg Raises:** 3 x 12 (Aan de optrekstang)")
            st.write("5. **Plank with Shoulder Taps:** 3 x 60s")
            st.write("6. **Mobility Board Enkel Stretch:** 10 min actieve stretch")

with tab4:
    st.header("📈 Voortgang")
    runs = st.session_state.logs[st.session_state.logs['Type'] == 'RUNNING']
    if not runs.empty:
        curr_ri = runs['RunningIndex'].tail(5).mean()
        pred_5k = 26 - (curr_ri - 50) * 0.5
        m1, m2, m3 = st.columns(3)
        m1.metric("5K Voorspelling", f"{int(pred_5k)}:{(pred_5k%1*60):02.0f} min")
        m2.metric("Running Index", f"{curr_ri:.1f}")
        m3.metric("Status", "Productief" if curr_ri > 55 else "Opbouwend")
        st.plotly_chart(px.line(runs, x='Datum', y='RunningIndex', title="Running Index Trend", markers=True), use_container_width=True)
    else:
        st.info("Upload data om grafieken te zien.")

with tab5:
    st.header("📂 Data")
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
                'Pijn': injury_score, 'Gewicht': curr_weight, 'Ratio': current_ratio
            }
            if st.button("Sessie Opslaan"):
                st.session_state.logs = pd.concat([st.session_state.logs, pd.DataFrame([new_data])], ignore_index=True)
                st.success("Sessie opgeslagen!")
        except: st.error("Fout bij inlezen.")
    st.dataframe(st.session_state.logs.sort_values('Datum', ascending=False), use_container_width=True)
