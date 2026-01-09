import streamlit as st
from fpdf import FPDF
import base64

# Konfiguracja strony
st.set_page_config(page_title="Generator TRAVIS", page_icon="✈️")

# --- KLASA GENERUJĄCA PDF ---
class TravisPDF(FPDF):
    def header(self):
        # Logo Travis na każdej stronie
        self.image("https://travis.pl/wp-content/uploads/2025/07/logo_travis500.png", 10, 8, 40)
        self.set_font('Arial', 'B', 15)
        self.set_text_color(0, 45, 90) # Granat Travis
        self.cell(80)
        self.cell(30, 10, 'OFERTA BIURA PODROZY TRAVIS', 0, 0, 'C')
        self.ln(20)

    def footer(self):
        # Stała stopka na każdej stronie
        self.set_y(-25)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(0, 45, 90)
        self.cell(0, 5, f'Biuro Podrozy TRAVIS | tel: {st.session_state.tel} | e-mail: {st.session_state.mail}', 0, 1, 'C')
        self.set_font('Arial', 'B', 8)
        self.cell(0, 5, 'wpis do Rejestru Organizatorów i Posredników Turystycznych pod numerem 41059', 0, 0, 'C')

# --- INTERFEJS ---
st.title("🚀 Generator PDF Travis")

with st.sidebar:
    st.header("⚙️ Ustawienia")
    st.session_state.tel = st.text_input("Telefon", value="789 563 405")
    st.session_state.mail = st.text_input("E-mail", value="biuro@travis.pl")
    st.markdown("---")
    foto_glowne = st.file_uploader("Wgraj zdjęcie główne (do PDF)", type=['jpg', 'png'])

col1, col2 = st.columns(2)
with col1:
    tytul = st.text_input("Nazwa wycieczki", "MALTA 4 DNI")
    termin = st.text_input("Termin", "27.06 - 01.07.2026")
with col2:
    ceny = st.text_area("Wyceny (każda w nowej linii)", "46-50 os. | 3 395 zł\n40-45 os. | 3 470 zł")

plan = st.text_area("Plan wycieczki", height=200)
zawiera = st.text_area("Cena zawiera", height=100)
nie_zawiera = st.text_area("Cena nie zawiera", height=100)

# --- LOGIKA GENEROWANIA ---
if st.button("🔥 GENERUJ GOTOWY PLIK PDF"):
    pdf = TravisPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=30)
    
    # Nagłówek i Tytuł
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, tytul.encode('latin-1', 'ignore').decode('latin-1'), ln=True)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f"Termin: {termin}".encode('latin-1', 'ignore').decode('latin-1'), ln=True)
    pdf.ln(5)

    # Zdjęcie (jeśli wgrane)
    if foto_glowne:
        with open("temp_img.png", "wb") as f:
            f.write(foto_glowne.getbuffer())
        pdf.image("temp_img.png", x=10, w=180)
        pdf.ln(5)

    # Program
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, "PROGRAM:", ln=True)
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 7, plan.encode('latin-1', 'ignore').decode('latin-1'))
    pdf.ln(5)

    # Ceny
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, "CENNIK:", ln=True)
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 7, ceny.encode('latin-1', 'ignore').decode('latin-1'))
    pdf.ln(5)

    # Świadczenia
    pdf.set_font('Arial', 'B', 11)
    pdf.set_text_color(0, 100, 0) # Zielony dla "Zawiera"
    pdf.cell(0, 10, "CENA ZAWIERA:", ln=True)
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 6, zawiera.encode('latin-1', 'ignore').decode('latin-1'))
    
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 11)
    pdf.set_text_color(150, 0, 0) # Czerwony dla "Nie zawiera"
    pdf.cell(0, 10, "CENA NIE ZAWIERA:", ln=True)
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 6, nie_zawiera.encode('latin-1', 'ignore').decode('latin-1'))

    # Konwersja do pobrania
    pdf_output = pdf.output(dest='S').encode('latin-1', 'ignore')
    b64 = base64.b64encode(pdf_output).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="Oferta_Travis_{tytul}.pdf" style="text-decoration: none; padding: 10px 20px; background-color: #002d5a; color: white; border-radius: 5px;">📥 KLIKNIJ TUTAJ ABY POBRAĆ PDF</a>'
    st.markdown(href, unsafe_allow_html=True)
