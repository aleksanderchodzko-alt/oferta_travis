import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageTemplate, Frame
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
import requests

# --- KONFIGURACJA CZCIONKI ---
@st.cache_data
def setup_fonts():
    try:
        url = "https://github.com/google/fonts/raw/main/ofl/opensans/OpenSans%5Bwdth%2Cwght%5D.ttf"
        res = requests.get(url)
        pdfmetrics.registerFont(TTFont('Standard', BytesIO(res.content)))
        return 'Standard'
    except:
        return 'Helvetica'

FONT_NAME = setup_fonts()

# --- KOLORY FIRMOWE ---
NAVY = colors.HexColor("#002d5a")
BG_LIGHT = colors.HexColor("#f5f7f9")
TEXT_BLACK = colors.HexColor("#121212")
WHITE = colors.white

# --- NAGŁÓWEK I STOPKA (POWTARZALNE NA KAŻDEJ STRONIE) ---
def my_page_layout(canvas, doc):
    canvas.saveState()
    
    # 1. Tło strony
    canvas.setFillColor(BG_LIGHT)
    canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
    
    # 2. LOGO NA ŚRODKU (Nagłówek każdej strony)
    logo_url = "https://travis.pl/wp-content/uploads/2025/07/logo_travis500.png"
    try:
        # Pobieramy logo do rysowania bezpośrednio na canvasie
        logo_data = BytesIO(requests.get(logo_url).content)
        canvas.drawImage(Image(logo_data).filename, (A4[0]-8.5*cm)/2, A4[1]-3*cm, width=8.5*cm, preserveAspectRatio=True, mask='auto')
    except:
        pass

    # 3. Fala na dole
    canvas.setFillColor(NAVY)
    path = canvas.beginPath()
    path.moveTo(0, 0)
    path.lineTo(A4[0], 0)
    path.lineTo(A4[0], 2*cm)
    path.curveTo(A4[0]*0.7, 1*cm, A4[0]*0.3, 3*cm, 0, 1.5*cm)
    path.close()
    canvas.drawPath(path, fill=1, stroke=0)
    
    # 4. Stopka (Tekst na fali)
    canvas.setFillColor(WHITE)
    canvas.setFont(FONT_NAME, 7)
    u_tel = st.session_state.get('tel', '789 563 405')
    u_mail = st.session_state.get('mail', 'biuro@travis.pl')
    canvas.drawCentredString(A4[0]/2, 1*cm, f"Biuro Podróży TRAVIS | tel: {u_tel} | e-mail: {u_mail} | Rejestr nr 41059")
    
    canvas.restoreState()

