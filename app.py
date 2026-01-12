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
    try:
        return requests.get(url, timeout=10).content
    except: return None

FONT_BYTES = get_resource("https://github.com/google/fonts/raw/main/ofl/opensans/OpenSans%5Bwdth%2Cwght%5D.ttf")
if FONT_BYTES:
    pdfmetrics.registerFont(TTFont('Standard', BytesIO(FONT_BYTES)))
    FONT_NAME = 'Standard'
else: FONT_NAME = 'Helvetica'

# --- 2. KOLORY I STYLE ---
NAVY = colors.HexColor("#002d5a")
TEXT_BLACK = colors.HexColor("#1a1a1a")
WHITE = colors.white

# --- 3. FUNKCJA CIENIA DLA ZDJĘĆ ---
def shadow_image(img_file, w, h):
    try:
        img = Image(img_file, width=w, height=h, kind='proportional')
        t = Table([[img]], colWidths=[w + 0.3*cm], rowHeights=[h + 0.3*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,0), colors.HexColor("#f0f0f0")), # Delikatny cień
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('RIGHTPADDING', (0,0), (-1,-1), 3),
        ]))
        return t
    except: return Paragraph("[Obraz]", getSampleStyleSheet()['Normal'])

# --- 4. GENERATOR PDF ---
def generate_pdf(tytul, termin, plan, koszt, zawiera, nie_zawiera, foto_main, galeria):
    buffer = BytesIO()
    # Marginesy
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=1.5*cm, leftMargin=1.5*cm, topMargin=1*cm, bottomMargin=1*cm)
    
    style_h = ParagraphStyle('H', fontName=FONT_NAME, fontSize=11, textColor=NAVY, spaceAfter=8, borderLeftWidth=3, borderLeftColor=NAVY, leftIndent=8)
    style_p = ParagraphStyle('P', fontName=FONT_NAME, fontSize=9, leading=12, textColor=TEXT_BLACK)
    
    story = []

    # LOGO NA GÓRZE (Klasycznie w Story)
    logo_url = "https://travis.pl/wp-content/uploads/2025/07/logo_travis500.png"
    try:
        logo = Image(logo_url, width=7*cm, height=2*cm, kind='proportional')
        story.append(logo)
    except: pass
    
    story.append(Spacer(1, 15))

    # TYTUŁ I TERMIN
    story.append(Paragraph(tytul.upper(), ParagraphStyle('T', fontName=FONT_NAME, fontSize=22, alignment=1, textColor=NAVY)))
    story.append(Spacer(1, 5))
    story.append(Paragraph(f"📅 TERMIN: {termin}", ParagraphStyle('S', fontName=FONT_NAME, fontSize=12, alignment=1)))
    story.append(Spacer(1, 20))

    # ZDJĘCIE GŁÓWNE
    if foto_main:
        story.append(shadow_image(foto_main, 17*cm, 8*cm))
        story.append(Spacer(1, 25))

    # KARTA (Biała z obramowaniem zamiast tła)
    def card(content, w):
        t = Table([[content]], colWidths=[w])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), WHITE),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#eeeeee")), # Bardzo subtelna ramka
            ('ROUNDEDCORNERS', [5, 5, 5, 5]),
            ('PADDING', 12)
        ]))
        return t

    # PROGRAM
    story.append(Paragraph("✈️ PROGRAM WYCIECZKI", style_h))
    story.append(card(Paragraph(plan.replace('\n','<br/>'), style_p), 17.5*cm))
    story.append(Spacer(1, 20))

    # FINANSE - 3 BLOKI
    story.append(Paragraph("💰 SZCZEGÓŁY FINANSOWE", style_h))
    col_w = 5.5*cm
    f_table = Table([
        [Paragraph("<b>Koszt:</b>", style_p), Paragraph("<b>Cena zawiera:</b>", style_p), Paragraph("<b>Cena nie zawiera:</b>", style_p)],
        [card(Paragraph(koszt.replace('\n','<br/>'), style_p), col_w),
         card(Paragraph(zawiera.replace('\n','<br/>'), style_p), col_w),
         card(Paragraph(nie_zawiera.replace('\n','<br/>'), style_p), col_w)]
    ], colWidths=[5.8*cm]*3)
    f_table.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP')]))
    story.append(f_table)

    # GALERIA
    if galeria:
        story.append(Spacer(1, 25))
        story.append(Paragraph("📸 GALERIA", style_h))
        g_rows, row = [], []
        for i, f in enumerate(galeria):
            row.append(shadow_image(f, 5.2*cm, 3.5*cm))
            if (i+1)%3==0: g_rows.append(row); row=[]
        if row: g_rows.append(row)
        story.append(Table(g_rows, colWidths=[5.6*cm]*3))

    # STOPKA
    story.append(Spacer(1, 30))
    tel = st.session_state.get('tel', '789 563 405')
    mail = st.session_state.get('mail', 'biuro@travis.pl')
    story.append(Paragraph(f"<hr/><center><font size=8>Biuro Podróży TRAVIS | tel: {tel} | e-mail: {mail}<br/>Wpis do Rejestru Organizatorów nr 41059</font></center>", style_p))

    doc.build(story)
    return buffer.getvalue()

# --- 5. UI ---
st.title("🏝️ Travis Offer Designer")
with st.sidebar:
    st.session_state['tel'] = st.text_input("Telefon", "789 563 405")
    st.session_state['mail'] = st.text_input("E-mail", "biuro@travis.pl")
    f_main = st.file_uploader("Zdjęcie główne", type=['jpg','png'])
    f_gal = st.file_uploader("Galeria", type=['jpg','png'], accept_multiple_files=True)

u_t = st.text_input("Tytuł wycieczki")
u_d = st.text_input("Termin")
u_p = st.text_area("Program wycieczki", height=200)

c1, c2, c3 = st.columns(3)
with c1: u_k = st.text_area("Koszt")
with c2: u_z = st.text_area("Cena zawiera")
with c3: u_nz = st.text_area("Cena nie zawiera")

if st.button("🚀 GENERUJ PDF"):
    if u_t:
        pdf_final = generate_pdf(u_t, u_d, u_p, u_k, u_z, u_nz, f_main, f_gal)
        st.download_button("📥 POBIERZ PDF", data=pdf_final, file_name=f"Oferta_Travis_{u_t}.pdf")
