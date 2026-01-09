import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from io import BytesIO
from PIL import Image as PILImage # do obróbki zdjęć

# Konfiguracja strony Streamlit
st.set_page_config(page_title="TRAVIS Kreator PDF", page_icon="✈️", layout="wide")

# --- STYLE GRAFICZNE TRAVIS ---
# Główne kolory Travis: Granat (#002d5a), Jasnoszary (#f0f2f6)
TRAVIS_BLUE = colors.HexColor("#002d5a")
TRAVIS_LIGHT_GREY = colors.HexColor("#f0f2f6")

# Globalne style
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='TravisTitle', fontName='Helvetica-Bold', fontSize=24, leading=28, alignment=1, textColor=TRAVIS_BLUE))
styles.add(ParagraphStyle(name='TravisSubtitle', fontName='Helvetica', fontSize=14, leading=16, alignment=1, textColor=TRAVIS_BLUE))
styles.add(ParagraphStyle(name='TravisHeader', fontName='Helvetica-Bold', fontSize=16, leading=18, textColor=TRAVIS_BLUE, spaceAfter=8))
styles.add(ParagraphStyle(name='TravisNormal', fontName='Helvetica', fontSize=12, leading=14, textColor=colors.black, spaceAfter=4))
styles.add(ParagraphStyle(name='TravisIncludes', fontName='Helvetica', fontSize=12, leading=14, textColor=colors.HexColor("#28a745"), spaceAfter=4)) # Zielony
styles.add(ParagraphStyle(name='TravisExcludes', fontName='Helvetica', fontSize=12, leading=14, textColor=colors.HexColor("#dc3545"), spaceAfter=4)) # Czerwony
styles.add(ParagraphStyle(name='TravisFooter', fontName='Helvetica', fontSize=9, leading=11, alignment=1, textColor=TRAVIS_BLUE))

# --- GENERATOR PDF ---
def generate_travis_pdf(tytul, termin, plan, ceny_raw, zawiera, nie_zawiera, foto_buffer, tel, email):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    story = []

    # Logo Travis na górze dokumentu (wbudowane, nie jako header ReportLab)
    travis_logo_path = "https://travis.pl/wp-content/uploads/2025/07/logo_travis500.png"
    logo_img = Image(travis_logo_path, width=1.5*inch, height=0.5*inch)
    logo_img.hAlign = 'CENTER'
    story.append(logo_img)
    story.append(Spacer(1, 0.2*inch))

    # Zdjęcie główne (jeśli wgrane)
    if foto_buffer:
        img_pil = PILImage.open(foto_buffer)
        aspect_ratio = img_pil.width / img_pil.height
        img_width = 5.5 * inch # Ustalona szerokość
        img_height = img_width / aspect_ratio
        
        img = Image(foto_buffer, width=img_width, height=img_height)
        img.hAlign = 'CENTER'
        story.append(img)
        story.append(Spacer(1, 0.2*inch))

    # Tytuł oferty
    story.append(Paragraph(tytul, styles['TravisTitle']))
    story.append(Paragraph(f"Termin: {termin}", styles['TravisSubtitle']))
    story.append(Spacer(1, 0.4*inch))

    # Plan wycieczki
    story.append(Paragraph("PLAN PODROZY:", styles['TravisHeader']))
    for line in plan.split('\n'):
        if line.strip():
            story.append(Paragraph(line, styles['TravisNormal']))
    story.append(Spacer(1, 0.2*inch))

    # Cennik (tabela)
    ceny_data = [['Konfiguracja grupy', 'Cena za osobę']]
    for line in ceny_raw.split('\n'):
        if '|' in line:
            ceny_data.append([item.strip() for item in line.split('|')])
        elif line.strip():
            ceny_data.append([line.strip(), '']) # Umożliwia wpisanie linii bez '|'
    
    if len(ceny_data) > 1:
        ceny_table = Table(ceny_data, colWidths=[2.5*inch, 3*inch])
        ceny_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), TRAVIS_BLUE),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.white),
            ('GRID', (0,0), (-1,-1), 1, TRAVIS_BLUE),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(Paragraph("CENNIK:", styles['TravisHeader']))
        story.append(ceny_table)
        story.append(Spacer(1, 0.2*inch))

    # Cena zawiera / nie zawiera (dwie kolumny)
    includes_list = [Paragraph(f"• {line.strip()}", styles['TravisIncludes']) for line in zawiera.split('\n') if line.strip()]
    excludes_list = [Paragraph(f"• {line.strip()}", styles['TravisExcludes']) for line in nie_zawiera.split('\n') if line.strip()]

    data_details = [
        [Paragraph("CENA ZAWIERA:", styles['TravisHeader']), Paragraph("CENA NIE ZAWIERA:", styles['TravisHeader'])]
    ]
    
    max_rows = max(len(includes_list), len(excludes_list))
    for i in range(max_rows):
        row = []
        row.append(includes_list[i] if i < len(includes_list) else Paragraph("", styles['TravisNormal']))
        row.append(excludes_list[i] if i < len(excludes_list) else Paragraph("", styles['TravisNormal']))
        data_details.append(row)

    details_table = Table(data_details, colWidths=[2.75*inch, 2.75*inch])
    details_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('SPAN', (0,0), (0,0)), # Rozciągnij nagłówki
        ('SPAN', (1,0), (1,0)),
    ]))
    story.append(details_table)
    story.append(Spacer(1, 0.5*inch))

    # Stopka jako element na końcu dokumentu (nie jako footer ReportLab)
    footer_text = f"Biuro Podrozy TRAVIS | tel: {tel} | e-mail: {email}\nwpis do Rejestru Organizatorów i Posredników Turystycznych pod numerem 41059"
    story.append(Paragraph(footer_text, styles['TravisFooter']))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# --- INTERFEJS STREAMLIT ---
