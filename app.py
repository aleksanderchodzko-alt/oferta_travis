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

# --- OBSŁUGA POLSKICH ZNAKÓW ---
# Pobieramy czcionkę z obsługą PL znaków (np. DejaVuSans)
try:
    font_url = "https://github.com/reingart/pyfpdf/raw/master/font/DejaVuSans.ttf"
    font_res = requests.get(font_url)
    with open("font.ttf", "wb") as f:
        f.write(font_res.content)
    pdfmetrics.registerFont(TTFont('DejaVu', 'font.ttf'))
    FONT_NAME = 'DejaVu'
    FONT_BOLD = 'DejaVu' # W tej wersji DejaVu jest jedna, dla pogrubienia można pobrać DejaVuSans-Bold
except:
    FONT_NAME = 'Helvetica' # Fallback

# --- KOLORY TRAVIS ---
NAVY = colors.HexColor("#002d5a")
BG_GRAY = colors.HexColor("#f8f9fa")
WHITE = colors.white

def draw_background(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(BG_GRAY)
    canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
    
    # Stała stopka
    footer_y = 1.0 * cm
    canvas.setFont(FONT_NAME, 7)
    canvas.setFillColor(NAVY)
    canvas.drawCentredString(A4[0]/2, footer_y + 10, f"Biuro Podróży TRAVIS | tel: {st.session_state.get('tel', '')} | e-mail: {st.session_state.get('mail', '')}")
    canvas.drawCentredString(A4[0]/2, footer_y, "wpis do Rejestru Organizatorów i Pośredników Turystycznych pod numerem 41059")
    canvas.restoreState()

def generate_pdf(tytul, termin, plan, ceny, zawiera, nie_zawiera, foto_main, galeria):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=1.5*cm, rightMargin=1.5*cm, topMargin=1.5*cm, bottomMargin=2.5*cm)
    
    styles = getSampleStyleSheet()
    style_title = ParagraphStyle('T', fontName=FONT_NAME, fontSize=20, textColor=NAVY, alignment=1, spaceAfter=20)
    style_h = ParagraphStyle('H', fontName=FONT_NAME, fontSize=11, textColor=NAVY, spaceBefore=10, spaceAfter=6)
    style_p = ParagraphStyle('P', fontName=FONT_NAME, fontSize=9, leading=12, textColor=colors.black)
    
    story = []

    # 1. LOGO
    logo_url = "https://travis.pl/wp-content/uploads/2025/07/logo_travis500.png"
    try:
        resp = requests.get(logo_url)
        logo = Image(BytesIO(resp.content), width=4.5*cm, height=1.3*cm, kind='proportional')
        logo.hAlign = 'LEFT'
        story.append(logo)
    except: pass
    story.append(Spacer(1, 10))

    # 2. BLOK TYTUŁOWY (Karta tytułowa)
    title_table = Table([[Paragraph(tytul.upper(), style_title), Paragraph(f"TERMIN: {termin}", style_p)]], colWidths=[12*cm, 5*cm])
    title_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('ALIGN', (1,0), (1,0), 'RIGHT')]))
    story.append(title_table)
    story.append(Spacer(1, 10))

    # 3. ZDJĘCIE GŁÓWNE
    if foto_main:
        img = Image(foto_main, width=17*cm, height=7*cm, kind='proportional')
        img.hAlign = 'CENTER'
        story.append(img)
        story.append(Spacer(1, 15))

    # 4. PROGRAM (Biała karta)
    story.append(Paragraph("PROGRAM WYCIECZKI", style_h))
    t_plan = Table([[Paragraph(plan.replace('\n', '<br/>'), style_p)]], colWidths=[17*cm])
    t_plan.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), WHITE), ('LEFTPADDING', (0,0), (-1,-1), 15), ('TOPPADDING', (0,0), (-1,-1), 15), ('BOTTOMPADDING', (0,0), (-1,-1), 15)]))
    story.append(t_plan)
    story.append(Spacer(1, 15))

    # 5. CENY I ŚWIADCZENIA
    story.append(Paragraph("KOSZTY I ŚWIADCZENIA", style_h))
    data_cost = [[Paragraph(ceny.replace('\n', '<br/>'), style_p), Paragraph(zawiera.replace('\n', '<br/>'), style_p)]]
    t_cost = Table(data_cost, colWidths=[8.5*cm, 8.5*cm])
    t_cost.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), WHITE), ('GRID', (0,0), (-1,-1), 0.1, BG_GRAY), ('VALIGN', (0,0), (-1,-1), 'TOP')]))
    story.append(t_cost)

    # 6. DODATKOWA GALERIA ZDJĘĆ
    if galeria:
        story.append(Spacer(1, 15))
        story.append(Paragraph("GALERIA ZDJĘĆ", style_h))
        imgs = []
        row = []
        for i, f in enumerate(galeria):
            img = Image(f, width=5.4*cm, height=4*cm, kind='proportional')
            row.append(img)
            if (i + 1) % 3 == 0:
                imgs.append(row)
                row = []
        if row: imgs.append(row)
        t_gal = Table(imgs, colWidths=[5.6*cm]*3)
        story.append(t_gal)

    # Budowanie PDF
    doc.addPageTemplates([PageTemplate(id='T', frames=Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height), onPage=draw_background)])
    doc.build(story)
    return buffer.getvalue()

# --- INTERFEJS STREAMLIT ---
st.title("🏝️ Generator Ofert Travis v3")

with st.sidebar:
    st.header("⚙️ Ustawienia")
    st.session_state['tel'] = st.text_input("Telefon", "789 563 405")
    st.session_state['mail'] = st.text_input("E-mail", "biuro@travis.pl")
    foto_m = st.file_uploader("Zdjęcie główne", type=['jpg', 'png'])
    galeria_m = st.file_uploader("Galeria zdjęć (max 6)", type=['jpg', 'png'], accept_multiple_files=True)

u_tytul = st.text_input("Tytuł wycieczki (np. MALTA 4 DNI)")
u_termin = st.text_input("Termin")
u_plan = st.text_area("Plan podróży", height=150)
u_ceny = st.text_area("Ceny (konfiguracje)", height=100)
u_zawiera = st.text_area("Co zawiera cena", height=100)
u_nie_zawiera = st.text_area("Czego nie zawiera", height=100)

if st.button("🚀 GENERUJ PDF Z POLSKIMI ZNAKAMI"):
    pdf_bytes = generate_pdf(u_tytul, u_termin, u_plan, u_ceny, u_zawiera, u_nie_zawiera, foto_m, galeria_m)
    st.download_button("📥 Pobierz gotowy PDF", data=pdf_bytes, file_name=f"Oferta_{u_tytul}.pdf", mime="application/pdf")
