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

# --- KONFIGURACJA CZCIONKI (POLSKIE ZNAKI) ---
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

# --- KOLORY ---
NAVY = colors.HexColor("#002d5a")
BG_LIGHT = colors.HexColor("#f5f7f9")
TEXT_BLACK = colors.HexColor("#121212")
WHITE = colors.white

# --- ELEGANCKA RAMKA DLA ZDJĘĆ (DOPASOWANA) ---
def create_bordered_image(img_file, width, height):
    try:
        img = Image(img_file, width=width, height=height, kind='proportional')
        # Bardzo mały margines (0.1cm), żeby zdjęcie wypełniało ramkę
        t = Table([[img]], colWidths=[width + 0.2*cm], rowHeights=[height + 0.2*cm])
        t.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOX', (0,0), (-1,-1), 0.5, NAVY),
            ('LEFTPADDING', (0,0), (-1,-1), 2),
            ('RIGHTPADDING', (0,0), (-1,-1), 2),
            ('TOPPADDING', (0,0), (-1,-1), 2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
            ('BACKGROUND', (0,0), (-1,-1), WHITE),
        ]))
        return t
    except:
        return Paragraph("Błąd zdjęcia", getSampleStyleSheet()['Normal'])

# --- SZABLON STRONY (LOGO, STOPKA, FALKI) ---
def my_page_layout(canvas, doc):
    canvas.saveState()
    
    # 1. Tło
    canvas.setFillColor(BG_LIGHT)
    canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
    
    # 2. Górna fala (Subtelna)
    canvas.setFillColor(NAVY)
    canvas.setStrokeColor(NAVY)
    p_top = canvas.beginPath()
    p_top.moveTo(0, A4[1])
    p_top.lineTo(A4[0], A4[1])
    p_top.lineTo(A4[0], A4[1]-0.8*cm)
    p_top.curveTo(A4[0]*0.7, A4[1]-1.5*cm, A4[0]*0.3, A4[1]-0.2*cm, 0, A4[1]-1*cm)
    p_top.close()
    canvas.drawPath(p_top, fill=1, stroke=0)

    # 3. LOGO (Pobierane bezpośrednio do rysowania)
    logo_url = "https://travis.pl/wp-content/uploads/2025/07/logo_travis500.png"
    try:
        logo_res = requests.get(logo_url)
        logo_data = BytesIO(logo_res.content)
        canvas.drawImage(Image(logo_data).filename, (A4[0]-7*cm)/2, A4[1]-3.2*cm, width=7*cm, preserveAspectRatio=True, mask='auto')
    except:
        pass

    # 4. Dolna fala
    canvas.setFillColor(NAVY)
    p_bot = canvas.beginPath()
    p_bot.moveTo(0, 0)
    p_bot.lineTo(A4[0], 0)
    p_bot.lineTo(A4[0], 2.2*cm)
    p_bot.curveTo(A4[0]*0.7, 1.2*cm, A4[0]*0.3, 3.2*cm, 0, 1.7*cm)
    p_bot.close()
    canvas.drawPath(p_bot, fill=1, stroke=0)
    
    # 5. Stopka
    canvas.setFillColor(WHITE)
    canvas.setFont(FONT_NAME, 7)
    u_tel = st.session_state.get('tel', '789 563 405')
    u_mail = st.session_state.get('mail', 'biuro@travis.pl')
    canvas.drawCentredString(A4[0]/2, 1.1*cm, f"Biuro Podróży TRAVIS | tel: {u_tel} | e-mail: {u_mail} | Rejestr nr 41059")
    
    canvas.restoreState()

