import streamlit as st

# Konfiguracja strony - stylistyka Travis (Granat: #002d5a)
st.set_page_config(page_title="Kreator Ofert TRAVIS", page_icon="✈️", layout="wide")

# CSS dla zachowania kolorystyki logo i stałej stopki
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    h1, h2, h3 { color: #002d5a; font-family: 'Arial'; border-left: 5px solid #002d5a; padding-left: 15px; }
    .stButton>button { 
        background-color: #002d5a; color: white; border-radius: 0px; border: none; font-weight: bold; width: 100%;
    }
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: white;
        color: #002d5a;
        text-align: center;
        padding: 10px;
        border-top: 1px solid #002d5a;
        font-size: 12px;
        z-index: 999;
    }
    @media print {
        .no-print { display: none !important; }
        .footer { position: fixed; bottom: 0; }
    }
    </style>
    """, unsafe_allow_html=True)

# Nagłówek z logo
LOGO_URL = "https://travis.pl/wp-content/uploads/2025/07/logo_travis500.png"
st.image(LOGO_URL, width=220)

st.title("PROFESJONALNY KREATOR OFERT")

# --- PANEL BOCZNY (SIDEBAR) ---
with st.sidebar:
    st.header("🖼️ Multimedia i Kontakt")
    foto_glowne = st.file_uploader("Wgraj zdjęcie główne", type=['jpg', 'png'], key="main_foto")
    galeria = st.file_uploader("Dodatkowa galeria zdjęć (wiele plików)", type=['jpg', 'png'], accept_multiple_files=True)
    
    st.markdown("---")
    u_tel = st.text_input("Telefon biura", value="789 563 405")
    u_mail = st.text_input("E-mail biura", value="biuro@travis.pl")

# --- FORMULARZ GŁÓWNY ---
col1, col2 = st.columns([2, 1])

with col1:
    tytul = st.text_input("Kierunek / Tytuł oferty", placeholder="np. MALTA 4 DNI - City Break")
    termin = st.text_input("Termin wycieczki", placeholder="np. 27 czerwca - 1 lipca 2026")
    plan = st.text_area("Plan wycieczki (Dzień po dniu)", height=300, placeholder="DZIEŃ 1: ...\nDZIEŃ 2: ...")

with col2:
    st.write("**💰 Konfiguracje cenowe**")
    c1 = st.text_input("Grupa 1 (np. 46-50 os.)", placeholder="3 395,00 zł")
    c2 = st.text_input("Grupa 2 (np. 40-45 os.)", placeholder="3 470,00 zł")
    c3 = st.text_input("Grupa 3 (np. 35-39 os.)", placeholder="3 545,00 zł")

st.markdown("---")

col_a, col_b = st.columns(2)
with col_a:
    zawiera = st.text_area("✅ Cena zawiera:", height=200, placeholder="- Transfery\n- Noclegi\n- Wyżywienie...")
with col_b:
    nie_zawiera = st.text_area("❌ Cena nie zawiera:", height=200, placeholder="- Bilety wstępu (ok. 130 EUR)\n- Wydatki własne...")

# --- SEKCJA PODGLĄDU ---
st.markdown("### 👁️ Podgląd dokumentu")

if foto_glowne:
    st.image(foto_glowne, use_container_width=True)

st.header(tytul)
st.subheader(f"📅 {termin}")

st.write("**PROGRAM PODRÓŻY:**")
st.write(plan)

# Tabela cenowa
st.table({
    "Wielkość grupy": ["Największa", "Średnia", "Najmniejsza"],
    "Cena za osobę": [c1, c2, c3]
})

# Galeria zdjęć na dole
if galeria:
    st.markdown("### 📸 Galeria zdjęć")
    cols = st.columns(3)
    for idx, img in enumerate(galeria):
        cols[idx % 3].image(img, use_container_width=True)

# --- ZASZYTA STOPKA ---
st.markdown(f"""
    <div class="footer">
        <p>Biuro Podróży TRAVIS | tel: {u_tel} | e-mail: {u_mail}<br>
        <b>wpis do Rejestru Organizatorów i Pośredników Turystycznych pod numerem 41059</b></p>
    </div>
    """, unsafe_allow_html=True)

# Przycisk pomocniczy
if st.button("🖨️ PRZYGOTUJ DO WYDRUKU PDF"):
    st.info("💡 Instrukcja: Naciśnij Ctrl+P. W oknie drukowania wybierz 'Zapisz jako PDF'.")
