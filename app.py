import streamlit as st
from fpdf import FPDF
import base64

# Konfiguracja stylu TRAVIS
st.set_page_config(page_title="Generator TRAVIS", page_icon="✈️")

def create_pdf(tytul, termin, program, ceny, logo_file, foto_file):
    pdf = FPDF()
    pdf.add_page()
    # Biblioteka fpdf wymaga czcionek unicode do polskich znaków, używamy standardowej dla uproszczenia
    pdf.set_font("Arial", size=12)

    # Nagłówek
    pdf.cell(200, 10, txt="TRAVIS BIURO PODRÓŻY - OFERTA", ln=True, align='C')
    pdf.ln(10)

    # Treść
    pdf.cell(200, 10, txt=f"Kierunek: {tytul}", ln=True)
    pdf.cell(200, 10, txt=f"Termin: {termin}", ln=True)
    pdf.ln(5)
    
    pdf.multi_cell(0, 10, txt=f"Program:\n{program}")
    pdf.ln(5)
    
    pdf.cell(200, 10, txt="Cennik:", ln=True)
    for k, v in ceny.items():
        pdf.cell(200, 10, txt=f"{k}: {v}", ln=True)
        
    return pdf.output(dest="S").encode("latin-1", errors="ignore")

st.title("📸 Kreator Ofert TRAVIS")

# PANEL BOCZNY - Personalizacja
with st.sidebar:
    st.header("🖼️ Wygląd")
    logo = st.file_uploader("Wgraj LOGO biura", type=['png', 'jpg'])
    foto = st.file_uploader("Wgraj ZDJĘCIE główne", type=['png', 'jpg'])
    
    st.header("📝 Dane")
    u_tytul = st.text_input("Tytuł", "MALTA 4 DNI")
    u_termin = st.text_input("Termin", "27 czerwca - 1 lipca")
    u_c1 = st.text_input("Cena (46-50 os.)", "3 395,00 zł")
    u_c2 = st.text_input("Cena (40-45 os.)", "3 470,00 zł")

# PODGLĄD W APLIKACJI
col1, col2 = st.columns([1, 2])
with col1:
    if logo: st.image(logo, width=150)
    else: st.warning("Brak logo")
with col2:
    if foto: st.image(foto, use_container_width=True)
    else: st.info("Tutaj pojawi się zdjęcie główne")

st.markdown("---")

# EDYCJA TREŚCI (Domyślnie z Twojego PDF)
program_input = st.text_area("Program wycieczki", value=(
    "Dzień 1: Wyjazd z Olsztyna, przylot na Maltę. [cite: 7]\n"
    "Dzień 2: Valletta (Katedra św. Jana), Mdina i Rotunda w Moście. [cite: 12, 17, 19]\n"
    "Dzień 3: Całodniowa wycieczka na Gozo i Victoria. [cite: 22, 24]\n"
    "Dzień 4: Błękitna Grota, Klify Dingli i powrót. [cite: 36, 39, 41]"
), height=200)

if st.button("📥 Generuj PDF"):
    try:
        pdf_res = create_pdf(u_tytul, u_termin, program_input, {"46-50 os.": u_c1, "40-45 os.": u_c2}, logo, foto)
        st.success("PDF wygenerowany! Użyj opcji drukowania w przeglądarce (Ctrl+P), aby zapisać z grafikami.")
    except Exception as e:
        st.error(f"Błąd generowania: {e}")

st.caption("Travis Biuro Podróży | tel: 789 563 405 [cite: 26]")
