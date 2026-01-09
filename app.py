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

# --- NAJSZERSZE WSPARCIE POLSKICH ZNAKÓW ---
@st.cache_data
def load_roboto_fonts():
    try:
        # Roboto ma pełne i stabilne wsparcie dla polskich znaków w ReportLab
        urls = {
            "Roboto": "https://github.com/google/fonts/raw/main/apache/roboto/Roboto-Regular.ttf",
            "Roboto-Bold": "https://github.com/google/fonts/raw/main/apache/roboto/Roboto-Bold.ttf"
        }
        for name, url in urls.items():
            res = requests.get(url)
            pdfmetrics.registerFont(TTFont(name, BytesIO(res.content)))
        return 'Roboto', 'Roboto-Bold'
    except Exception as e:
        st.error(f"Problem z czcionką: {e}")
        return 'Helvetica', 'Helvetica-Bold'

F_REG, F_BOLD = load_roboto_fonts()

# --- KOLORY ---
NAVY = colors.HexColor("#002d5a")
SOFT_GRAY = colors.HexColor("#f6f8fa") # Bardzo jasny szary
TEXT_BLACK = colors.HexColor("#121212")
WHITE = colors.white

def draw_decorations(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(SOFT_GRAY)
    canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
    
    # Fala na dole
    canvas.setFillColor(NAVY)
    p = canvas.beginPath()
    p.moveTo(0, 2.2*cm)
    p.curveTo(6*cm, 3.2*cm, 14*cm, 1.2*cm, A4[0], 2.7*cm)
    p.lineTo(A4[0], 0)
    p.lineTo(0, 0)
    p.close()
    canvas.drawPath(p, fill=1, stroke=0)
    
    # Stopka z polskimi znakami
    canvas.setFillColor(WHITE)
    canvas.setFont(F_REG, 7)
    u_tel = st.session_state.get('tel', '789 563 405')
    u_mail = st.session_state.get('mail', 'biuro@travis.pl')
    # Używamy .encode('utf-8').decode('utf-8') aby upewnić się co do kodowania
    footer_main = f"Biuro Podróży TRAVIS | tel: {u_tel} | e-mail: {u_mail}"
    canvas.drawCentredString(A4[0]/2, 1.3*cm, footer_main)
    canvas.setFont(F_BOLD, 6.5)
    canvas.drawCentredString(A4[0]/2, 0.9*cm, "Wpis do Rejestru Organizatorów i Pośredników Turystycznych nr 41059")
    canvas.restoreState()

def generate_pdf(tytul, termin, plan, ceny, zawiera, nie_zawiera, foto_main, galeria):
    buffer = BytesIO()
    # Marginesy dopasowane do fali
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=1.5*cm, rightMargin=1.5*cm, topMargin=1*cm, bottomMargin=3.5*cm)
    
    styles = getSampleStyleSheet()
    # Definicja stylów z czarnym tekstem i czcionką Roboto
    style_title = ParagraphStyle('T', fontName=F_BOLD, fontSize=22, textColor=NAVY, alignment=1, encoding='utf-8')
    style_term = ParagraphStyle('S', fontName=F_REG, fontSize=11, textColor=TEXT_BLACK, alignment=1, encoding='utf-8')
    style_h = ParagraphStyle('H', fontName=F_BOLD, fontSize=10, textColor=NAVY, spaceAfter=8, textTransform='uppercase', encoding='utf-8')
    style_p = ParagraphStyle('P', fontName=F_REG, fontSize=9, leading=13, textColor=TEXT_BLACK, encoding='utf-8')
    
    story = []
    
    # 1. LOGO - WIĘKSZE
    logo_url = "https://travis.pl/wp-content/uploads/2025/07/logo_travis500.png"
    try:
        logo = Image(BytesIO(requests.get(logo_url).content), width=7.5*cm, height=2.2*cm, kind='proportional')
        logo.hAlign = 'CENTER'
        story.append(logo)
    except: pass
    story.append(Spacer(1, 20))

    # 2. TYTUŁ I TERMIN
    story.append(Paragraph(tytul.upper(), style_title))
    story.append(Spacer(1, 15))
    story.append(Paragraph(f"📅 TERMIN: {termin}", style_term))
    story.append(Spacer(1, 20))

    # 3. ZDJĘCIE GŁÓWNE
    if foto_main:
        img = Image(foto_main, width=17.5*cm, height=7.5*cm, kind='proportional')
        img.hAlign = 'CENTER'
        story.append(img)
        story.append(Spacer(1, 25))

    # FUNKCJA DO PÓL Z MNIEJSZYM ZAOKRĄGLENIEM (5pt)
    def sharp_card(content):
        t = Table([[content]], colWidths=[17.5*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), WHITE),
            ('ROUNDEDCORNERS', [5, 5, 5, 5]), # Mniejsze zaokrąglenie
            ('LEFTPADDING', (0,0), (-1,-1), 15),
            ('RIGHTPADDING', (0,0), (-1,-1), 15),
            ('TOPPADDING', (0,0), (-1,-1), 12),
            ('BOTTOMPADDING', (0,0), (-1,-1), 12),
            ('GRID', (0,0), (-1,-1), 0.1, colors.HexColor("#e0e0e0"))
        ]))
        return t

    # 4. PROGRAM
    story.append(Paragraph("✈️ PROGRAM PODRÓŻY", style_h))
    story.append(sharp_card(Paragraph(plan.replace('\n', '<br/>'), style_p)))
    story.append(Spacer(1, 15))

    # 5. KOSZTY I ŚWIADCZENIA
    c1 = [Paragraph("💰 KOSZTY", style_h), Paragraph(ceny.replace('\n', '<br/>'), style_p)]
    c2 = [Paragraph("📋 ŚWIADCZENIA", style_h), Paragraph(zawiera.replace('\n', '<br/>'), style_p)]
    
    t_side = Table([
        [Table([[c1]], colWidths=[8.4*cm], style=[('BACKGROUND', (0,0), (-1,-1), WHITE), ('ROUNDEDCORNERS', [5,5,5,5]), ('PADDING', (0,0), (-1,-1), 10), ('GRID', (0,0), (-1,-1), 0.1, colors.HexColor("#e0e0e0"))]),
         Table([[c2]], colWidths=[8.4*cm], style=[('BACKGROUND', (0,0), (-1,-1), WHITE), ('ROUNDEDCORNERS', [5,5,5,5]), ('PADDING', (0,0), (-1,-1), 10), ('GRID', (0,0), (-1,-1), 0.1, colors.HexColor("#e0e0e0"))])]
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

    doc.addPageTemplates([PageTemplate(id='T', frames=Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height), onPage=draw_decorations)])
    doc.build(story)
    return buffer.getvalue()

# --- UI STREAMLIT ---
st.title("🏝️ Generator Travis Premium (Final Fix)")

with st.sidebar:
    st.header("Kontakt w stopce")
    st.session_state['tel'] = st.text_input("Telefon", "789 563 405")
    st.session_state['mail'] = st.text_input("E-mail", "biuro@travis.pl")
    f_main = st.file_uploader("Zdjęcie główne", type=['jpg', 'png'])
    f_gal = st.file_uploader("Dodatkowe zdjęcia", type=['jpg', 'png'], accept_multiple_files=True)

u_tytul = st.text_input("Nazwa wycieczki")
u_termin = st.text_input("Termin")
u_plan = st.text_area("Program wycieczki (Dzień po dniu)")
col_x, col_y = st.columns(2)
with col_x: u_ceny = st.text_area("Koszty uczestnictwa")
with col_y: u_zawiera = st.text_area("Świadczenia w cenie")

if st.button("🚀 GENERUJ PDF"):
    if u_tytul:
        pdf_final = generate_pdf(u_tytul, u_termin, u_plan, u_ceny, u_zawiera, "", f_main, f_gal)
        st.download_button("📥 POBIERZ OFERTĘ PDF", data=pdf_final, file_name=f"Oferta_Travis_{u_tytul}.pdf", mime="application/pdf")
    else:
        st.error("Proszę wpisać nazwę wycieczki.")
