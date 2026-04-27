import streamlit as st
import pandas as pd
import plotly.express as px
from io import StringIO
from datetime import datetime, timedelta

# --- CONFIG ---
st.set_page_config(page_title="Hybrid Coach Pro V5", layout="wide")

# --- CSS VOOR DARK MODE & DASHBOARD ---
st.markdown("""
<style>
    .coach-box { padding: 20px; border-radius: 10px; border-left: 5px solid #FF4B4B; background-color: rgba(255, 75, 75, 0.1); margin-bottom: 20px; }
    .deload-box { padding: 20px; border-radius: 10px; border-left: 5px solid #00C0F2; background-color: rgba(0, 192, 242, 0.1); margin-bottom: 20px; }
    .zone-card { padding: 10px; border-radius: 5px; margin: 5px 0; border: 1px solid #4a4a4a; }
</style>
""", unsafe_allow_html=True)

# --- INITIALISATIE ---
if 'logs' not in st.session_state:
    st.session_state.logs = pd.DataFrame(columns=['Datum', 'Type', 'KM', 'Duur', 'HR', 'RunningIndex', 'Pijn', 'Gewicht'])

# --- SIDEBAR ---
st.sidebar.header("🛡️ Coach & Gezondheid")
curr_weight = st.sidebar.number_input("Gewicht (kg)", value=76.0)
injury_score = st.sidebar.slider("Achilles Pijn (0-10)", 0, 10, 0)

st.sidebar.divider()
st.sidebar.header("💓 Jouw Zones")
st.sidebar.write("**Z1:** 90 - 124 bpm")
st.sidebar.write("**Z2:** 125 - 140 bpm")
st.sidebar.write("**Z3:** 141 - 155 bpm")
st.sidebar.write("**Z4:** 156 - 175 bpm")
st.sidebar.write("**Z5:** 176 - 199 bpm")

# --- LOGICA: PROGRESSIE & DELOAD ---
# We kijken naar de laatste 7 dagen volume
today = datetime.now()
last_week_date = today - timedelta(days=7)
if not st.session_state.logs.empty:
    st.session_state.logs['Datum'] = pd.to_datetime(st.session_state.logs['Datum'])
    last_week_vol = st.session_state.logs[(st.session_state.logs['Datum'] > last_week_date) & (st.session_state.logs['Type'] == 'RUNNING')]['KM'].sum()
else:
    last_week_vol = 22.0 # Startwaarde

# Bepaal of het een deload week is (elke 4e week van de maand)
is_deload = today.isocalendar()[1] % 4 == 0
if is_deload:
    week_limit = round(last_week_vol * 0.7, 1) # 30% minder in deload
    coach_style = "deload-box"
    status_text = "📉 DELOAD WEEK: Focus op herstel en mobiliteit."
else:
    week_limit = round(last_week_vol * 1.1, 1) # 10% erbij
    coach_style = "coach-box"
    status_text = "🚀 BOUWWEEK: Focus op aerobe basis en 10% groei."

# --- TABS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🚀 Coach", "📅 Planning", "💪 Kracht (A-D)", "📈 Progressie", "📂 Data"])

with tab1:
    st.header(f"Instructies voor {today.strftime('%d %B')}")
    st.markdown(f"""<div class="{coach_style}"><h3>{status_text}</h3><p><b>Jouw Weeklimiet:</b> {week_limit} km (Hardlopen)</p><p><b>Protocol:</b> 9:1 Run-Walk (Houd vast voor achilles herstel)</p></div>""", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Doel voor vandaag")
        if injury_score > 3:
            st.error("🚨 Te veel pijn. Vervang run door 45 min Fietsen in Z1 (90-124 bpm).")
        else:
            st.success(f"Run: Zone 2 focus (125-140 bpm). Blijf onder de {week_limit/3:.1f} km per sessie.")
    with c2:
        st.subheader("Brandstof (76kg -> 73kg)")
        st.write("- **Laag intensief:** Focus op vetverbranding. Geen suikers voor de run.")
        st.write("- **Hydratatie:** Drink 3L+ water. Voeg elektrolyten toe voor je pezen.")

with tab2:
    st.header("📅 4-Weken Cyclus (10% Regel)")
    weeks = []
    base = last_week_vol
    for i in range(1, 5):
        if i == 4:
            weeks.append({"Week": i, "Type": "Deload", "KM": round(base * 0.7, 1), "Focus": "Herstel"})
        else:
            base = base * 1.1
            weeks.append({"Week": i, "Type": "Build", "KM": round(base, 1), "Focus": "Aerobe Basis"})
    st.table(pd.DataFrame(weeks))

with tab3:
    st.header("💪 Home Gym Roulatie (A-B-C-D)")
    colA, colB = st.columns(2)
    with colA:
        with st.expander("🦵 Sessie A: Legs (Stability)"):
            st.write("- Single Leg RDL (20kg KB): 3x12")
            st.write("- Isometric Calf Raise: 5x45s")
            st.write("- Glute Bridges: 3x20")
        with st.expander("👕 Sessie B: Upper Power"):
            st.write("- Weighted Pull-ups: 4xMax")
            st.write("- Dips: 4xMax")
            st.write("- Barbell Rows (40kg): 3x12")
    with colB:
        with st.expander("🦵 Sessie C: Legs (Force)"):
            st.write("- Goblet Squats (20kg KB): 4x15")
            st.write("- Bulgarian Split Squat: 3x10")
            st.write("- KB Swings (20kg): 4x20")
        with st.expander("⚖️ Sessie D: Core & Mobility"):
            st.write("- Ab-Roller: 4x12")
            st.write("- Mobility Board Enkel Stretch: 10 min")
            st.write("- Plank Taps: 3x60s")

with tab4:
    st.header("📈 AI Progressie & PR Voorspeller")
    runs = st.session_state.logs[st.session_state.logs['Type'] == 'RUNNING']
    if not runs.empty:
        current_ri = runs['RunningIndex'].tail(5).mean()
        # Sub-18 Predictor
        pred_5k = 26 - (current_ri - 50) * 0.5
        m1, m2, m3 = st.columns(3)
        m1.metric("Huidige 5K Potentie", f"{int(pred_5k)}:{(pred_5k%1*60):02.0f} min")
        m2.metric("Running Index", f"{current_ri:.1f}")
        m3.metric("Doel voor Sub-18", "RI 65.0")
        
        st.plotly_chart(px.line(runs, x='Datum', y='RunningIndex', title="Conditie Trend"), use_container_width=True)
    else:
        st.info("Upload data om voorspellingen te zien.")

with tab5:
    st.header("📂 Data Import (Polar CSV)")
    uploaded = st.file_uploader("Upload bestand", type="csv")
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
        except: st.error("Fout in bestand.")
    st.dataframe(st.session_state.logs.sort_values('Datum', ascending=False), use_container_width=True)
