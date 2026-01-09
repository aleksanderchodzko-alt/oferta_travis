import streamlit as st
from fpdf import FPDF
import base64

# Konfiguracja strony - kolory Travis (Granat: #002d5a)
st.set_page_config(page_title="Generator TRAVIS", page_icon="✈️", layout="wide")

# Custom CSS - tylko kolory z logo (Granat i Biel)
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    .stButton>button { 
        background-color: #002d5a; 
        color: white; 
        border-radius: 0px; 
        border: none;
        height: 3em;
        font-weight: bold;
    }
    .stButton>button:hover { background-color: #004080; color: white; }
    h1, h2, h3 { color: #002d5a; font-family: 'Arial'; border-left: 5px solid #002d5a; padding-left: 15px; }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea { border-color: #002d5a; }
    .stTable { border: 1px solid #002d5a; }
    </style>
    """, unsafe_allow_html=True)

# Logo Travis
LOGO_URL = "https://travis.pl/wp-content/uploads/2025/07/logo_travis500.png"
st.image(LOGO_URL, width=220)

st.title("GENERATOR OFERT")

# --- PANEL BOCZNY ---
with st.sidebar:
    st.header("🖼️ Multimedia")
    foto_glowne = st.file_uploader("Wgraj zdjęcie główne (format poziomy najlepiej)", type=['jpg', 'png'])
    st.markdown("---")
    st.write("📩 **Kontakt w stopce:**")
    st.write("789 563 405 | biuro@travis.pl")

# --- FORMULARZ ---
col_head1, col_head2 = st.columns([2, 1])

with col_head1:
    tytul = st.text_input("Kierunek / Nazwa wycieczki", placeholder="np. MALTA - PERŁA MEDYTACJI")
    termin = st.text_input("Termin wyjazdu", placeholder="np. 27.06 - 01.07.2026")

with col_head2:
    st.write("**💰 Wycena grupy**")
    c1 = st.text_input("Opcja 1 (Liczba osób | Cena)", placeholder="46-50 os. | 3 395 zł")
    c2 = st.text_input("Opcja 2 (Liczba osób | Cena)", placeholder="40-45 os. | 3 470 zł")
    c3 = st.text_input("Opcja 3 (Liczba osób | Cena)", placeholder="35-39 os. | 3 545 zł")

st.markdown("### 🗺️ Plan podróży")
plan = st.text_area("Wpisz szczegółowy plan (ładnie sformatowany)", height=300, 
                    placeholder="DZIEŃ 1:\n...\n\nDZIEŃ 2:\n...")

col_details1, col_details2 = st.columns(2)
with col_details1:
    st.markdown("### ✅ Cena zawiera")
    zawiera = st.text_area("Lista świadczeń", height=180, placeholder="- Przejazd autokarem...\n- Noclegi...")

with col_details2:
    st.markdown("### ❌ Cena nie zawiera")
    nie_zawiera = st.text_area("Koszty dodatkowe", height=180, placeholder="- Bilety wstępu i przewodnicy (ok. 130 EUR)...")

# --- STOPKA KONTAKTOWA ---
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #002d5a; font-weight: bold;'>"
    "Biuro Podróży TRAVIS | tel: 789 563 405 | e-mail: biuro@travis.pl <br>"
    "Wpis do Rejestru Organizatorów Turystycznych nr 41059"
    "</div>", 
    unsafe_allow_html=True
)

# --- PODGLĄD I GENEROWANIE ---
if st.checkbox("Pokaż podgląd dokumentu"):
    if foto_glowne:
        st.image(foto_glowne, use_container_width=True)
    st.header(tytul)
    st.write(f"📅 **TERMIN:** {termin}")
    st.write(plan)
    
    st.table({
        "Konfiguracja grupy": ["Opcja I", "Opcja II", "Opcja III"],
        "Szczegóły i Cena": [c1, c2, c3]
    })

if st.button("💾 PRZYGOTUJ DO DRUKU (PDF)"):
    st.info("💡 INSTRUKCJA: Po kliknięciu przycisku naciśnij **Ctrl + P** (lub Cmd + P na Macu). \n"
             "W ustawieniach drukowania wybierz **'Zapisz jako PDF'** oraz zaznacz opcję **'Grafika tła'**, aby zachować kolory Travis.")
