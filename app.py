import streamlit as st
import pandas as pd
import numpy as np

# Configurazione Pagina
st.set_page_config(page_title="Jasic Laser Sinergic App", layout="centered")

# --- DATABASE ---
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
            "Diametro_Filo": 1.0  # <--- AGGIUNTO
        }
    ])

# --- LOGICA DI CALCOLO ---
def calcola_parametri(materiale, giunto, spessore_target):
    dati_mat = st.session_state.db_parametri[st.session_state.db_parametri['Materiale'] == materiale]
    if dati_mat.empty: return None

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
    
    return {
        "Potenza (W)": int(min(potenza, 2000)),
        "Wobble Width (mm)": round(wobble_w, 1),
        "Wobble Freq (Hz)": int(base['Wobble_F']),
        "Velocità Filo (cm/min)": int(v_filo),
        "Diametro Filo (mm)": base['Diametro_Filo'] # <--- AGGIUNTO
    }

# --- INTERFACCIA ---
st.title("⚡ Jasic Laser Sinergic")
st.markdown(f"**Hardware:** Raycus 2kW | Torcia WSX HD31")

choice = st.sidebar.selectbox("Menu", ["Calcolatore Operatore", "Area Amministratore"])

if choice == "Calcolatore Operatore":
    st.header("🔍 Calcolo Parametri")
    col1, col2 = st.columns(2)
    with col1:
        mat = st.selectbox("Materiale", st.session_state.db_parametri['Materiale'].unique())
        giunto = st.selectbox("Tipo di Giunto", ["Butt Joint", "Full penetration", "Inner Joint", "Outer Joint"])
    with col2:
        spessore = st.number_input("Spessore Materiale (mm)", min_value=0.5, max_value=10.0, value=1.0, step=0.5)
    
    if st.button("Genera Parametri"):
        res = calcola_parametri(mat, giunto, spessore)
        if res:
            st.success(f"Parametri suggeriti per {mat} {spessore}mm ({giunto})")
            c1, c2, c3, c4, c5 = st.columns(5) # <--- AGGIUNTA COLONNA
            c1.metric("Potenza", f"{res['Potenza (W)']} W")
            c2.metric("Wobble L", f"{res['Wobble Width (mm)']} mm")
            c3.metric("Wobble F", f"{res['Wobble Freq (Hz)']} Hz")
            c4.metric("Filo", f"{res['Velocità Filo (cm/min)']} cm/min")
            c5.metric("Ø Filo", f"{res['Diametro Filo (mm)']} mm") # <--- MOSTRATO
        else:
            st.error("Nessun dato base trovato.")

elif choice == "Area Amministratore":
    st.header("⚙️ Configurazione Sistema")
    with st.form("admin_form"):
        # ... (campi precedenti)
        new_mat = st.text_input("Materiale")
        new_giunto = st.selectbox("Giunto", ["Butt Joint", "Full penetration", "Inner Joint", "Outer Joint"])
        new_spessore = st.number_input("Spessore (mm)", value=1.0)
        new_potenza = st.number_input("Potenza (W)", value=450)
        new_w_w = st.number_input("Wobble Width (mm)", value=2.5)
        new_w_f = st.number_input("Wobble Freq (Hz)", value=300)
        new_v_f = st.number_input("Velocità Filo (cm/min)", value=80)
        new_d_f = st.number_input("Diametro Filo (mm)", value=1.0) # <--- AGGIUNTO INPUT
        
        if st.form_submit_button("Salva nel Database"):
            nuovo_dato = {
                "Materiale": new_mat, "Giunto": new_giunto, "Spessore": new_spessore,
                "Potenza": new_potenza, "Wobble_W": new_w_w, "Wobble_F": new_w_f, 
                "V_Filo": new_v_f, "Diametro_Filo": new_d_f # <--- SALVATO
            }
            st.session_state.db_parametri = pd.concat([st.session_state.db_parametri, pd.DataFrame([nuovo_dato])], ignore_index=True)
            st.success("Database aggiornato!")

    st.dataframe(st.session_state.db_parametri)