st.title("✨ Nowoczesny Generator Ofert TRAVIS (PDF)")

with st.sidebar:
    st.header("🖼️ Dane Kontaktowe i Zdjęcia")
    u_tel = st.text_input("Telefon biura", value="789 563 405")
    u_mail = st.text_input("E-mail biura", value="biuro@travis.pl")
    st.markdown("---")
    foto_glowne_upload = st.file_uploader("Wgraj zdjęcie główne (do PDF)", type=['jpg', 'png'])

col1, col2 = st.columns(2)
with col1:
    tytul = st.text_input("Tytuł wycieczki", placeholder="np. MALTA 4 DNI - City Break")
    termin = st.text_input("Termin wyjazdu", placeholder="np. 27.06 - 01.07.2026")
with col2:
    st.write("**💰 Konfiguracje cenowe (jedna na linię)**")
    ceny_input = st.text_area("np. 46-50 os. | 3 395 zł\n40-45 os. | 3 470 zł", height=100)

st.markdown("### 🗺️ Plan podróży")
plan_input = st.text_area("Wpisz plan dnia po dniu", height=250, placeholder="DZIEŃ 1: ...\nDZIEŃ 2: ...")

col_det1, col_det2 = st.columns(2)
with col_det1:
    zawiera_input = st.text_area("✅ Cena zawiera:", height=150, placeholder="- Przejazdy autokarem\n- Noclegi...")
with col_det2:
    nie_zawiera_input = st.text_area("❌ Cena nie zawiera:", height=150, placeholder="- Bilety wstępu (ok. 130 EUR)\n- Wydatki własne...")

st.markdown("---")

if st.button("🚀 GENERUJ PROFESJONALNY PLIK PDF"):
    if not (tytul and termin and plan_input and ceny_input and zawiera_input and nie_zawiera_input):
        st.error("Wypełnij wszystkie pola, aby wygenerować ofertę!")
    else:
        pdf_buffer = generate_travis_pdf(tytul, termin, plan_input, ceny_input, zawiera_input, nie_zawiera_input, foto_glowne_upload, u_tel, u_mail)
        
        st.download_button(
            label="📥 POBIERZ OFERTĘ PDF",
            data=pdf_buffer,
            file_name=f"Oferta_Travis_{tytul.replace(' ', '_')}.pdf",
            mime="application/pdf",
            type="primary"
        )
        st.success("PDF został wygenerowany i jest gotowy do pobrania!")

# Brak stopki w Streamlit, bo jest w PDF
