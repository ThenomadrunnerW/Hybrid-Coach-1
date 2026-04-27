import streamlit as st
import pandas as pd
import plotly.express as px
from io import StringIO
from datetime import datetime

# --- CONFIG ---
st.set_page_config(page_title="Wladimir Hybrid Coach", layout="wide")

# --- CSS VOOR DARK/LIGHT MODE VEILIGE UI ---
st.markdown("""
<style>
    /* Kaart-stijl die werkt in dark mode */
    .st-emotion-cache-1r6slb0 { border: 1px solid #4a4a4a; border-radius: 10px; padding: 20px; }
    .coach-box {
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #FF4B4B;
        background-color: rgba(255, 75, 75, 0.1);
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- INITIALISATIE ---
if 'logs' not in st.session_state:
    st.session_state.logs = pd.DataFrame(columns=['Datum', 'Type', 'KM', 'Duur', 'HR', 'RunningIndex', 'Pijn', 'Gewicht'])

# --- SIDEBAR: PROFIEL & ZONES ---
st.sidebar.header("🛡️ Coach Instellingen")
weight = st.sidebar.number_input("Gewicht (kg)", value=76.0)
hr_max = 190
hr_rest = 51
hrr = hr_max - hr_rest

zones = {
    "Z1 (Herstel)": [int(hr_rest + 0.50*hrr), int(hr_rest + 0.60*hrr)],
    "Z2 (Lydiard Basis)": [int(hr_rest + 0.60*hrr), int(hr_rest + 0.70*hrr)],
    "Z3 (Tempo)": [int(hr_rest + 0.70*hrr), int(hr_rest + 0.80*hrr)],
    "Z4 (Threshold)": [int(hr_rest + 0.80*hrr), int(hr_rest + 0.90*hrr)]
}

# --- TABS ---
tabs = st.tabs(["🚀 Daily Coach", "📅 Programma", "💪 Kracht", "📈 Progressie", "📂 Data"])

with tabs[0]:
    st.header(f"Plan voor {datetime.now().strftime('%A %d %B')}")
    
    # Coach Card met dynamische tekstkleur voor dark mode
    st.markdown(f"""
    <div class="coach-box">
        <h3 style='margin-top:0;'>🏃‍♂️ Lydiard Aerobe Opbouw</h3>
        <p><b>Status:</b> Achilles Herstel Protocol (9:1)</p>
        <p><b>Focus:</b> 8.0 - 8.5 km in Zone 2</p>
        <p><b>HR Range:</b> {zones['Z2 (Lydiard Basis)'][0]} - {zones['Z2 (Lydiard Basis)'][1]} bpm</p>
        <p><i>Loop 9 minuten, wandel 1 minuut. Herhaal tot afstand bereikt is.</i></p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Hartslag Doelen")
        for z, r in zones.items():
            st.write(f"**{z}:** {r[0]}-{r[1]} bpm")
    with c2:
        st.subheader("Mobiliteit Tip")
        st.info("Gebruik je Mobility Board vandaag: 3 x 60 sec rekken per kuit.")

with tabs[1]:
    st.header("📅 Trainingsschema")
    schema = pd.DataFrame({
        "Dag": ["Maandag", "Dinsdag", "Woensdag", "Donderdag", "Vrijdag", "Zaterdag", "Zondag"],
        "Sessie": ["🚲 Fiets Herstel (Z1)", "🏃 8km Steady (Z2)", "💪 Kracht A", "🏃 8km Steady (Z2)", "🚲 Fiets Herstel (Z1)", "🏃 10-12km Duur (Z2)", "💪 Kracht B"],
        "Zones": ["< 134 bpm", "134 - 148 bpm", "Home Gym", "134 - 148 bpm", "< 134 bpm", "134 - 148 bpm", "Mobility"]
    })
    st.dataframe(schema, use_container_width=True, hide_index=True)

with tabs[2]:
    st.header("💪 Kracht & Hyrox (Home Gym)")
    st.write("Jouw uitrusting: 40kg Barbell, 20kg KB, Pull-up bar.")
    
    k_col1, k_col2 = st.columns(2)
    with k_col1:
        st.subheader("Sessie A (Benen & Core)")
        st.info("Focus op Achilles-veiligheid")
        st.write("- **Goblet Squat (20kg KB):** 3 x 15")
        st.write("- **Single Leg RDL (20kg KB):** 3 x 10 per been")
        st.write("- **Isometric Calf Raise (Board):** 5 x 45 sec vasthouden")
        st.write("- **Ab-Roller:** 3 x 12")
    
    with k_col2:
        st.subheader("Sessie B (Upper Body Power)")
        st.info("Focus op Hyrox Pull/Push")
        st.write("- **Weighted Pull-ups:** 3 x Max")
        st.write("- **Dips:** 3 x Max")
        st.write("- **KB Swings (20kg):** 4 x 20 (Explosief)")
        st.write("- **Push-ups op Parallettes:** 3 x Max (Diepe stretch)")

with tabs[3]:
    st.header("📈 Voortgang & Voorspellingen")
    
    # Berekening
    runs = st.session_state.logs[st.session_state.logs['Type'] == 'RUNNING']
    current_ri = runs['RunningIndex'].tail(5).mean() if not runs.empty else 57.0
    
    m1, m2, m3 = st.columns(3)
    # Sub-18 5K voorspelling (Linear approximation op basis van RI)
    pred_5k = 26 - (current_ri - 50) * 0.5
    m1.metric("5K Potentie (Nu)", f"{int(pred_5k)}:{(pred_5k%1*60):02.0f} min")
    
    # Marathon Foundation
    verste_loop = runs['KM'].max() if not runs.empty else 8.0
    foundation = (verste_loop / 32) * 100
    m2.metric("Marathon Basis", f"{foundation:.1f}%")
    
    m3.metric("Running Index", f"{current_ri:.1f}")

    if not runs.empty:
        # Plotly chart die thema van Streamlit volgt (Safe voor dark mode)
        fig = px.line(runs, x='Datum', y='RunningIndex', title="Conditie Verloop (Running Index)", markers=True)
        st.plotly_chart(fig, use_container_width=True)
        
        fig2 = px.bar(st.session_state.logs, x='Datum', y='KM', color='Type', title="Weekoverzicht Volume")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("Upload data om grafieken te genereren.")

with tabs[4]:
    st.header("📂 Polar Data Import")
    uploaded_file = st.file_uploader("Kies Polar Flow CSV", type="csv")
    
    if uploaded_file:
        try:
            stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
            df_raw = pd.read_csv(stringio)
            ri = df_raw.iloc[0]['Running index']
            
            data = {
                'Datum': df_raw.iloc[0]['Date'],
                'Type': df_raw.iloc[0]['Sport'],
                'KM': round(float(df_raw.iloc[0]['Total distance (km)']), 2),
                'Duur': df_raw.iloc[0]['Duration'],
                'HR': int(df_raw.iloc[0]['Average heart rate (bpm)']),
                'RunningIndex': int(ri) if pd.notnull(ri) else 0,
                'Pijn': 0, 'Gewicht': weight
            }
            if st.button("Training Opslaan"):
                st.session_state.logs = pd.concat([st.session_state.logs, pd.DataFrame([data])], ignore_index=True)
                st.success("Sessie toegevoegd!")
        except Exception as e:
            st.error(f"Fout: {e}")
    
    st.divider()
    st.subheader("Trainingslogboek")
    st.dataframe(st.session_state.logs.sort_values('Datum', ascending=False), use_container_width=True)
