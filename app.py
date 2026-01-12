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

# --- 1. CZCIONKI I LOGO ---
@st.cache_data
def get_resource(url):
    try:
        return requests.get(url, timeout=10).content
    except: return None

# Pobieranie czcionki z polskimi znakami
FONT_BYTES = get_resource("https://github.com/google/fonts/raw/main/ofl/opensans/OpenSans%5Bwdth%2Cwght%5D.ttf")
if FONT_BYTES:
    pdfmetrics.registerFont(TTFont('Standard', BytesIO(FONT_BYTES)))
    FONT_NAME = 'Standard'
else: FONT_NAME = 'Helvetica'

# --- 2. STYLE ---
NAVY = colors.HexColor("#002d5a")
TEXT_BLACK = colors.HexColor("#1a1a1a")

# --- 3. FUNKCJA CIENIA (SUBTELNA) ---
def shadow_image(img_file, w, h):
    try:
        img = Image(img_file, width=w, height=h, kind='proportional')
        # Tabela tworząca efekt przesuniętego cienia
        t = Table([[img]], colWidths=[w + 0.2*cm], rowHeights=[h + 0.2*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,0), colors.HexColor("#f4f4f4")),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('RIGHTPADDING', (0,0), (-1,-1), 3),
        ]))
        return t
    except: return Paragraph("[Błąd obrazu]", getSampleStyleSheet()['Normal'])

# --- 4. GŁÓWNA FUNKCJA PDF ---
def generate_pdf(tytul, termin, plan, koszt, zawiera, nie_zawiera, foto_main, galeria):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=1.5*cm, leftMargin=1.5*cm, topMargin=1.5*cm, bottomMargin=1.5*cm)
    
    style_h = ParagraphStyle('H', fontName=FONT_NAME, fontSize=11, textColor=NAVY, spaceAfter=8, borderLeftWidth=3, borderLeftColor=NAVY, leftIndent=8)
    style_p = ParagraphStyle('P', fontName=FONT_NAME, fontSize=9, leading=12, textColor=TEXT_BLACK)
    
    story = []

    # LOGO (Wstawione bezpośrednio na górze)
    logo_url = "https://travis.pl/wp-content/uploads/2025/07/logo_travis500.png"
    try:
        logo = Image(logo_url, width=7.5*cm, height=2.2*cm, kind='proportional')
        logo.hAlign = 'CENTER'
        story.append(logo)
        story.append(Spacer(1, 15))
    except:
        story.append(Paragraph("<b>TRAVIS TRAVEL</b>", style_h))

    # TYTUŁ I TERMIN
    story.append(Paragraph(tytul.upper(), ParagraphStyle('T', fontName=FONT_NAME, fontSize=22, alignment=1, textColor=NAVY)))
    story.append(Spacer(1, 5))
    story.append(Paragraph(f"📅 TERMIN: {termin}", ParagraphStyle('S', fontName=FONT_NAME, fontSize=12, alignment=1)))
    story.append(Spacer(1, 20))

    # ZDJĘCIE GŁÓWNE
    if foto_main:
        story.append(shadow_image(foto_main, 17.5*cm, 8*cm))
        story.append(Spacer(1, 25))

    # KARTA (Naprawiony PADDING)
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

    # PROGRAM
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

    # GALERIA
    if galeria:
        story.append(Spacer(1, 25))
        story.append(Paragraph("📸 GALERIA", style_h))
        g_rows, row = [], []
        for i, f in enumerate(galeria):
            row.append(shadow_image(f, 5.5*cm, 3.8*cm))
            if (i+1)%3==0: g_rows.append(row); row=[]
        if row: g_rows.append(row)
        story.append(Table(g_rows, colWidths=[6.1*cm]*3))

    # STOPKA
    story.append(Spacer(1, 30))
    tel = st.session_state.get('tel', '789 563 405')
    mail = st.session_state.get('mail', 'biuro@travis.pl')
    footer_text = f"Biuro Podróży TRAVIS | tel: {tel} | e-mail: {mail}<br/>Wpis do Rejestru Organizatorów nr 41059"
    story.append(Paragraph(f"<hr/><center><font size=8>{footer_text}</font></center>", style_p))

    doc.build(story)
    return buffer.getvalue()

# --- 5. UI STREAMLIT ---
st.set_page_config(page_title="Travis Offer Designer", layout="centered")
st.title("🏝️ Travis Designer Crystal")

with st.sidebar:
    st.header("Dane kontaktowe")
    st.session_state['tel'] = st.text_input("Numer telefonu", "789 563 405")
    st.session_state['mail'] = st.text_input("Adres e-mail", "biuro@travis.pl")
    f_main = st.file_uploader("Zdjęcie główne", type=['jpg','png'])
    f_gal = st.file_uploader("Galeria", type=['jpg','png'], accept_multiple_files=True)

u_t = st.text_input("Tytuł wycieczki")
u_d = st.text_input("Termin")
u_p = st.text_area("Program (Dzień po dniu)", height=200)

c1, c2, c3 = st.columns(3)
with c1: u_k = st.text_area("Koszt")
with c2: u_z = st.text_area("Cena zawiera")
with c3: u_nz = st.text_area("Cena nie zawiera")

if st.button("🚀 GENERUJ PDF"):
    if u_t:
        with st.spinner("Budowanie PDF..."):
            pdf_out = generate_pdf(u_t, u_d, u_p, u_k, u_z, u_nz, f_main, f_gal)
            st.download_button("📥 POBIERZ GOTOWĄ OFERTĘ", data=pdf_out, file_name=f"Oferta_Travis_{u_t}.pdf", mime="application/pdf")
    else:
        st.warning("Wpisz tytuł wycieczki!")
