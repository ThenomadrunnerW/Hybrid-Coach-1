import streamlit as st
import pandas as pd
import plotly.express as px # Voor professionele grafieken
from io import StringIO

# --- CONFIG ---
st.set_page_config(page_title="Hybrid Pro Coach", layout="wide")

# --- DATA INITIALISATIE ---
if 'logs' not in st.session_state:
    st.session_state.logs = pd.DataFrame(columns=['Datum', 'Type', 'KM', 'HR', 'RunningIndex', 'Pijn', 'Gewicht'])

# --- SIDEBAR ---
st.sidebar.header("🛡️ De Bodyguard")
curr_weight = st.sidebar.number_input("Huidig Gewicht (kg)", value=76.0, step=0.1)
injury_score = st.sidebar.slider("Achilles Pijn (0-10)", 0, 10, 0)
st.sidebar.divider()

# --- HELPER FUNCTIE: POLAR CSV LEZEN ---
def parse_polar(file):
    stringio = StringIO(file.getvalue().decode("utf-8"))
    df_raw = pd.read_csv(stringio, skiprows=0)
    # Pak de data uit de eerste rij van de Polar export
    data = {
        'Datum': df_raw.iloc[0]['Date'],
        'Type': df_raw.iloc[0]['Sport'],
        'KM': float(df_raw.iloc[0]['Total distance (km)']),
        'HR': int(df_raw.iloc[0]['Average heart rate (bpm)']),
        'RunningIndex': int(df_raw.iloc[0]['Running index']),
        'Pijn': injury_score,
        'Gewicht': curr_weight
    }
    return data

# --- TITEL ---
st.title("🏃‍♂️ Wladimir's Hybrid Dashboard")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["🚀 Coach", "📅 Blueprint", "💪 Home Gym", "📂 Polar Upload", "📈 Progressie"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Training van vandaag")
        if injury_score > 3:
            st.error("🚨 Achilles focus: Fietsen ipv hardlopen!")
        else:
            st.success("Lydiard Z2 Run: 8km @ 138-142 bpm")
    with col2:
        st.subheader("Voeding")
        st.write(f"Doel: 73kg (Huidig: {curr_weight}kg)")
        st.info("Eet vandaag extra eiwitten voor herstel na je krachtsessie.")

with tab2:
    st.header("Lydiard 5K-Marathon Blueprint")
    st.write("Fase: Aerobe Basis (Week 3/12)")
    st.table(pd.DataFrame({
        "Dag": ["Ma", "Di", "Wo", "Do", "Vr", "Za", "Zo"],
        "Training": ["Fiets 45m", "Run 8km", "Kracht A", "Run 8km", "Fiets 45m", "Lange Loop 12km", "Kracht B"]
    }))

with tab3:
    st.header("Home Gym Sessies")
    colA, colB = st.columns(2)
    with colA:
        st.write("**Sessie A (Benen/Core)**")
        st.write("- 3x10 Single Leg RDL (20kg KB)")
        st.write("- 3x15 Goblet Squats (20kg KB)")
        st.write("- 5x45s Isometric Calf Raise")
    with colB:
        st.write("**Sessie B (Upper/Explosief)**")
        st.write("- 3xMax Pull-ups")
        st.write("- 4x20 KB Swings (20kg)")
        st.write("- 3x12 Dips")

with tab4:
    st.header("Upload Polar Flow Data")
    st.write("Upload hier je Wladimir_Bijl_...CSV bestand uit Polar Flow.")
    uploaded_file = st.file_uploader("Kies Polar CSV bestand", type="csv")
    
    if uploaded_file:
        try:
            new_data = parse_polar(uploaded_file)
            st.write("### Gevonden Trainingsinformatie:")
            st.json(new_data)
            
            if st.button("Bevestig en Voeg toe aan Dagboek"):
                st.session_state.logs = pd.concat([st.session_state.logs, pd.DataFrame([new_data])], ignore_index=True)
                st.success("Training succesvol toegevoegd!")
        except Exception as e:
            st.error(f"Fout bij lezen bestand: {e}")

    st.divider()
    st.subheader("Huidig Dagboek")
    st.dataframe(st.session_state.logs)

with tab5:
    st.header("Analyse & Voortgang")
    if len(st.session_state.logs) > 0:
        # Grafiek 1: Running Index (Conditie)
        fig_ri = px.line(st.session_state.logs, x='Datum', y='RunningIndex', title='Conditie Trend (Running Index)')
        st.plotly_chart(fig_ri, use_container_width=True)
        
        # Grafiek 2: Afstand per week
        fig_km = px.bar(st.session_state.logs, x='Datum', y='KM', title='Hardloop Volume (KM)')
        st.plotly_chart(fig_km, use_container_width=True)
        
        # Grafiek 3: Gewicht verloop
        fig_w = px.line(st.session_state.logs, x='Datum', y='Gewicht', title='Gewicht Trend (Target 73kg)')
        st.plotly_chart(fig_w, use_container_width=True)
    else:
        st.info("Upload eerst data in de 'Polar Upload' tab om je progressie te zien.")
