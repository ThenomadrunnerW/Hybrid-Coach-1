import streamlit as st
import pandas as pd
import plotly.express as px
from io import StringIO
from datetime import datetime, timedelta

# --- CONFIG ---
st.set_page_config(page_title="Hybrid Pro Coach V6", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .coach-box { padding: 20px; border-radius: 10px; border-left: 5px solid #FF4B4B; background-color: rgba(255, 75, 75, 0.1); margin-bottom: 20px; }
    .success-box { padding: 20px; border-radius: 10px; border-left: 5px solid #28a745; background-color: rgba(40, 167, 69, 0.1); margin-bottom: 20px; }
    .info-box { padding: 20px; border-radius: 10px; border-left: 5px solid #00C0F2; background-color: rgba(0, 192, 242, 0.1); margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# --- INITIALISATIE ---
if 'logs' not in st.session_state:
    st.session_state.logs = pd.DataFrame(columns=['Datum', 'Type', 'KM', 'Duur', 'HR', 'RunningIndex', 'Pijn', 'Gewicht', 'Ratio'])

# --- SIDEBAR ---
st.sidebar.header("🛡️ Status & Gezondheid")
curr_weight = st.sidebar.number_input("Gewicht (kg)", value=76.0)
injury_score = st.sidebar.slider("Achilles Pijn (0-10)", 0, 10, 0)
st.sidebar.info(f"Status: {'✅ Veilig voor progressie' if injury_score <= 2 else '⚠️ Pas op, ratio bevriezen'}")

st.sidebar.divider()
st.sidebar.header("💓 Jouw Zones")
st.sidebar.write("**Z1 (Herstel):** 90-124")
st.sidebar.write("**Z2 (Basis):** 125-140")
st.sidebar.write("**Z3 (Tempo):** 141-155")
st.sidebar.write("**Z4 (Threshold):** 156-175")
st.sidebar.write("**Z5 (Max):** 176-199")

# --- LOGICA: KM & RATIO PROGRESSIE ---
today = datetime.now()
last_week_date = today - timedelta(days=7)

if not st.session_state.logs.empty:
    st.session_state.logs['Datum'] = pd.to_datetime(st.session_state.logs['Datum'])
    last_week_runs = st.session_state.logs[(st.session_state.logs['Datum'] > last_week_date) & (st.session_state.logs['Type'] == 'RUNNING')]
    last_week_vol = last_week_runs['KM'].sum() if not last_week_runs.empty else 22.0
else:
    last_week_vol = 22.0

# Bepaal weektype (3 build, 1 deload)
week_num = today.isocalendar()[1]
is_deload = week_num % 4 == 0

# Ratio Logica
if is_deload:
    current_ratio = "9:1" # Rustiger aan in deload
    week_limit = round(last_week_vol * 0.7, 1)
    box_type = "info-box"
    title = "📉 Deload Week"
else:
    # Progressie van ratio op basis van pijn
    if injury_score <= 2:
        # Als we meer dan 3 runs hebben gedaan op 9:1, gaan we naar 10:1
        current_ratio = "10:1" if last_week_vol > 20 else "9:1"
    else:
        current_ratio = "9:1"
    week_limit = round(last_week_vol * 1.1, 1)
    box_type = "success-box"
    title = "🚀 Bouw Week"

# --- TABS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🚀 Daily Coach", "📅 Roadmap", "💪 Kracht", "📈 Progressie", "📂 Data"])

with tab1:
    st.header(f"Plan voor {today.strftime('%d %B')}")
    st.markdown(f"""
    <div class="{box_type}">
        <h3>{title}</h3>
        <p><b>Weeklimiet:</b> {week_limit} km totaal hardlopen</p>
        <p><b>Vandaag Protocol:</b> <span style='font-size: 20px; color: #FF4B4B;'>{current_ratio}</span> (Lopen : Wandelen)</p>
        <p><b>Focus Zone:</b> 125 - 140 bpm (Zone 2)</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Sessie Instructie")
        st.write(f"- Warm-up: 5 min wandelen / dribbelen.")
        st.write(f"- Kern: Herhaal {current_ratio} blokken tot je ± {round(week_limit/3, 1)} km bereikt.")
        st.write("- Na afloop: 5 min Mobility Board kuitstretch.")
    with col2:
        st.subheader("Hybride Tip")
        st.info("Je fietsritten (125-135 bpm) zijn perfecte 'aerobe vulling'. Houd dit vast voor je Sub-3 marathon basis.")

with tab2:
    st.header("📅 Roadmap naar Continu Hardlopen")
    roadmap = pd.DataFrame({
        "Fase": ["Week 1-2", "Week 3-4", "Week 5-6", "Week 7-8", "Week 9+"],
        "Ratio": ["9:1", "10:1 of 12:1", "15:1", "20:1", "Continu (30 min+)"],
        "Check": ["Geen pijn", "Stijfheid < 2", "Goede Z2 HR", "RI stabiel", "Target Sub-18"]
    })
    st.table(roadmap)
    st.caption("Let op: Bij pijn > 2 vallen we altijd één stap terug in de ratio.")

with tab3:
    st.header("💪 Home Gym Roulatie (A-D)")
    c_a, c_b = st.columns(2)
    with c_a:
        with st.expander("🦵 Sessie A: Benen (Stabiliteit)"):
            st.write("- **Single Leg RDL:** 3x12 (20kg KB)")
            st.write("- **Isometric Calf Raise:** 5x45s (Houd vast!)")
            st.write("- **Glute Bridge:** 3x20")
        with st.expander("👕 Sessie B: Upper Power"):
            st.write("- **Weighted Pull-ups:** 4xMax")
            st.write("- **Dips:** 4xMax")
            st.write("- **Barbell Row:** 3x12 (40kg)")
    with c_b:
        with st.expander("🦵 Sessie C: Benen (Kracht)"):
            st.write("- **Goblet Squat:** 4x15 (20kg KB)")
            st.write("- **Bulgarian Split Squat:** 3x10 per been")
            st.write("- **KB Swings:** 4x20 (Explosief)")
        with st.expander("⚖️ Sessie D: Core & Mobiliteit"):
            st.write("- **Ab-Roller:** 4x12")
            st.write("- **Mobility Board Stretch:** 10 min")
            st.write("- **Deadbugs:** 3x15")

with tab4:
    st.header("📈 AI Voorspelling & Conditie")
    runs = st.session_state.logs[st.session_state.logs['Type'] == 'RUNNING']
    if not runs.empty:
        curr_ri = runs['RunningIndex'].tail(5).mean()
        pred_5k = 26 - (curr_ri - 50) * 0.5
        m1, m2, m3 = st.columns(3)
        m1.metric("Huidige 5K Potentie", f"{int(pred_5k)}:{(pred_5k%1*60):02.0f} min")
        m2.metric("Running Index", f"{curr_ri:.1f}")
        m3.metric("Doel Gewicht", "73.0 kg")
        st.plotly_chart(px.line(runs, x='Datum', y='RunningIndex', title="VO2max Trend"), use_container_width=True)
    else:
        st.warning("Upload data om voorspellingen te zien.")

with tab5:
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
                'Pijn': injury_score, 'Gewicht': curr_weight, 'Ratio': current_ratio
            }
            if st.button("Opslaan in Dagboek"):
                st.session_state.logs = pd.concat([st.session_state.logs, pd.DataFrame([new_data])], ignore_index=True)
                st.success("Sessie opgeslagen!")
        except: st.error("Fout bij inlezen.")
    st.dataframe(st.session_state.logs.sort_values('Datum', ascending=False), use_container_width=True)
