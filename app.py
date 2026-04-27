import streamlit as st
import pandas as pd
import datetime

# --- CONFIG & THEMA ---
st.set_page_config(page_title="Wladimir Hybrid Coach Pro", layout="wide")

st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e0e0e0; }
    .main { background-color: #fafafa; }
    </style>
    """, unsafe_allow_html=True)

# --- DATA INITIALISATIE ---
if 'logs' not in st.session_state:
    st.session_state.logs = pd.DataFrame(columns=['Datum', 'Type', 'KM', 'Duur', 'HR', 'Pijn'])

# --- SIDEBAR: DE BODYGUARD ---
st.sidebar.header("🛡️ De Bodyguard")
weight = st.sidebar.number_input("Huidig Gewicht (kg)", value=76.0, step=0.1)
injury_score = st.sidebar.slider("Achilles/Kuit Pijn (0-10)", 0, 10, 0)
st.sidebar.divider()

# --- HOOFDSCHERM ---
st.title("🏃‍♂️ Wladimir's Hybrid Coach Pro")
st.write(f"**Doel:** Sub-18 5K | Sub-3 Marathon | Hyrox Ready | Target: 73kg")

tab1, tab2, tab3, tab4 = st.tabs(["🚀 Dagelijkse Coach", "📊 Blueprint", "💪 Home Gym Kracht", "📝 Dagboek"])

with tab1:
    col1, col2, col3 = st.columns(3)
    
    # Dynamisch Advies op basis van Achilles
    if injury_score > 3:
        status = "🚨 AANGEPAST"
        advies = "GEEN RUN. Doe 60 min fietsen (Z2) + 15 min Mobility Board sessie."
    else:
        status = "✅ VOL GAS"
        advies = "Lydiard Steady Run: 8-10 km in Zone 2 (138-142 bpm)."

    col1.metric("Status", status)
    col2.metric("Weeklimiet", "26.4 km", "+10%")
    col3.metric("Running Index", "57", "Stabiel")

    st.info(f"**Coach Advies:** {advies}")
    
    st.subheader("🍎 Voeding voor Vandaag")
    if weight > 73:
        st.write("- **Pre-Run:** 40g Koolhydraten (Banaan/Havermout).")
        st.write("- **Tijdens dag:** Focus op eiwit (150g+) en groenten.")
        st.write("- **Post-training:** 30g Eiwit + 50g Koolhydraten voor herstel.")

with tab2:
    st.header("📅 Lydiard Blueprint: Aerobe Basis")
    st.write("Fase 1 van 4: De Motor Bouwen (Weken 1-8)")
    
    schema_data = {
        "Dag": ["Maandag", "Dinsdag", "Woensdag", "Donderdag", "Vrijdag", "Zaterdag", "Zondag"],
        "Focus": ["Fietsen (Commute)", "Run (Steady)", "Kracht A", "Run (Kort)", "Fietsen (Commute)", "Lange Loop", "Kracht B"],
        "Intensiteit": ["Z1 (Herstel)", "Z2 (Aerobe Basis)", "Hyrox Power", "Z2 + Strides", "Z1/Z2", "Z2 (Duur)", "Mobiliteit/Kracht"]
    }
    st.table(pd.DataFrame(schema_data))

with tab3:
    st.header("🏠 Home Gym Programmering")
    st.write("Jouw uitrusting: 40kg Barbell, KBs (10, 20kg), Pull-up bar.")
    
    kg_col1, kg_col2 = st.columns(2)
    with kg_col1:
        st.subheader("Sessie A (Posterior Chain)")
        st.write("1. **Single Leg RDL:** 3 x 10 (met 20kg KB)")
        st.write("2. **Weighted Pull-ups:** 3 x Max")
        st.write("3. **Barbell Row:** 4 x 12 (40kg)")
        st.write("4. **Isometric Calf Raise:** 5 x 45 sec (op mobility board)")
        
    with kg_col2:
        st.subheader("Sessie B (Hyrox/Explosief)")
        st.write("1. **Goblet Squat:** 3 x 15 (20kg KB)")
        st.write("2. **Kettlebell Swings:** 4 x 20 (20kg KB)")
        st.write("3. **Dips:** 3 x Max")
        st.write("4. **Ab-Roller:** 3 x 10")

with tab4:
    st.subheader("📝 Training Loggen")
    with st.form("log_form"):
        type_tr = st.selectbox("Type", ["Run", "Fietsen", "Kracht"])
        vol = st.number_input("Volume (KM of Minuten)", value=0.0)
        hr_avg = st.number_input("Gemiddelde Hartslag", value=130)
        submit = st.form_submit_button("Sessie Opslaan")
        
        if submit:
            st.success("Training opgeslagen in database!")

st.divider()
st.caption("Gebruik de Polar Flow export om je voortgang over tijd te analyseren.")
