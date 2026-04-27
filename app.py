import streamlit as st
import pandas as pd
import plotly.express as px
from io import StringIO
from datetime import datetime, timedelta

# --- CONFIG ---
st.set_page_config(page_title="Hybrid Coach Pro V8", layout="wide")

# --- INITIALISATIE ---
if 'logs' not in st.session_state:
    st.session_state.logs = pd.DataFrame(columns=['Datum', 'Type', 'KM', 'Duur', 'HR', 'RunningIndex', 'Pijn', 'Gewicht', 'Ratio'])

# --- SIDEBAR & ZONES ---
st.sidebar.header("🛡️ Coach Dashboard")
curr_weight = st.sidebar.number_input("Huidig Gewicht (kg)", value=76.0)
injury_score = st.sidebar.slider("Achilles Pijn (0-10)", 0, 10, 0)

# Jouw specifieke zones
z_info = {
    "Z1 (Herstel)": "90 - 124 bpm",
    "Z2 (Basis)": "125 - 140 bpm",
    "Z3 (Tempo)": "141 - 155 bpm",
    "Z4 (Threshold)": "156 - 175 bpm",
    "Z5 (Max)": "176 - 199 bpm"
}

# --- LOGICA: PACES BEREKENEN OP RI ---
runs = st.session_state.logs[st.session_state.logs['Type'] == 'RUNNING']
current_ri = runs['RunningIndex'].tail(5).mean() if not runs.empty else 57.0

# 5K pace schatting in sec/km
five_k_pace_sec = (26 - (current_ri - 50) * 0.5) * 60 / 5 
z2_pace_sec = five_k_pace_sec * 1.35
threshold_pace_sec = five_k_pace_sec * 1.08
interval_400_sec = (five_k_pace_sec * 0.95) * 0.4

def format_pace(seconds):
    return f"{int(seconds//60)}:{int(seconds%60):02d} min/km"

# --- TABS ---
tabs = st.tabs(["🚀 Coach", "🔮 Toekomst Planner", "💪 Kracht (A-D)", "📈 Progressie", "📂 Data"])

with tabs[0]:
    st.header(f"Focus voor {datetime.now().strftime('%d %B')}")
    st.info(f"**Jouw Sub-18 Threshold:** {format_pace(threshold_pace_sec)} | **Zone 2 Tempo:** {format_pace(z2_pace_sec)}")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Training Vandaag")
        st.success(f"9:1 Lydiard Run | Range: {z_info['Z2 (Basis)']} | Afstand: {round(24/3,1)} km")
    with col2:
        st.subheader("Doel")
        st.write("Versterken van de pees-matrix en vergroten van de linker hartkamer.")

with tabs[1]:
    st.header("📅 4-Weken Roadmap (Interfereert met Volume & Intensiteit)")
    
    # Volume berekening
    base_vol = 24.0 # Startwaarde
    
    for w in range(1, 5):
        is_del = (w == 4)
        vol = base_vol * (1.1 ** (w-1)) if not is_del else base_vol * 1.1**2 * 0.7
        type_w = "BOUWWEEK" if not is_del else "DELOAD (Herstel)"
        
        with st.expander(f"Week {w}: {type_w} - Target: {vol:.1f} km"):
            st.write(f"**Focus:** {'Progressie in kilometers' if not is_del else 'Supercompensatie'}")
            
            day_data = {
                "Dag": ["Maandag", "Dinsdag", "Woensdag", "Donderdag", "Vrijdag", "Zaterdag", "Zondag"],
                "Sessie": ["🚲 Fiets Z1", "🏃 Run Z2", "💪 Kracht A", "🏃 Run Z2", "🚲 Fiets Z1", "🏃 Lange Loop", "💪 Kracht B"],
                "Target": ["45 min", f"{vol*0.25:.1f} km", "Stability", f"{vol*0.25:.1f} km", "45 min", f"{vol*0.5:.1f} km", "Power"]
            }
            st.table(pd.DataFrame(day_data))
            
            st.markdown("---")
            st.write("**Uitleg per sessie:**")
            st.write("- **Run Z2:** Het fundament. Doel: Mitochondriële dichtheid verhogen.")
            st.write("- **Fiets Z1:** 'Flushing'. Afvalstoffen uit de benen fietsen zonder impact.")
            st.write(f"- **Interval Preview (voor later):** Bijv. 10x400m op **{int(interval_400_sec//60)}:{(interval_400_sec%60):02.0f} min/km**.")

with tabs[2]:
    st.header("💪 Kracht Roulatie (A-D)")
    c1, c2 = st.columns(2)
    with c1:
        with st.expander("Sessie A (Stability)"): st.write("- Single Leg RDL, Isometric Calf Raise, Tibialis Raise")
        with st.expander("Sessie B (Upper)"): st.write("- Pull-ups, Dips, Barbell Row")
    with c2:
        with st.expander("Sessie C (Force)"): st.write("- Goblet Squat, Bulgarian Split Squat, KB Swings")
        with st.expander("Sessie D (Core)"): st.write("- Ab-Roller, Plank, Mobility Board")

with tabs[3]:
    st.header("📈 AI Analyse & Voorspelling")
    col_z1, col_z2 = st.columns(2)
    
    with col_z1:
        st.subheader("Jouw Zones & Threshold")
        for z, r in z_info.items():
            st.write(f"**{z}:** `{r}`")
        st.warning(f"**Anarobe Threshold:** {format_pace(threshold_pace_sec)} @ ~165 bpm")
        
    with col_z2:
        st.subheader("PR Voorspelling")
        st.metric("Verwachte 5K tijd", f"{int(pred_5k)}:{(pred_5k%1*60):02.0f} min")
        st.write("Om Sub-18 te halen moet je Running Index naar 65.")

with tabs[4]:
    uploaded = st.file_uploader("Upload Polar CSV", type="csv")
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
                'Pijn': injury_score, 'Gewicht': curr_weight
            }
            if st.button("Opslaan"):
                st.session_state.logs = pd.concat([st.session_state.logs, pd.DataFrame([new_data])], ignore_index=True)
                st.success("Sessie opgeslagen!")
        except: st.error("Upload mislukt.")
    st.dataframe(st.session_state.logs.sort_values('Datum', ascending=False), use_container_width=True)
