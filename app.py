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

# --- CZCIONKI I POLSKIE ZNAKI ---
@st.cache_data
def load_fonts():
    try:
        # Montserrat - nowoczesna i czytelna czcionka z polskimi znakami
        reg_url = "https://github.com/google/fonts/raw/main/ofl/montserrat/Montserrat-Regular.ttf"
        bold_url = "https://github.com/google/fonts/raw/main/ofl/montserrat/Montserrat-Bold.ttf"
        pdfmetrics.registerFont(TTFont('Montserrat', BytesIO(requests.get(reg_url).content)))
        pdfmetrics.registerFont(TTFont('Montserrat-Bold', BytesIO(requests.get(bold_url).content)))
        return 'Montserrat', 'Montserrat-Bold'
    except:
        return 'Helvetica', 'Helvetica-Bold'

F_REG, F_BOLD = load_fonts()

# --- KOLORY ---
NAVY = colors.HexColor("#002d5a")
SOFT_GRAY = colors.HexColor("#f4f7f9")
TEXT_BLACK = colors.HexColor("#1a1a1a") # Bardzo ciemny szary/czarny dla lepszej czytelności
WHITE = colors.white

def draw_page_decorations(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(SOFT_GRAY)
    canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
    
    # Subtelna fala na dole
    canvas.setFillColor(NAVY)
    p = canvas.beginPath()
    p.moveTo(0, 2.2*cm)
    p.curveTo(6*cm, 3.2*cm, 14*cm, 1.2*cm, A4[0], 2.7*cm)
    p.lineTo(A4[0], 0)
    p.lineTo(0, 0)
    p.close()
    canvas.drawPath(p, fill=1, stroke=0)
    
    # Stopka
    canvas.setFillColor(WHITE)
    canvas.setFont(F_REG, 7)
    u_tel = st.session_state.get('tel', '789 563 405')
    u_mail = st.session_state.get('mail', 'biuro@travis.pl')
    canvas.drawCentredString(A4[0]/2, 1.3*cm, f"Biuro Podróży TRAVIS | tel: {u_tel} | e-mail: {u_mail}")
    canvas.setFont(F_BOLD, 6)
    canvas.drawCentredString(A4[0]/2, 0.9*cm, "wpis do Rejestru Organizatorów i Pośredników Turystycznych nr 41059")
    canvas.restoreState()

def generate_pdf(tytul, termin, plan, ceny, zawiera, nie_zawiera, foto_main, galeria):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=1.5*cm, rightMargin=1.5*cm, topMargin=1*cm, bottomMargin=3.5*cm)
    
    styles = getSampleStyleSheet()
    # Czcionki ustawione na czarny kolor
    style_title = ParagraphStyle('T', fontName=F_BOLD, fontSize=22, textColor=NAVY, alignment=1)
    style_term = ParagraphStyle('S', fontName=F_REG, fontSize=12, textColor=TEXT_BLACK, alignment=1)
    style_h = ParagraphStyle('H', fontName=F_BOLD, fontSize=10, textColor=NAVY, spaceAfter=8, textTransform='uppercase')
    style_p = ParagraphStyle('P', fontName=F_REG, fontSize=9, leading=13, textColor=TEXT_BLACK)
    
    story = []
    
    # 1. LOGO - WIĘKSZE I NA ŚRODKU
    logo_url = "https://travis.pl/wp-content/uploads/2025/07/logo_travis500.png"
    try:
        logo = Image(BytesIO(requests.get(logo_url).content), width=7*cm, height=2*cm, kind='proportional')
        logo.hAlign = 'CENTER'
        story.append(logo)
    except: pass
    story.append(Spacer(1, 20))

    # 2. TYTUŁ I TERMIN Z ODSTĘPEM
    story.append(Paragraph(tytul.upper(), style_title))
    story.append(Spacer(1, 12)) # Odstęp pomiędzy tytułem a terminem
    story.append(Paragraph(f"📅 TERMIN: {termin}", style_term))
    story.append(Spacer(1, 20))

    # 3. ZDJĘCIE GŁÓWNE
    if foto_main:
        img = Image(foto_main, width=17.5*cm, height=7.5*cm, kind='proportional')
        img.hAlign = 'CENTER'
        story.append(img)
        story.append(Spacer(1, 25))

    def rounded_card(content):
        t = Table([[content]], colWidths=[17.5*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), WHITE),
            ('ROUNDEDCORNERS', [15, 15, 15, 15]),
            ('LEFTPADDING', (0,0), (-1,-1), 20),
            ('RIGHTPADDING', (0,0), (-1,-1), 20),
            ('TOPPADDING', (0,0), (-1,-1), 15),
            ('BOTTOMPADDING', (0,0), (-1,-1), 15),
        ]))
        return t

    # 4. PROGRAM Z IKONĄ
    story.append(Paragraph("✈️ PROGRAM PODRÓŻY", style_h))
    story.append(rounded_card(Paragraph(plan.replace('\n', '<br/>'), style_p)))
    story.append(Spacer(1, 15))

    # 5. KOSZTY I ŚWIADCZENIA Z IKONAMI
    c1 = [Paragraph("💰 KOSZTY", style_h), Paragraph(ceny.replace('\n', '<br/>'), style_p)]
    c2 = [Paragraph("📋 ŚWIADCZENIA", style_h), Paragraph(zawiera.replace('\n', '<br/>'), style_p)]
    
    t_side = Table([
        [Table([[c1]], colWidths=[8.4*cm], style=[('BACKGROUND', (0,0), (-1,-1), WHITE), ('ROUNDEDCORNERS', [15,15,15,15]), ('PADDING', (0,0), (-1,-1), 12)]),
         Table([[c2]], colWidths=[8.4*cm], style=[('BACKGROUND', (0,0), (-1,-1), WHITE), ('ROUNDEDCORNERS', [15,15,15,15]), ('PADDING', (0,0), (-1,-1), 12)])]
    ], colWidths=[8.7*cm, 8.7*cm])
    story.append(t_side)

    # 6. GALERIA
    if galeria:
        story.append(Spacer(1, 20))
        story.append(Paragraph("📸 GALERIA ZDJĘĆ", style_h))
        row, g_data = [], []
        for i, f in enumerate(galeria):
            img = Image(f, width=5.5*cm, height=3.8*cm, kind='proportional')
            row.append(img)
            if (i + 1) % 3 == 0:
                g_data.append(row)
                row = []
        if row: g_data.append(row)
        story.append(Table(g_data, colWidths=[5.8*cm]*3))

    doc.addPageTemplates([PageTemplate(id='Travis', frames=Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height), onPage=draw_page_decorations)])
    doc.build(story)
    return buffer.getvalue()

