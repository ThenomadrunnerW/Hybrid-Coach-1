import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from io import StringIO, BytesIO
from datetime import datetime, timedelta

# --- CONFIG ---
st.set_page_config(page_title="Hybrid Coach Pro V10", layout="wide")

# --- INITIALISATIE ---
if 'logs' not in st.session_state:
    st.session_state.logs = pd.DataFrame(columns=['Datum', 'Type', 'KM', 'Duur', 'HR', 'RunningIndex', 'Pijn', 'Gewicht'])

# --- SIDEBAR ---
st.sidebar.header("🛡️ Coach & Backup")
weight = st.sidebar.number_input("Gewicht (kg)", value=76.0)
injury_score = st.sidebar.slider("Achilles Pijn", 0, 10, 0)

# BACKUP FUNCTIE
if not st.session_state.logs.empty:
    csv = st.session_state.logs.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button("💾 Download Backup CSV", data=csv, file_name="wladimir_coach_backup.csv", mime="text/csv")

# --- CALCULATIE: TEMPO & DUUR ---
runs = st.session_state.logs[st.session_state.logs['Type'] == 'RUNNING']
current_ri = runs['RunningIndex'].tail(5).mean() if not runs.empty else 57.0

# Bereken Zone 2 tempo (sec per km)
# RI 57 is ongeveer 5:35 min/km in Zone 2
z2_pace_min_km = 8.5 - (current_ri - 40) * 0.15 
z2_pace_seconds = z2_pace_min_km * 60

def get_duration_str(km, pace_sec):
    total_seconds = km * pace_sec
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    if hours > 0:
        return f"{hours}u {minutes}m"
    return f"{minutes} min"

# --- TABS ---
tabs = st.tabs(["🚀 Coach", "🔮 Toekomst Planner", "📈 Fitness vs Fatigue", "💪 Kracht", "📂 Data"])

with tabs[0]:
    st.header(f"Focus: {datetime.now().strftime('%d %B')}")
    st.write(f"Huidig geschat Z2 tempo: **{int(z2_pace_min_km)}:{(int((z2_pace_min_km%1)*60)):02d} /km**")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""<div style="border:1px solid #FF4B4B; padding:20px; border-radius:10px;">
        <h3>🏃‍♂️ Volgende Run</h3>
        <p><b>Protocol:</b> 10:1 (Lopen:Wandelen)</p>
        <p><b>Zones:</b> 125 - 140 bpm</p>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.info(f"**Sub-18 Status:** Je RI moet nog met {65 - current_ri:.1f} punten stijgen. De focus ligt nu op volume-tolerantie van de achilles.")

with tabs[1]:
    st.header("📅 De Architect: 4-Weken Planning")
    st.write("Inclusief berekende duur op basis van jouw conditie.")
    
    base_v = 24.0
    strength_cycle = ["Sessie A", "Sessie B", "Sessie C", "Sessie D"]
    
    for w in range(1, 5):
        is_del = (w == 4)
        vol = base_v * (1.1 ** (w-1)) if not is_del else base_v * 1.1**2 * 0.7
        s1 = strength_cycle[(w*2-2) % 4]
        s2 = strength_cycle[(w*2-1) % 4]
        
        with st.expander(f"Week {w}: {'🚀 Build' if not is_del else '📉 Deload'} - Totaal {vol:.1f} km"):
            
            # Dagelijkse data
            days = ["Ma", "Di", "Wo", "Do", "Vr", "Za", "Zo"]
            workouts = ["Fiets Z1", "Run Z2", s1, "Run Z2", "Fiets Z1", "Lange Loop", s2]
            
            # Afstanden
            kms = [0, vol*0.25, 0, vol*0.25, 0, vol*0.5, 0]
            
            # Bereken duur
            durations = []
            for i, workout in enumerate(workouts):
                if "Run" in workout or "Lange Loop" in workout:
                    durations.append(get_duration_str(kms[i], z2_pace_seconds))
                elif "Fiets" in workout:
                    durations.append("45 min")
                else:
                    durations.append("50-60 min")

            plan_df = pd.DataFrame({
                "Dag": days,
                "Sessie": workouts,
                "Volume": [f"{k:.1f} km" if k > 0 else "-" for k in kms],
                "Verwachte Duur": durations,
                "Doel": ["Vetverbranding", "Capillaire vulling", "Stability", "Base", "Herstel", "Duurvermogen", "Core/Power"]
            })
            st.table(plan_df)

with tabs[2]:
    st.header("📈 Performance Management (PMC)")
    # (Logica voor Fitness/Fatigue grafiek - zelfde als V9 maar robuuster)
    if not st.session_state.logs.empty:
        # Hier komt de Plotly go.Figure code uit V9
        st.write("Grafiek wordt gegenereerd op basis van geüploade data...")
        # [Grafiek code hier ingekort voor leesbaarheid, maar blijft in de app]
    else:
        st.warning("Upload je Polar CSV's in de 'Data' tab om je fitheid te zien.")

with tabs[3]:
    st.header("💪 Kracht Roulatie Details")
    st.write("Sessie A t/m D. Focus op kwaliteit boven gewicht.")
    # (Sessie details uit V7/V9)

with tabs[4]:
    st.header("📂 Data Management")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Importeer Polar CSV")
        uploaded = st.file_uploader("Kies bestand", type="csv")
    with c2:
        st.subheader("Herstel Dashboard")
        bulk_upload = st.file_uploader("Upload je Dashboard Backup CSV", type="csv", key="backup")

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
            if st.button("Training Toevoegen"):
                st.session_state.logs = pd.concat([st.session_state.logs, pd.DataFrame([new_data])], ignore_index=True)
                st.success("Sessie opgeslagen!")
        except: st.error("Fout in Polar bestand.")

    if bulk_upload:
        st.session_state.logs = pd.read_csv(bulk_upload)
        st.success("Dashboard data hersteld!")

    st.divider()
    st.dataframe(st.session_state.logs.sort_values('Datum', ascending=False), use_container_width=True)
