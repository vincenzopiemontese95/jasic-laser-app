import streamlit as st
import pandas as pd
import numpy as np

# Configurazione Pagina
st.set_page_config(page_title="Jasic Laser Sinergic App", layout="centered")

# --- DATABASE INIZIALE ---
if 'db_parametri' not in st.session_state:
    st.session_state.db_parametri = pd.DataFrame([
        {
            "Materiale": "Acciaio Inox",
            "Giunto": "Full penetration",
            "Spessore": 1.0,
            "Potenza": 450,
            "Wobble_W": 2.5,
            "Wobble_F": 300,
            "V_Filo": 80,
            "Diametro_Filo": 1.0,
            "Focus": -0.5
        }
    ])

# --- LOGICA DI CALCOLO ---
def calcola_parametri(materiale, giunto, spessore_target):
    dati_mat = st.session_state.db_parametri[st.session_state.db_parametri['Materiale'] == materiale]
    if dati_mat.empty: return None

    # Trova il punto reale più vicino per lo spessore
    idx_vicino = (dati_mat['Spessore'] - spessore_target).abs().idxmin()
    base = dati_mat.loc[idx_vicino]
    
    moltiplicatori = {
        "Butt Joint": 0.85,
        "Full penetration": 1.0,
        "Inner Joint": 0.92,
        "Outer Joint": 0.78
    }
    
    ratio = spessore_target / base['Spessore']
    potenza = base['Potenza'] * (ratio ** 1.15) * moltiplicatori[giunto]
    wobble_w = min(base['Wobble_W'] * (ratio ** 0.4), 4.5)
    v_filo = base['V_Filo'] * ratio
    
    # Il focus tende a scendere (più negativo) all'aumentare dello spessore per la penetrazione
    focus_stimato = max(base['Focus'] - (0.2 * (ratio - 1)), -2.0)
    
    return {
        "Potenza (W)": int(min(potenza, 2000)),
        "Wobble Width (mm)": round(wobble_w, 1),
        "Wobble Freq (Hz)": int(base['Wobble_F']),
        "Velocità Filo (cm/min)": int(v_filo),
        "Diametro Filo (mm)": base['Diametro_Filo'],
        "Focus (mm)": round(focus_stimato, 1)
    }

# --- INTERFACCIA ---
st.title("⚡ Jasic Laser Sinergic Pro")
st.markdown(f"**Hardware:** Raycus 2kW | Torcia WSX HD31")

choice = st.sidebar.selectbox("Menu", ["Calcolatore Operatore", "Area Amministratore"])

if choice == "Calcolatore Operatore":
    st.header("🔍 Calcolo Parametri")
    col1, col2 = st.columns(2)
    with col1:
        mat = st.selectbox("Materiale", st.session_state.db_parametri['Materiale'].unique())
        giunto = st.selectbox("Tipo di Giunto", ["Butt Joint", "Full penetration", "Inner Joint", "Outer Joint"])
    with col2:
        # Step impostato a 0.10mm come richiesto
        spessore = st.number_input("Spessore Materiale (mm)", min_value=0.1, max_value=12.0, value=1.0, step=0.10)
    
    if st.button("Genera Parametri"):
        res = calcola_parametri(mat, giunto, spessore)
        if res:
            st.success(f"Parametri suggeriti per {mat} {spessore}mm ({giunto})")
            c1, c2, c3 = st.columns(3)
            c1.metric("Potenza", f"{res['Potenza (W)']} W")
            c2.metric("Wobble L", f"{res['Wobble Width (mm)']} mm")
            c3.metric("Wobble F", f"{res['Wobble Freq (Hz)']} Hz")
            
            st.divider()
            
            c4, c5, c6 = st.columns(3)
            c4.metric("Velocità Filo", f"{res['Velocità Filo (cm/min)']} cm/min")
            c5.metric("Ø Filo", f"{
