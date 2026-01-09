import streamlit as st
from fpdf import FPDF
import base64

# Ustawienia strony nawiązujące do travis.pl
st.set_page_config(page_title="Generator TRAVIS", page_icon="✈️", layout="wide")

# Custom CSS dla kolorystyki Travis (Granat #002d5a, Złoto/Żółty #fbbd08)
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stButton>button { background-color: #002d5a; color: white; border-radius: 5px; width: 100%; }
    .stTextInput>div>div>input { border-color: #002d5a; }
    h1, h2, h3 { color: #002d5a; border-bottom: 2px solid #fbbd08; padding-bottom: 10px; }
    .stTextArea>div>div>textarea { border-color: #002d5a; }
    </style>
    """, unsafe_allow_html=True)

# Logo z URL Travis
LOGO_URL = "https://travis.pl/wp-content/uploads/2025/07/logo_travis500.png"
st.image(LOGO_URL, width=250)

st.title("🏗️ Profesjonalny Kreator Ofert")

# --- PANEL BOCZNY: MULTIMEDIA ---
with st.sidebar:
    st.header("🖼️ Personalizacja")
    foto_glowne = st.file_uploader("Wgraj zdjęcie główne wycieczki", type=['jpg', 'png'])
    st.info("Zdjęcie pojawi się na samej górze oferty pod logo.")

# --- FORMULARZ EDYCJI ---
col_info1, col_info2 = st.columns(2)

with col_info1:
    tytul = st.text_input("Nazwa wycieczki", placeholder="np. MALTA 4 DNI - City Break")
    termin = st.text_input("Termin", placeholder="np. 27 czerwca - 1 lipca 2026")

with col_info2:
    st.subheader("💰 Tabela wycen")
    c_opcja1 = st.text_input("Opcja 1 (np. 46-50 os.)", placeholder="3 395,00 zł")
    c_opcja2 = st.text_input("Opcja 2 (np. 40-45 os.)", placeholder="3 470,00 zł")
    c_opcja3 = st.text_input("Opcja 3 (np. 35-39 os.)", placeholder="3 545,00 zł")

st.markdown("### 🗺️ Plan wycieczki")
plan = st.text_area("Wpisz plan (użyj 'Dzień 1:', 'Dzień 2:' itd.)", height=250, 
                    placeholder="Dzień 1: ...\nDzień 2: ...")

col_c1, col_c2 = st.columns(2)
with col_c1:
    st.markdown("### ✅ Cena zawiera")
    zawiera = st.text_area("Wpisz świadczenia (jedno pod drugim)", height=150,
                          placeholder="- Przelot\n- Transfer z Olsztyna\n- 3 noclegi (HB)")
with col_c2:
    st.markdown("### ❌ Cena nie zawiera")
    nie_zawiera = st.text_area("Wpisz koszty dodatkowe", height=150,
                               placeholder="- Bilety wstępu (ok. 130 EUR)\n- Własne wydatki")

# --- PODGLĄD GRAFICZNY ---
st.markdown("---")
if st.checkbox("Pokaż podgląd przed pobraniem"):
    if foto_glowne:
        st.image(foto_glowne, use_container_width=True)
    
    st.header(tytul)
    st.subheader(f"📅 {termin}")
    
    col_p1, col_p2 = st.columns([2, 1])
    with col_p1:
        st.write("**PROGRAM:**")
        st.write(plan)
    with col_p2:
        st.write("**CENNIK:**")
        st.table({
            "Konfiguracja": ["Grupa 1", "Grupa 2", "Grupa 3"],
            "Cena": [c_opcja1, c_opcja2, c_opcja3]
        })

# --- PRZYCISK POBIERANIA ---
if st.button("🚀 Generuj gotowy dokument PDF"):
    st.success("Twoja oferta jest gotowa! Użyj skrótu Ctrl+P (lub Cmd+P), aby zapisać ten widok jako PDF. Dzięki temu zachowasz kolory i zdjęcia biura Travis.")
