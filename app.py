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

# --- OBSŁUGA POLSKICH ZNAKÓW I CZCIONEK ---
@st.cache_data
def load_fonts():
    try:
        # Pobieramy Roboto - nowoczesna, zgrabna i czytelna czcionka z PL znakami
        r_reg = requests.get("https://github.com/google/fonts/raw/main/apache/roboto/Roboto-Regular.ttf")
        r_bold = requests.get("https://github.com/google/fonts/raw/main/apache/roboto/Roboto-Bold.ttf")
        
        pdfmetrics.registerFont(TTFont('Roboto', BytesIO(r_reg.content)))
        pdfmetrics.registerFont(TTFont('Roboto-Bold', BytesIO(r_bold.content)))
        return 'Roboto', 'Roboto-Bold'
    except:
        return 'Helvetica', 'Helvetica-Bold'

FONT_REG, FONT_BOLD = load_fonts()

# --- KOLORY LOGO TRAVIS ---
NAVY = colors.HexColor("#002d5a")
BG_GRAY = colors.HexColor("#f1f3f5") # Jaśniejszy szary dla nowoczesnego efektu
WHITE = colors.white

def draw_decorations(canvas, doc):
    canvas.saveState()
    # Tło
    canvas.setFillColor(BG_GRAY)
    canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
    
    # Element graficzny inspirowany logo (linia akcentowa po lewej)
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, 0.4*cm, A4[1], fill=1, stroke=0)
    
    # Stopka
    footer_y = 1.0 * cm
    canvas.setFont(FONT_REG, 7)
    canvas.setFillColor(NAVY)
    canvas.drawCentredString(A4[0]/2, footer_y + 10, f"Biuro Podróży TRAVIS | tel: {st.session_state.get('tel', '')} | e-mail: {st.session_state.get('mail', '')}")
    canvas.setFont(FONT_BOLD, 7)
    canvas.drawCentredString(A4[0]/2, footer_y, "wpis do Rejestru Organizatorów i Pośredników Turystycznych pod numerem 41059")
    canvas.restoreState()

def generate_pdf(tytul, termin, plan, ceny, zawiera, nie_zawiera, foto_main, galeria):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=1.5*cm, rightMargin=1.5*cm, topMargin=1.5*cm, bottomMargin=2.5*cm)
    
    styles = getSampleStyleSheet()
    # Zmniejszone, zgrabniejsze teksty
    style_title = ParagraphStyle('T', fontName=FONT_BOLD, fontSize=16, textColor=NAVY, alignment=0, spaceAfter=2)
    style_term = ParagraphStyle('ST', fontName=FONT_REG, fontSize=10, textColor=NAVY, alignment=0, spaceAfter=15)
    style_h = ParagraphStyle('H', fontName=FONT_BOLD, fontSize=10, textColor=NAVY, spaceBefore=8, spaceAfter=4, borderLeftWidth=2, borderLeftColor=NAVY, leftIndent=5)
    style_p = ParagraphStyle('P', fontName=FONT_REG, fontSize=8.5, leading=11, textColor=colors.black)
    
    story = []

    # 1. LOGO
    logo_url = "https://travis.pl/wp-content/uploads/2025/07/logo_travis500.png"
    try:
        resp = requests.get(logo_url)
        logo = Image(BytesIO(resp.content), width=3.5*cm, height=1.0*cm, kind='proportional')
        logo.hAlign = 'LEFT'
        story.append(logo)
    except: pass
    story.append(Spacer(1, 15))

    # 2. BLOK TYTUŁOWY
    story.append(Paragraph(tytul.upper(), style_title))
    story.append(Paragraph(f"TERMIN: {termin}", style_term))

    # 3. ZDJĘCIE GŁÓWNE
    if foto_main:
        img = Image(foto_main, width=17*cm, height=6.5*cm, kind='proportional')
        img.hAlign = 'CENTER'
        story.append(img)
        story.append(Spacer(1, 10))

    # 4. PROGRAM (Biała karta)
    story.append(Paragraph("PROGRAM WYCIECZKI", style_h))
    t_plan = Table([[Paragraph(plan.replace('\n', '<br/>'), style_p)]], colWidths=[17*cm])
    t_plan.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), WHITE),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_plan)

    # 5. CENY I ŚWIADCZENIA (Nowoczesny układ)
    story.append(Spacer(1, 10))
    data_cost = [
        [Paragraph("KOSZTY", style_h), Paragraph("ŚWIADCZENIA", style_h)],
        [Paragraph(ceny.replace('\n', '<br/>'), style_p), Paragraph(zawiera.replace('\n', '<br/>'), style_p)]
    ]
    t_cost = Table(data_cost, colWidths=[8.5*cm, 8.5*cm])
    t_cost.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), WHITE),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_cost)

    # 6. GALERIA
    if galeria:
        story.append(Spacer(1, 10))
        story.append(Paragraph("GALERIA", style_h))
        imgs = []
        row = []
        for i, f in enumerate(galeria):
            img = Image(f, width=5.3*cm, height=3.5*cm, kind='proportional')
            row.append(img)
            if (i + 1) % 3 == 0:
                imgs.append(row)
                row = []
        if row: imgs.append(row)
        t_gal = Table(imgs, colWidths=[5.6*cm]*3)
        story.append(t_gal)

    # Budowa
    doc.addPageTemplates([PageTemplate(id='T', frames=Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height), onPage=draw_decorations)])
    doc.build(story)
    return buffer.getvalue()

# --- STREAMLIT ---
st.title("🏝️ Generator Travis v4 - Nowoczesny PDF")

with st.sidebar:
    st.header("⚙️ Konfiguracja")
    st.session_state['tel'] = st.text_input("Telefon", "789 563 405")
    st.session_state['mail'] = st.text_input("E-mail", "biuro@travis.pl")
    foto_m = st.file_uploader("Zdjęcie główne", type=['jpg', 'png'])
    galeria_m = st.file_uploader("Galeria zdjęć", type=['jpg', 'png'], accept_multiple_files=True)

u_tytul = st.text_input("Tytuł wycieczki")
u_termin = st.text_input("Termin")
u_plan = st.text_area("Plan", height=150)
u_ceny = st.text_area("Ceny", height=80)
u_zawiera = st.text_area("Zawiera", height=80)
u_nie_zawiera = st.text_area("Nie zawiera", height=80)

if st.button("🚀 GENERUJ PROFESJONALNY PDF"):
    if u_tytul:
        pdf_bytes = generate_pdf(u_tytul, u_termin, u_plan, u_ceny, u_zawiera, u_nie_zawiera, foto_m, galeria_m)
        st.download_button("📥 Pobierz PDF", data=pdf_bytes, file_name=f"Oferta_{u_tytul}.pdf", mime="application/pdf")
    else:
        st.error("Wpisz tytuł!")