# --- INTERFEJS STREAMLIT ---
st.title("🌊 Generator Travis Premium v5")

with st.sidebar:
    st.header("Dane kontaktowe")
    st.session_state['tel'] = st.text_input("Telefon", "789 563 405")
    st.session_state['mail'] = st.text_input("E-mail", "biuro@travis.pl")
    f_main = st.file_uploader("Zdjęcie główne", type=['jpg', 'png'])
    f_gal = st.file_uploader("Zdjęcia do galerii", type=['jpg', 'png'], accept_multiple_files=True)

u_tytul = st.text_input("Tytuł wycieczki")
u_termin = st.text_input("Termin")
u_plan = st.text_area("Szczegółowy program", height=150)
col_a, col_b = st.columns(2)
with col_a: u_ceny = st.text_area("Ceny i opcje", height=100)
with col_b: u_zawiera = st.text_area("Świadczenia", height=100)

if st.button("🚀 GENERUJ PDF PREMIUM"):
    if u_tytul:
        pdf = generate_pdf(u_tytul, u_termin, u_plan, u_ceny, u_zawiera, "", f_main, f_gal)
        st.download_button("📥 Pobierz gotowy PDF", data=pdf, file_name=f"Oferta_Travis_{u_tytul}.pdf", mime="application/pdf")
