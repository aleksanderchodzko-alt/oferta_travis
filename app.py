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

# --- FUNKCJA RAMKI DLA ZDJĘĆ ---
def create_bordered_image(img_file, width, height):
    try:
        img = Image(img_file, width=width, height=height, kind='proportional')
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
        return Paragraph("Błąd pliku graficznego", getSampleStyleSheet()['Normal'])

# --- SZABLON STRONY (LOGO, STOPKA, FALKI) ---
def my_page_layout(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(BG_LIGHT)
    canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
    
    # Górna falka
    canvas.setFillColor(NAVY)
    p_top = canvas.beginPath()
    p_top.moveTo(0, A4[1])
    p_top.lineTo(A4[0], A4[1])
    p_top.lineTo(A4[0], A4[1]-0.8*cm)
    p_top.curveTo(A4[0]*0.7, A4[1]-1.5*cm, A4[0]*0.3, A4[1]-0.2*cm, 0, A4[1]-1*cm)
    p_top.close()
    canvas.drawPath(p_top, fill=1, stroke=0)

    # Logo
    logo_url = "https://travis.pl/wp-content/uploads/2025/07/logo_travis500.png"
    try:
        logo_res = requests.get(logo_url)
        canvas.drawImage(Image(BytesIO(logo_res.content)).filename, (A4[0]-7*cm)/2, A4[1]-3.2*cm, width=7*cm, preserveAspectRatio=True, mask='auto')
    except: pass

    # Dolna falka i stopka
    canvas.setFillColor(NAVY)
    p_bot = canvas.beginPath()
    p_bot.moveTo(0, 0)
    p_bot.lineTo(A4[0], 0)
    p_bot.lineTo(A4[0], 2.2*cm)
    p_bot.curveTo(A4[0]*0.7, 1.2*cm, A4[0]*0.3, 3.2*cm, 0, 1.7*cm)
    p_bot.close()
    canvas.drawPath(p_bot, fill=1, stroke=0)
    
    canvas.setFillColor(WHITE)
    canvas.setFont(FONT_NAME, 7)
    u_tel = st.session_state.get('tel', '789 563 405')
    u_mail = st.session_state.get('mail', 'biuro@travis.pl')
    canvas.drawCentredString(A4[0]/2, 1.1*cm, f"Biuro Podróży TRAVIS | tel: {u_tel} | e-mail: {u_mail} | Rejestr nr 41059")
    canvas.restoreState()

def generate_pdf(tytul, termin, plan, koszt, zawiera, nie_zawiera, foto_main, galeria):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=1.2*cm, rightMargin=1.2*cm, topMargin=4.2*cm, bottomMargin=3.5*cm)
    
    style_title = ParagraphStyle('T', fontName=FONT_NAME, fontSize=20, textColor=NAVY, alignment=1)
    style_term = ParagraphStyle('S', fontName=FONT_NAME, fontSize=11, textColor=TEXT_BLACK, alignment=1)
    style_h = ParagraphStyle('H', fontName=FONT_NAME, fontSize=10, textColor=NAVY, spaceAfter=8, borderLeftWidth=2, borderLeftColor=NAVY, leftIndent=5)
    style_p = ParagraphStyle('P', fontName=FONT_NAME, fontSize=8.5, leading=11, textColor=TEXT_BLACK)
    
    story = []
    story.append(Paragraph(tytul.upper(), style_title))
    story.append(Spacer(1, 8))
    story.append(Paragraph(f"📅 TERMIN: {termin}", style_term))
    story.append(Spacer(1, 15))

    if foto_main:
        story.append(create_bordered_image(foto_main, 17.5*cm, 7.5*cm))
        story.append(Spacer(1, 20))

    def create_card(content_para, width=18*cm):
        t = Table([[content_para]], colWidths=[width])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), WHITE),
            ('ROUNDEDCORNERS', [4, 4, 4, 4]),
            ('PADDING', (0,0), (-1,-1), 12),
        ]))
        return t

    # PROGRAM
    story.append(Paragraph("✈️ PROGRAM WYCIECZKI", style_h))
    story.append(create_card(Paragraph(plan.replace('\n', '<br/>'), style_p)))
    story.append(Spacer(1, 15))

    # SEKCCJA FINANSOWA: 3 BLOKI
    col_w = 5.8*cm
    story.append(Table([
        [Paragraph("💰 KOSZT", style_h), Paragraph("📋 CENA ZAWIERA", style_h), Paragraph("❌ CENA NIE ZAWIERA", style_h)],
        [create_card(Paragraph(koszt.replace('\n', '<br/>'), style_p), width=col_w),
         create_card(Paragraph(zawiera.replace('\n', '<br/>'), style_p), width=col_w),
         create_card(Paragraph(nie_zawiera.replace('\n', '<br/>'), style_p), width=col_w)]
    ], colWidths=[6.1*cm]*3, style=[('VALIGN', (0,0), (-1,-1), 'TOP'), ('LEFTPADDING', (0,0), (-1,-1), 0)]))

    # GALERIA
    if galeria:
        story.append(Spacer(1, 20))
        story.append(Paragraph("📸 GALERIA", style_h))
        row, g_data = [], []
        for i, f in enumerate(galeria):
            row.append(create_bordered_image(f, 5.5*cm, 3.8*cm))
            if (i + 1) % 3 == 0:
                g_data.append(row)
                row = []
        if row: g_data.append(row)
        story.append(Table(g_data, colWidths=[6*cm]*3))

    doc.addPageTemplates([PageTemplate(id='Travis', frames=Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height), onPage=my_page_layout)])
    doc.build(story)
    return buffer.getvalue()

# --- UI ---
st.title("🏝️ Travis Premium Designer")
with st.sidebar:
    st.session_state['tel'] = st.text_input("Tel", "789 563 405")
    st.session_state['mail'] = st.text_input("Mail", "biuro@travis.pl")
    f_main = st.file_uploader("Główne", type=['jpg','png'])
    f_gal = st.file_uploader("Galeria", type=['jpg','png'], accept_multiple_files=True)

u_t = st.text_input("Tytuł")
u_d = st.text_input("Termin")
u_p = st.text_area("Program")
c1, c2, c3 = st.columns(3)
with c1: u_koszt = st.text_area("Koszt")
with c2: u_zawiera = st.text_area("Cena zawiera")
with c3: u_nie_zawiera = st.text_area("Cena nie zawiera")

if st.button("🚀 GENERUJ"):
    pdf = generate_pdf(u_t, u_d, u_p, u_koszt, u_zawiera, u_nie_zawiera, f_main, f_gal)
    st.download_button("📥 POBIERZ PDF", data=pdf, file_name="Oferta_Travis.pdf")
