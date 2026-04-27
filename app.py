import streamlit as st
import pandas as pd
import plotly.express as px
from io import StringIO
from datetime import datetime, timedelta

# --- CONFIG ---
st.set_page_config(page_title="Hybrid Coach Pro", layout="wide")

# --- CSS VOOR UI ---
st.markdown("""
<style>
    .reportview-container { background: #f0f2f6; }
    .stMetric { background-color: #ffffff; padding: 10px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .training-card { background-color: #e1f5fe; padding: 15px; border-radius: 10px; border-left: 5px solid #0288d1; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# --- DATA INITIALISATIE ---
if 'logs' not in st.session_state:
    st.session_state.logs = pd.DataFrame(columns=['Datum', 'Type', 'KM', 'Duur', 'HR', 'RunningIndex', 'Pijn', 'Gewicht'])

# --- SIDEBAR: COACH SETTINGS ---
st.sidebar.header("🛡️ Persoonlijk Profiel")
weight = st.sidebar.number_input("Gewicht (kg)", value=76.0)
hr_max = 190
hr_rest = 51

# --- BEREKEN ZONES ---
hrr = hr_max - hr_rest
zones = {
    "Zone 1 (Herstel)": f"{int(hr_rest + 0.50*hrr)} - {int(hr_rest + 0.60*hrr)} bpm",
    "Zone 2 (Aerobe Basis)": f"{int(hr_rest + 0.60*hrr)} - {int(hr_rest + 0.70*hrr)} bpm",
    "Zone 3 (Tempo)": f"{int(hr_rest + 0.70*hrr)} - {int(hr_rest + 0.80*hrr)} bpm",
    "Zone 4 (Threshold)": f"{int(hr_rest + 0.80*hrr)} - {int(hr_rest + 0.90*hrr)} bpm"
}

# --- TABS ---
tab_coach, tab_plan, tab_prog, tab_data = st.tabs(["🚀 Daily Coach", "📅 Programma", "📈 Analyse", "📂 Data"])

with tab_coach:
    st.header(f"Training voor {datetime.now().strftime('%A %d %B')}")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"""
        <div class="training-card">
            <h3>🏃‍♂️ Lydiard Aerobe Opbouw (Achilles Safe)</h3>
            <p><b>Focus:</b> Zone 2 Endurance</p>
            <p><b>Protocol:</b> 9:1 Run-Walk (9 min lopen, 1 min wandelen)</p>
            <p><b>Afstand:</b> 8.0 - 8.8 km (Blijf binnen 10% groei)</p>
            <p><b>Hartslag Target:</b> {zones['Zone 2 (Aerobe Basis)']}</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.subheader("HR Zone Dashboard")
        for zone, range_bpm in zones.items():
            st.write(f"**{zone}:** `{range_bpm}`")

with tab_plan:
    st.header("📅 Trainingsschema")
    period = st.radio("Overzicht per:", ["Week", "Maand"], horizontal=True)
    
    # Voorbeeld schema data
    schema_weekly = pd.DataFrame({
        "Dag": ["Maandag", "Dinsdag", "Woensdag", "Donderdag", "Vrijdag", "Zaterdag", "Zondag"],
        "Sessie": ["🚲 Fiets Herstel (45m)", "🏃 8km Lydiard Run", "💪 Kracht A", "🏃 6km Lydiard Run", "🚲 Fiets Herstel (45m)", "🏃 10km Lange Loop", "💪 Kracht B"],
        "Zone": ["Zone 1", "Zone 2", "Power", "Zone 2", "Zone 1", "Zone 2", "Mobility"]
    })
    
    if period == "Week":
        st.table(schema_weekly)
    else:
        st.info("Maandoverzicht: Focus op accumulatie van Zone 2 uren. Target: 100km lopen + 200km fietsen per maand.")

with tab_prog:
    st.header("📈 Progressie & AI Predictions")
    
    # Bereken gemiddelde RI
    runs = st.session_state.logs[st.session_state.logs['Type'] == 'RUNNING']
    current_ri = runs['RunningIndex'].tail(5).mean() if not runs.empty else 57.0
    
    col_p1, col_p2, col_p3 = st.columns(3)
    
    # 5K Predictor
    pred_5k = 26 - (current_ri - 50) * 0.5
    col_p1.metric("Huidige 5K Potentie", f"{int(pred_5k)}:{(pred_5k%1*60):02.0f} min")
    
    # Marathon Shape (Gebaseerd op verste loop van 8km)
    marathon_foundation = (8 / 32) * 100 # 32km is de Lydiard standaard voor Sub-3 training
    col_p2.metric("Marathon Fundering", f"{marathon_foundation:.1f}%", help="Hoeveel % van de benodigde duurkracht heb je?")
    
    # Achilles Trend
    avg_pain = st.session_state.logs['Pijn'].tail(5).mean() if not st.session_state.logs.empty else 0
    col_p3.metric("Achilles Stabiliteit", f"{10-avg_pain}/10")

    if not runs.empty:
        st.subheader("Conditie Verloop (Running Index)")
        fig = px.area(runs, x='Datum', y='RunningIndex', title="VO2max Trend (Lydiard Engine)")
        st.plotly_chart(fig, use_container_width=True)

with tab_data:
    st.header("📂 Data Import")
    uploaded = st.file_uploader("Sleep je Polar CSV hierheen", type="csv")
    if uploaded:
        stringio = StringIO(uploaded.getvalue().decode("utf-8"))
        df_raw = pd.read_csv(stringio)
        
        # Pak data
        ri = df_raw.iloc[0]['Running index']
        data = {
            'Datum': df_raw.iloc[0]['Date'],
            'Type': df_raw.iloc[0]['Sport'],
            'KM': round(float(df_raw.iloc[0]['Total distance (km)']), 2),
            'Duur': df_raw.iloc[0]['Duration'],
            'HR': int(df_raw.iloc[0]['Average heart rate (bpm)']),
            'RunningIndex': int(ri) if pd.notnull(ri) else 0,
            'Pijn': st.session_state.get('last_pain', 0),
            'Gewicht': weight
        }
        if st.button("Sessie opslaan"):
            st.session_state.logs = pd.concat([st.session_state.logs, pd.DataFrame([data])], ignore_index=True)
            st.success("Training opgeslagen!")
            
    st.subheader("Trainingslogboek")
    st.dataframe(st.session_state.logs.sort_values('Datum', ascending=False), use_container_width=True)
