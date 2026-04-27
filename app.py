import streamlit as st
import pandas as pd

# --- CONFIG ---
st.set_page_config(page_title="Hybrid Coach Pro", layout="wide")

# --- DATA OPSLAG ---
if 'history' not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=['Datum', 'Sport', 'KM', 'HR', 'Pijn'])

# --- APP TITEL ---
st.title("🏃‍♂️ Wladimir's Hybrid Coach")
st.write("Route naar: Sub-18 5K | Sub-3 Marathon | Hyrox Power")

# --- SIDEBAR ---
st.sidebar.header("Instellingen")
fase = st.sidebar.selectbox("Lydiard Fase", ["Aerobe Basis", "Heuvel Fase", "Anaerobe Fase"])
injury_level = st.sidebar.slider("Pijn Achilles/Kuit (0-10)", 0, 10, 0)

# --- LYDIARD WEEKPLANNER LOGICA ---
st.header("📅 Jouw Trainingsweek (Blueprint)")

if fase == "Aerobe Basis":
    st.info("Doel: Je aerobe motor bouwen. Alles op hartslag 138-142 bpm.")
    schema = {
        "Dag": ["Maandag", "Dinsdag", "Woensdag", "Donderdag", "Vrijdag", "Zaterdag", "Zondag"],
        "Training": ["Rust of Licht Fietsen", "Lydiard Steady Run (Z2)", "Kracht (Hyrox Focus)", "Lydiard Steady Run (Z2)", "Fietsen (Herstel)", "Lange Loop (Z2)", "Kracht + Mobiliteit"],
        "Details": ["45 min zone 1", "7-8 km steady", "Squat/Deadlift focus", "8 km steady", "60 min relaxed", "10-12 km (10% opbouw)", "Focus op Achilles/Heupen"]
    }
elif fase == "Heuvel Fase":
    st.warning("Focus: Kracht-uithoudingsvermogen. Dit maakt je pezen 'bulletproof'.")
    schema = {
        "Dag": ["Maandag", "Dinsdag", "Woensdag", "Donderdag", "Vrijdag", "Zaterdag", "Zondag"],
        "Training": ["Rust", "Heuvelsprongen / Hill Bounding", "Kracht", "Lichte Run (Z2)", "Heuvel Sprints", "Lange Loop", "Mobiliteit"]
    }
# Voeg hier later Anaerobe fase toe

st.table(pd.DataFrame(schema))

# --- TRAININGSDAGBOEK ---
st.divider()
st.header("📝 Jouw Dagboek & Polar Upload")

uploaded_file = st.file_uploader("Upload je Polar CSV", type="csv")
if uploaded_file:
    try:
        df_raw = pd.read_csv(uploaded_file)
        # Polar parsing
        session_date = df_raw.iloc[0]['Date']
        session_km = df_raw.iloc[0]['Total distance (km)']
        session_hr = df_raw.iloc[0]['Average heart rate (bpm)']
        
        if st.button("Training Opslaan"):
            new_data = pd.DataFrame([{'Datum': session_date, 'Sport': 'Lopen', 'KM': session_km, 'HR': session_hr, 'Pijn': injury_level}])
            st.session_state.history = pd.concat([st.session_state.history, new_data], ignore_index=True)
            st.success("Sessie toegevoegd aan je geschiedenis!")
    except:
        st.error("Bestand niet herkend. Zorg dat je de CSV uit Polar Flow gebruikt.")

st.dataframe(st.session_state.history, use_container_width=True)

# --- KRACHT & REVALIDATIE ---
st.divider()
col1, col2 = st.columns(2)
with col1:
    st.subheader("💪 Kracht (The Bodyguard)")
    if injury_level > 2:
        st.error("⚠️ Hoge pijnscore! Doe alleen isometrische Calf Raises (vasthouden). Geen sprongen.")
    else:
        st.success("Pezen voelen goed. Focus op: RDL, Squats en Calf Raises (3 sets van 12).")
with col2:
    st.subheader("💧 Voeding & Hydratatie")
    st.write("- Drink minimaal 3.5L water vandaag.")
    st.write("- Eiwitdoel: ~130g (gebaseerd op 72kg lichaamswicht).")
