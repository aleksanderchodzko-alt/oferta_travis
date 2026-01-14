import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
import requests

# --- 1. ZASOBY ---
@st.cache_data
def get_resource(url):
    try: return requests.get(url, timeout=10).content
    except: return None

FONT_BYTES = get_resource("https://github.com/google/fonts/raw/main/ofl/opensans/OpenSans%5Bwdth%2Cwght%5D.ttf")
if FONT_BYTES:
    pdfmetrics.registerFont(TTFont('Standard', BytesIO(FONT_BYTES)))
    FONT_NAME = 'Standard'
else: FONT_NAME = 'Helvetica'

NAVY = colors.HexColor("#002d5a")
TEXT_BLACK = colors.HexColor("#1a1a1a")

# --- 2. POMOCNICZE FUNKCJE ---
def shadow_image(img_file, w, h):
    try:
        img = Image(img_file, width=w, height=h, kind='proportional')
        t = Table([[img]], colWidths=[w + 0.2*cm], rowHeights=[h + 0.2*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,0), colors.HexColor("#f4f4f4")),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('RIGHTPADDING', (0,0), (-1,-1), 3),
        ]))
        return t
    except: return None

def card(content, w):
    t = Table([[content]], colWidths=[w])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.white),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#eeeeee")),
        ('ROUNDEDCORNERS', [5, 5, 5, 5]),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
        ('TOPPADDING', (0,0), (-1,-1), 12),
        ('BOTTOMPADDING', (0,0), (-1,-1), 12),
    ]))
    return t

