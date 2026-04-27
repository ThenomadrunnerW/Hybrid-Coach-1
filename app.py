import streamlit as st
import pandas as pd
import plotly.express as px
from io import StringIO

# --- CONFIG ---
st.set_page_config(page_title="Hybrid Pro Coach", layout="wide")

# --- DATA INITIALISATIE ---
if 'logs' not in st.session_state:
    st.session_state.logs = pd.DataFrame(columns=['Datum', 'Type', 'KM', 'Duur', 'HR', 'RunningIndex', 'Pijn', 'Gewicht'])

# --- SIDEBAR ---
st.sidebar.header("🛡️ De Bodyguard")
curr_weight = st.sidebar.number_input("Huidig Gewicht (kg)", value=76.0, step=0.1)
injury_score = st.sidebar.slider("Achilles Pijn (0-10)", 0, 10, 0)
st.sidebar.divider()

# --- HELPER FUNCTIE: POLAR CSV LEZEN ---
def parse_polar(file):
    stringio = StringIO(file.getvalue().decode("utf-8"))
    df_raw = pd.read_csv(stringio, skiprows=0)
    
    # Haal waarden op en vervang lege waarden (NaN) door 0
    ri = df_raw.iloc[0]['Running index']
    ri_value = int(ri) if pd.notnull(ri) else 0
    
    data = {
        'Datum': df_raw.iloc[0]['Date'],
        'Type': df_raw.iloc[0]['Sport'],
        'KM': round(float(df_raw.iloc[0]['Total distance (km)']), 2),
        'Duur': df_raw.iloc[0]['Duration'],
        'HR': int(df_raw.iloc[0]['Average heart rate (bpm)']),
        'RunningIndex': ri_value,
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
        st.subheader("Status")
        st.write(f"Doel: 73kg (Huidig: {curr_weight}kg)")
        if not st.session_state.logs.empty:
            avg_ri = st.session_state.logs[st.session_state.logs['Type'] == 'RUNNING']['RunningIndex'].mean()
            if avg_ri > 0:
                st.metric("Gemiddelde Running Index", f"{avg_ri:.1f}")

with tab2:
    st.header("Lydiard 5K-Marathon Blueprint")
    st.write("Fase: Aerobe Basis")
    st.table(pd.DataFrame({
        "Dag": ["Maandag", "Dinsdag", "Woensdag", "Donderdag", "Vrijdag", "Zaterdag", "Zondag"],
        "Focus": ["Fiets Herstel", "Lydiard Run", "Kracht A", "Lydiard Run", "Fiets Herstel", "Lange Loop", "Kracht B"],
        "Detail": ["45 min commute", "8 km Zone 2", "Home Gym", "8 km Zone 2", "45 min commute", "12-14 km Zone 2", "Home Gym"]
    }))

with tab3:
    st.header("Home Gym Sessies")
    colA, colB = st.columns(2)
    with colA:
        st.write("**Sessie A (Posterior/Benen)**")
        st.write("- 3x10 Single Leg RDL (20kg KB)")
        st.write("- 3x15 Goblet Squats (20kg KB)")
        st.write("- 5x45s Isometric Calf Raise")
    with colB:
        st.write("**Sessie B (Hyrox/Upper)**")
        st.write("- 3xMax Pull-ups / Dips")
        st.write("- 4x20 KB Swings (20kg)")
        st.write("- 3x10 Ab-Roller")

with tab4:
    st.header("Upload Polar Flow Data")
    st.write("Upload je CSV bestanden (Hardlopen of Fietsen).")
    uploaded_file = st.file_uploader("Kies Polar CSV bestand", type="csv")
    
    if uploaded_file:
        try:
            new_data = parse_polar(uploaded_file)
            st.write("### Gevonden informatie:")
            st.write(f"**Type:** {new_data['Type']} | **Afstand:** {new_data['KM']} km | **Tijd:** {new_data['Duur']}")
            
            if st.button("Bevestig en Voeg toe aan Dagboek"):
                st.session_state.logs = pd.concat([st.session_state.logs, pd.DataFrame([new_data])], ignore_index=True)
                st.success("Training succesvol toegevoegd!")
        except Exception as e:
            st.error(f"Fout bij lezen bestand: {e}")

    st.divider()
    st.subheader("Huidig Dagboek")
    st.dataframe(st.session_state.logs, use_container_width=True)

with tab5:
    st.header("Analyse & Voortgang")
    if len(st.session_state.logs) > 0:
        # Filter alleen hardlopen voor Running Index
        runs = st.session_state.logs[st.session_state.logs['Type'] == 'RUNNING']
        
        if not runs.empty:
            fig_ri = px.line(runs, x='Datum', y='RunningIndex', title='Hardloop Conditie (Running Index)', markers=True)
            st.plotly_chart(fig_ri, use_container_width=True)
        
        # Totale kilometers (alle sporten)
        fig_km = px.bar(st.session_state.logs, x='Datum', y='KM', color='Type', title='Volume per Sessie (KM)')
        st.plotly_chart(fig_km, use_container_width=True)
        
        # Gewicht
        fig_w = px.line(st.session_state.logs, x='Datum', y='Gewicht', title='Gewicht Verloop')
        st.plotly_chart(fig_w, use_container_width=True)
    else:
        st.info("Nog geen data beschikbaar voor analyse.")