def generate_pdf(tytul, termin, plan, ceny, zawiera, foto_main, galeria):
    buffer = BytesIO()
    # Zwiększony topMargin, aby treść nie nachodziła na logo w nagłówku
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=1.5*cm, rightMargin=1.5*cm, topMargin=3.5*cm, bottomMargin=3*cm)
    
    style_title = ParagraphStyle('T', fontName=FONT_NAME, fontSize=22, textColor=NAVY, alignment=1)
    style_term = ParagraphStyle('S', fontName=FONT_NAME, fontSize=11, textColor=TEXT_BLACK, alignment=1)
    style_h = ParagraphStyle('H', fontName=FONT_NAME, fontSize=10, textColor=NAVY, spaceAfter=6, borderLeftWidth=2, borderLeftColor=NAVY, leftIndent=5)
    style_p = ParagraphStyle('P', fontName=FONT_NAME, fontSize=9, leading=12, textColor=TEXT_BLACK)
    
    story = []
    
    # 1. TYTUŁ I TERMIN
    story.append(Paragraph(tytul.upper(), style_title))
    story.append(Spacer(1, 10))
    story.append(Paragraph(f"📅 TERMIN: {termin}", style_term))
    story.append(Spacer(1, 20))

    # 2. ZDJĘCIE GŁÓWNE
    if foto_main:
        img = Image(foto_main, width=17*cm, height=7*cm, kind='proportional')
        img.hAlign = 'CENTER'
        story.append(img)
        story.append(Spacer(1, 25))

    # FUNKCJA KARTY (Zaokrąglenie 5pt)
    def create_card(content_para, width=17.5*cm):
        t = Table([[content_para]], colWidths=[width])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), WHITE),
            ('ROUNDEDCORNERS', [5, 5, 5, 5]),
            ('LEFTPADDING', (0,0), (-1,-1), 15),
            ('TOPPADDING', (0,0), (-1,-1), 12),
            ('BOTTOMPADDING', (0,0), (-1,-1), 12),
        ]))
        return t

    # 3. PROGRAM
    story.append(Paragraph("✈️ PROGRAM WYCIECZKI", style_h))
    story.append(create_card(Paragraph(plan.replace('\n', '<br/>'), style_p)))
    story.append(Spacer(1, 15))

    # 4. KOSZTY I ŚWIADCZENIA
    c1 = [Paragraph("💰 KOSZTY", style_h), Paragraph(ceny.replace('\n', '<br/>'), style_p)]
    c2 = [Paragraph("📋 ŚWIADCZENIA", style_h), Paragraph(zawiera.replace('\n', '<br/>'), style_p)]
    
    t_side = Table([
        [Table([[c1]], colWidths=[8.3*cm], style=[('BACKGROUND', (0,0), (-1,-1), WHITE), ('ROUNDEDCORNERS', [5,5,5,5])]),
         Table([[c2]], colWidths=[8.3*cm], style=[('BACKGROUND', (0,0), (-1,-1), WHITE), ('ROUNDEDCORNERS', [5,5,5,5])])]
    ], colWidths=[8.7*cm, 8.7*cm])
    t_side.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('LEFTPADDING', (0,0), (-1,-1), 0)]))
    story.append(t_side)

    # 5. GALERIA
    if galeria:
        story.append(Spacer(1, 20))
        story.append(Paragraph("📸 GALERIA", style_h))
        row, g_data = [], []
        for i, f in enumerate(galeria):
            img = Image(f, width=5.5*cm, height=3.5*cm, kind='proportional')
            row.append(img)
            if (i + 1) % 3 == 0:
                g_data.append(row)
                row = []
        if row: g_data.append(row)
        story.append(Table(g_data, colWidths=[5.8*cm]*3))

    # REJESTRACJA SZABLONU STRONY
    doc.addPageTemplates([PageTemplate(id='Travis', frames=Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height), onPage=my_page_layout)])
    doc.build(story)
    return buffer.getvalue()

# --- INTERFEJS STREAMLIT ---
st.set_page_config(page_title="Travis Designer", page_icon="✈️")
st.title("🌊 Travis Designer Premium")

with st.sidebar:
    st.header("Kontakt")
    st.session_state['tel'] = st.text_input("Telefon", "789 563 405")
    st.session_state['mail'] = st.text_input("E-mail", "biuro@travis.pl")
    f_main = st.file_uploader("Zdjęcie główne", type=['jpg','png'])
    f_gal = st.file_uploader("Galeria", type=['jpg','png'], accept_multiple_files=True)

u_t = st.text_input("Tytuł")
u_d = st.text_input("Termin")
u_p = st.text_area("Program (Dzień po dniu)", height=250)
col1, col2 = st.columns(2)
with col1: u_c = st.text_area("Koszt", height=120)
with col2: u_s = st.text_area("Świadczenia", height=120)

if st.button("🚀 GENERUJ PDF"):
    if u_t:
        try:
            pdf_out = generate_pdf(u_t, u_d, u_p, u_c, u_s, f_main, f_gal)
            st.download_button("📥 POBIERZ OFERTĘ", data=pdf_out, file_name=f"Oferta_Travis_{u_t}.pdf", mime="application/pdf")
        except Exception as e:
            st.error(f"Błąd: {e}")
    else:
        st.warning("Podaj tytuł!")
