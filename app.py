import streamlit as st
from fpdf import FPDF
import base64

# Konfiguracja strony
st.set_page_config(page_title="Generator Travis", page_icon="✈️")

# --- FUNKCJA GENEROWANIA PDF ---
def create_pdf(tytul, termin, program, ceny, logo_file, foto_file):
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font('DejaVu', '', 'https://github.com/reingart/pyfpdf/raw/master/font/DejaVuSans.ttf', uni=True)
    pdf.set_font('DejaVu', '', 14)

    # Logo biura
    if logo_file:
        with open("temp_logo.png", "wb") as f:
            f.write(logo_file.getbuffer())
        pdf.image("temp_logo.png", 10, 8, 33)
    
    pdf.cell(200, 10, "TRAVIS BIURO PODRÓŻY", ln=True, align='C')
    pdf.ln(10)

    # Zdjęcie główne
    if foto_file:
        with open("temp_foto.png", "wb") as f:
            f.write(foto_file.getbuffer())
        pdf.image("temp_foto.png", x=10, y=40, w=190)
        pdf.ln(100)

    # Treść oferty
    pdf.set_font('DejaVu', '', 18)
    pdf.cell(200, 10, tytul.upper(), ln=True, align='C')
    pdf.set_font('DejaVu', '', 12)
    pdf.cell(200, 10, f"Termin: {termin}", ln=True, align='C')
    pdf.ln(5)

    pdf.multi_cell(0, 10, f"Program wycieczki:\n{program}")
    pdf.ln(5)
    
    pdf.cell(200, 10, "Cennik:", ln=True)
    for k, v in ceny.items():
        pdf.cell(200, 10, f"- {k}: {v} zł", ln=True)

    return pdf.output(dest="S").encode("latin-1", errors="ignore")

# --- INTERFEJS APLIKACJI ---
st.title("📸 Personalizowany Kreator Travis")

with st.sidebar:
    st.header("🖼️ Multimedia")
    logo = st.file_uploader("Wgraj LOGO biura", type=['png', 'jpg'])
    foto = st.file_uploader("Wgraj ZDJĘCIE główne wycieczki", type=['png', 'jpg'])
    
    st.header("✍️ Dane oferty")
    tytul = st.text_input("Tytuł", "MALTA 4 DNI [cite: 3]")
    termin = st.text_input("Termin", "27 czerwca - 1 lipca [cite: 6]")
    c1 = st.text_input("Cena (46-50 osób)", "3 395,00 ")
    c2 = st.text_input("Cena (40-45 osób)", "3 470,00 ")

# Wyświetlanie podglądu zdjęć
col1, col2 = st.columns(2)
with col1:
    if logo:
        st.image(logo, caption="Twoje Logo", width=150)
with col2:
    if foto:
        st.image(foto, caption="Zdjęcie wycieczki", use_container_width=True)

st.markdown("---")
program_tekst = st.text_area("Edytuj program dnia po dniu", 
    "Dzień 1: Zbiórka w Olsztynie, przylot na Maltę. [cite: 7]\n"
    "Dzień 2: Zwiedzanie Valletty, Mdiny i Mosty. [cite: 12, 17, 19]\n"
    "Dzień 3: Rejs na Gozo, Victoria i solniska. [cite: 22, 24, 32]\n"
    "Dzień 4: Błękitna Grota i powrót do Polski. [cite: 36, 41]")

ceny_dict = {"46-50 osób": c1, "40-45 osób": c2}

# --- POBIERANIE ---
if st.button("🚀 Generuj i Pobierz Ofertę PDF"):
    pdf_data = create_pdf(tytul, termin, program_tekst, ceny_dict, logo, foto)
    b64 = base64.b64encode(pdf_data).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="Oferta_Travis.pdf">Kliknij tutaj, aby pobrać plik PDF</a>'
    st.markdown(href, unsafe_allow_html=True)