def generate_pdf(tytul, termin, plan, ceny, zawiera, foto_main, galeria):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=1.5*cm, rightMargin=1.5*cm, topMargin=4.5*cm, bottomMargin=3.5*cm)
    
    styles = getSampleStyleSheet()
    style_title = ParagraphStyle('T', fontName=FONT_NAME, fontSize=20, textColor=NAVY, alignment=1)
    style_term = ParagraphStyle('S', fontName=FONT_NAME, fontSize=11, textColor=TEXT_BLACK, alignment=1)
    style_h = ParagraphStyle('H', fontName=FONT_NAME, fontSize=10, textColor=NAVY, spaceAfter=8, borderLeftWidth=2, borderLeftColor=NAVY, leftIndent=5)
    style_p = ParagraphStyle('P', fontName=FONT_NAME, fontSize=9, leading=13, textColor=TEXT_BLACK)
    
    story = []
    
    # 1. TYTUŁ I TERMIN
    story.append(Paragraph(tytul.upper(), style_title))
    story.append(Spacer(1, 10))
    story.append(Paragraph(f"📅 TERMIN: {termin}", style_term))
    story.append(Spacer(1, 20))

    # 2. ZDJĘCIE GŁÓWNE W RAMCE
    if foto_main:
        story.append(create_bordered_image(foto_main, 16.5*cm, 7.5*cm))
        story.append(Spacer(1, 25))

    # KARTA (4pt zaokrąglenia)
    def create_card(content_para, width=17.5*cm):
        t = Table([[content_para]], colWidths=[width])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), WHITE),
            ('ROUNDEDCORNERS', [4, 4, 4, 4]),
            ('LEFTPADDING', (0,0), (-1,-1), 15),
            ('TOPPADDING', (0,0), (-1,-1), 12),
            ('BOTTOMPADDING', (0,0), (-1,-1), 12),
        ]))
        return t

    # 3. PROGRAM
    story.append(Paragraph("✈️ PROGRAM WYCIECZKI", style_h))
    story.append(create_card(Paragraph(plan.replace('\n', '<br/>'), style_p)))
    story.append(Spacer(1, 20))

    # 4. KOSZTY I ŚWIADCZENIA (Nagłówki NAD polami)
    story.append(Table([
        [Paragraph("💰 KOSZTY", style_h), Paragraph("📋 ŚWIADCZENIA", style_h)],
        [create_card(Paragraph(ceny.replace('\n', '<br/>'), style_p), width=8.3*cm), 
         create_card(Paragraph(zawiera.replace('\n', '<br/>'), style_p), width=8.3*cm)]
    ], colWidths=[8.7*cm, 8.7*cm], style=[('VALIGN', (0,0), (-1,-1), 'TOP'), ('LEFTPADDING', (0,0), (-1,-1), 0)]))

    # 5. GALERIA
    if galeria:
        story.append(Spacer(1, 25))
        story.append(Paragraph("📸 GALERIA", style_h))
        row, g_data = [], []
        for i, f in enumerate(galeria):
            row.append(create_bordered_image(f, 5.3*cm, 3.8*cm))
            if (i + 1) % 3 == 0:
                g_data.append(row)
                row = []
        if row: g_data.append(row)
        story.append(Table(g_data, colWidths=[5.8*cm]*3))

    doc.addPageTemplates([PageTemplate(id='Travis', frames=Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height), onPage=my_page_layout)])
    doc.build(story)
    return buffer.getvalue()

# --- STREAMLIT ---
st.set_page_config(page_title="Travis Designer", layout="centered")
st.title("🏝️ Travis Designer Premium")

with st.sidebar:
    st.header("Kontakt")
    st.session_state['tel'] = st.text_input("Tel", "789 563 405")
    st.session_state['mail'] = st.text_input("Mail", "biuro@travis.pl")
    f_main = st.file_uploader("Zdjęcie główne", type=['jpg','png'])
    f_gal = st.file_uploader("Galeria", type=['jpg','png'], accept_multiple_files=True)

u_t = st.text_input("Tytuł")
u_d = st.text_input("Termin")
u_p = st.text_area("Program", height=200)
u_c = st.text_area("Koszty", height=100)
u_s = st.text_area("Świadczenia", height=100)

if st.button("🚀 GENERUJ OFERTĘ"):
    if u_t:
        pdf = generate_pdf(u_t, u_d, u_p, u_c, u_s, f_main, f_gal)
        st.download_button("📥 POBIERZ PDF", data=pdf, file_name=f"Oferta_Travis_{u_t}.pdf", mime="application/pdf")