# --- 3. GENERATOR PDF ---
def generate_pdf(tytul, termin, dni_programu, koszt, zawiera, nie_zawiera, foto_main, galeria):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=1.5*cm, leftMargin=1.5*cm, topMargin=1.5*cm, bottomMargin=3.5*cm)
    
    style_h = ParagraphStyle('H', fontName=FONT_NAME, fontSize=11, textColor=NAVY, spaceAfter=8, borderLeftWidth=3, borderLeftColor=NAVY, leftIndent=8)
    style_day = ParagraphStyle('Day', fontName=FONT_NAME, fontSize=10, textColor=NAVY, fontWeight='BOLD', spaceBefore=6)
    style_p = ParagraphStyle('P', fontName=FONT_NAME, fontSize=9, leading=12, textColor=TEXT_BLACK)
    style_info = ParagraphStyle('I', fontName=FONT_NAME, fontSize=8, textColor=colors.gray, italic=True, spaceBefore=10)
    
    story = []

    # LOGO
    try:
        logo = Image("https://travis.pl/wp-content/uploads/2025/07/logo_travis500.png", width=7.5*cm, height=2.2*cm, kind='proportional')
        logo.hAlign = 'CENTER'
        story.append(logo)
        story.append(Spacer(1, 15))
    except: pass

    # NAGŁÓWEK
    story.append(Paragraph(tytul.upper() if tytul else "OFERTA WYCIECZKI", ParagraphStyle('T', fontName=FONT_NAME, fontSize=22, alignment=1, textColor=NAVY)))
    if termin:
        story.append(Spacer(1, 5))
        story.append(Paragraph(f"📅 TERMIN: {termin}", ParagraphStyle('S', fontName=FONT_NAME, fontSize=12, alignment=1)))
    story.append(Spacer(1, 20))

    if foto_main:
        img_shadow = shadow_image(foto_main, 17.5*cm, 8*cm)
        if img_shadow:
            story.append(img_shadow)
            story.append(Spacer(1, 25))

    # PROGRAM DNIA PO DNIU (DYNAMICZNY)
    story.append(Paragraph("✈️ PROGRAM WYCIECZKI", style_h))
    
    program_content = []
    for i, tresc_dnia in enumerate(dni_programu):
        if tresc_dnia.strip():
            program_content.append(Paragraph(f"<b>DZIEŃ {i+1}</b>", style_day))
            program_content.append(Paragraph(tresc_dnia.replace('\n', '<br/>'), style_p))
            program_content.append(Spacer(1, 6))
    
    # Stały dopisek na końcu programu
    program_content.append(Paragraph("Program wycieczki jest ramowy, kolejność atrakcji może ulec zmianie.", style_info))
    
    story.append(card(program_content, 18*cm))
    story.append(Spacer(1, 20))

    # FINANSE (DYNAMICZNE)
    if koszt.strip() or zawiera.strip() or nie_zawiera.strip():
        story.append(Paragraph("💰 SZCZEGÓŁY FINANSOWE", style_h))
        
        # Budujemy wiersze tabeli tylko dla uzupełnionych pól
        fin_cols = []
        if koszt.strip(): fin_cols.append([Paragraph("<b>Koszt:</b>", style_p), card(Paragraph(koszt.replace('\n','<br/>'), style_p), 5.5*cm)])
        if zawiera.strip(): fin_cols.append([Paragraph("<b>Cena zawiera:</b>", style_p), card(Paragraph(zawiera.replace('\n','<br/>'), style_p), 5.5*cm)])
        if nie_zawiera.strip(): fin_cols.append([Paragraph("<b>Cena nie zawiera:</b>", style_p), card(Paragraph(nie_zawiera.replace('\n','<br/>'), style_p), 5.5*cm)])
        
        if fin_cols:
            # Reorganizacja na format tabeli (nagłówki w jednym rzędzie, karty w drugim)
            headers = [item[0] for item in fin_cols]
            cards = [item[1] for item in fin_cols]
            f_table = Table([headers, cards], colWidths=[18*cm / len(fin_cols)] * len(fin_cols))
            f_table.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP')]))
            story.append(f_table)

    # GALERIA
    if galeria:
        story.append(Spacer(1, 25))
        story.append(Paragraph("📸 GALERIA", style_h))
        g_rows, row = [], []
        for i, f in enumerate(galeria):
            img_g = shadow_image(f, 5.5*cm, 3.8*cm)
            if img_g:
                row.append(img_g)
                if (i+1)%3==0: g_rows.append(row); row=[]
        if row: g_rows.append(row)
        if g_rows: story.append(Table(g_rows, colWidths=[6.1*cm]*3))

    def draw_footer_wave(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(NAVY)
        p = canvas.beginPath()
        p.moveTo(0, 0); p.lineTo(A4[0], 0); p.lineTo(A4[0], 2.2*cm)
        p.curveTo(A4[0]*0.7, 1.2*cm, A4[0]*0.3, 3.2*cm, 0, 1.7*cm); p.close()
        canvas.drawPath(p, fill=1, stroke=0)
        canvas.setFillColor(colors.white)
        canvas.setFont(FONT_NAME, 7)
        tel = st.session_state.get('tel', '789 563 405')
        mail = st.session_state.get('mail', 'biuro@travis.pl')
        canvas.drawCentredString(A4[0]/2, 1.1*cm, f"Biuro Podróży TRAVIS | tel: {tel} | e-mail: {mail}")
        canvas.drawCentredString(A4[0]/2, 0.7*cm, "Wpis do Rejestru Organizatorów i Pośredników Turystycznych nr 41059")
        canvas.restoreState()

    doc.build(story, onFirstPage=draw_footer_wave, onLaterPages=draw_footer_wave)
    return buffer.getvalue()

# --- 4. UI ---
st.set_page_config(page_title="Travis Offer Designer", layout="wide")
st.title("🏝️ Travis Designer - Kreator Dynamiczny")

with st.sidebar:
    st.header("Dane i Media")
    st.session_state['tel'] = st.text_input("Numer telefonu", "789 563 405")
    st.session_state['mail'] = st.text_input("Adres e-mail", "biuro@travis.pl")
    f_main = st.file_uploader("Zdjęcie główne", type=['jpg','png'])
    f_gal = st.file_uploader("Galeria (max 6 zdjęć)", type=['jpg','png'], accept_multiple_files=True)

u_t = st.text_input("Tytuł wycieczki")
u_d = st.text_input("Termin")

st.subheader("✈️ Program wycieczki")
col_p1, col_p2 = st.columns(2)
dni_tekst = []
for i in range(1, 9):
    target_col = col_p1 if i <= 4 else col_p2
    with target_col:
        dni_tekst.append(st.text_area(f"DZIEŃ {i}", placeholder=f"Opisz co wydarzy się dnia {i}...", height=100))

st.subheader("💰 Finanse")
c1, c2, c3 = st.columns(3)
with c1: u_k = st.text_area("Koszt (opcjonalnie)")
with c2: u_z = st.text_area("Cena zawiera (opcjonalnie)")
with c3: u_nz = st.text_area("Cena nie zawiera (opcjonalnie)")

if st.button("🚀 GENERUJ PDF"):
    with st.spinner("Generowanie profesjonalnej oferty..."):
        pdf_out = generate_pdf(u_t, u_d, dni_tekst, u_k, u_z, u_nz, f_main, f_gal)
        st.download_button("📥 POBIERZ PDF", data=pdf_out, file_name=f"Oferta_Travis_{u_t}.pdf", mime="application/pdf")
