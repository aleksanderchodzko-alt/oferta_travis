import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageTemplate, Frame
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
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
    except: return 'Helvetica'

FONT_NAME = setup_fonts()
NAVY = colors.HexColor("#002d5a")
TEXT_BLACK = colors.HexColor("#1a1a1a")
BG_LIGHT = colors.HexColor("#f8f9fa")

# --- FUNKCJA CIENIA ---
def shadow_image(img_file, w, h):
    try:
        img = Image(img_file, width=w, height=h, kind='proportional')
        t = Table([[img]], colWidths=[w + 0.3*cm], rowHeights=[h + 0.3*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,0), colors.HexColor("#e8e8e8")),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ]))
        return t
    except: return Paragraph("[Błąd obrazu]", getSampleStyleSheet()['Normal'])

# --- SZABLON STRONY ---
def my_page_layout(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(BG_LIGHT)
    canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
    
    # Góra
    canvas.setFillColor(NAVY)
    p = canvas.beginPath()
    p.moveTo(0, A4[1])
    p.lineTo(A4[0], A4[1])
    p.lineTo(A4[0], A4[1]-1*cm)
    p.curveTo(A4[0]*0.6, A4[1]-1.8*cm, A4[0]*0.4, A4[1]-0.4*cm, 0, A4[1]-1.2*cm)
    p.close()
    canvas.drawPath(p, fill=1, stroke=0)

    # LOGO (Stabilna metoda)
    try:
        logo_url = "https://travis.pl/wp-content/uploads/2025/07/logo_travis500.png"
        canvas.drawImage(logo_url, (A4[0]-7.5*cm)/2, A4[1]-3.2*cm, width=7.5*cm, preserveAspectRatio=True, mask='auto')
    except: pass

    # Dół
    canvas.setFillColor(NAVY)
    p_bot = canvas.beginPath()
    p_bot.moveTo(0, 0); p_bot.lineTo(A4[0], 0); p_bot.lineTo(A4[0], 2.2*cm)
    p_bot.curveTo(A4[0]*0.7, 1.2*cm, A4[0]*0.3, 3.2*cm, 0, 1.7*cm); p_bot.close()
    canvas.drawPath(p_bot, fill=1, stroke=0)
    
    # STOPKA
    canvas.setFillColor(colors.white)
    canvas.setFont(FONT_NAME, 7)
    tel = st.session_state.get('tel', '')
    mail = st.session_state.get('mail', '')
    canvas.drawCentredString(A4[0]/2, 1.2*cm, f"Biuro Podróży TRAVIS | tel: {tel} | e-mail: {mail}")
    canvas.drawCentredString(A4[0]/2, 0.8*cm, "Wpis do Rejestru Organizatorów i Pośredników Turystycznych nr 41059")
    canvas.restoreState()

def generate_pdf(tytul, termin, plan, koszt, zawiera, nie_zawiera, foto_main, galeria):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=4.5*cm, bottomMargin=3.5*cm, leftMargin=1.2*cm, rightMargin=1.2*cm)
    
    style_h = ParagraphStyle('H', fontName=FONT_NAME, fontSize=11, textColor=NAVY, spaceAfter=8, borderLeftWidth=3, borderLeftColor=NAVY, leftIndent=8)
    style_p = ParagraphStyle('P', fontName=FONT_NAME, fontSize=9, leading=12, textColor=TEXT_BLACK)
    
    story = []
    story.append(Paragraph(tytul.upper(), ParagraphStyle('T', fontName=FONT_NAME, fontSize=22, alignment=1, textColor=NAVY)))
    story.append(Spacer(1, 10))
    story.append(Paragraph(f"📅 TERMIN: {termin}", ParagraphStyle('S', fontName=FONT_NAME, fontSize=12, alignment=1)))
    story.append(Spacer(1, 20))

    if foto_main:
        story.append(shadow_image(foto_main, 17.5*cm, 8*cm))
        story.append(Spacer(1, 25))

    # POPRAWIONA FUNKCJA KARTY (bez błędnego PADDING)
    def card(content, w):
        t = Table([[content]], colWidths=[w])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.white),
            ('ROUNDEDCORNERS', [5, 5, 5, 5]),
            ('LEFTPADDING', (0,0), (-1,-1), 12),
            ('RIGHTPADDING', (0,0), (-1,-1), 12),
            ('TOPPADDING', (0,0), (-1,-1), 12),
            ('BOTTOMPADDING', (0,0), (-1,-1), 12),
        ]))
        return t

    story.append(Paragraph("✈️ PROGRAM WYCIECZKI", style_h))
    story.append(card(Paragraph(plan.replace('\n','<br/>'), style_p), 18*cm))
    story.append(Spacer(1, 20))

    # FINANSE
    story.append(Paragraph("💰 SZCZEGÓŁY FINANSOWE", style_h))
    col_w = 5.7*cm
    f_table = Table([
        [Paragraph("<b>Koszt:</b>", style_p), Paragraph("<b>Cena zawiera:</b>", style_p), Paragraph("<b>Cena nie zawiera:</b>", style_p)],
        [card(Paragraph(koszt.replace('\n','<br/>'), style_p), col_w),
         card(Paragraph(zawiera.replace('\n','<br/>'), style_p), col_w),
         card(Paragraph(nie_zawiera.replace('\n','<br/>'), style_p), col_w)]
    ], colWidths=[6.1*cm]*3)
    f_table.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP')]))
    story.append(f_table)

    if galeria:
        story.append(Spacer(1, 25))
        story.append(Paragraph("📸 GALERIA", style_h))
        g_rows, row = [], []
        for i, f in enumerate(galeria):
            row.append(shadow_image(f, 5.3*cm, 3.5*cm))
            if (i+1)%3==0: g_rows.append(row); row=[]
        if row: g_rows.append(row)
        story.append(Table(g_rows, colWidths=[6*cm]*3))

    doc.addPageTemplates([PageTemplate(id='T', frames=Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height), onPage=my_page_layout)])
    doc.build(story)
    return buffer.getvalue()

# --- UI ---
st.title("🏝️ Travis Designer Premium")
with st.sidebar:
    st.session_state['tel'] = st.text_input("Numer telefonu", "789 563 405")
    st.session_state['mail'] = st.text_input("Adres e-mail", "biuro@travis.pl")
    f_main = st.file_uploader("Zdjęcie główne", type=['jpg','png'])
    f_gal = st.file_uploader("Galeria", type=['jpg','png'], accept_multiple_files=True)

u_t = st.text_input("Tytuł")
u_d = st.text_input("Termin")
u_p = st.text_area("Program")
c1, c2, c3 = st.columns(3)
with c1: u_k = st.text_area("Koszt")
with c2: u_z = st.text_area("Cena zawiera")
with c3: u_nz = st.text_area("Cena nie zawiera")

if st.button("🚀 GENERUJ PDF"):
    if u_t:
        pdf_final = generate_pdf(u_t, u_d, u_p, u_k, u_z, u_nz, f_main, f_gal)
        st.download_button("📥 POBIERZ", data=pdf_final, file_name=f"Oferta_Travis_{u_t}.pdf")
