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

# --- OBSŁUGA CZCIONEK (POLSKIE ZNAKI) ---
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
SOFT_GRAY = colors.HexColor("#f9f9fb")
WHITE = colors.white

# --- ELEMENTY GRAFICZNE (FALA I STOPKA) ---
def draw_page_decorations(canvas, doc):
    canvas.saveState()
    # Tło strony
    canvas.setFillColor(SOFT_GRAY)
    canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
    
    # Rysowanie fali (element graficzny)
    canvas.setFillColor(NAVY)
    p = canvas.beginPath()
    p.moveTo(0, 2*cm)
    p.curveTo(5*cm, 3*cm, 15*cm, 1*cm, A4[0], 2.5*cm)
    p.lineTo(A4[0], 0)
    p.lineTo(0, 0)
    p.close()
    canvas.drawPath(p, fill=1, stroke=0)
    
    # Stopka
    canvas.setFillColor(WHITE)
    canvas.setFont(F_REG, 7)
    u_tel = st.session_state.get('tel', '789 563 405')
    u_mail = st.session_state.get('mail', 'biuro@travis.pl')
    
    canvas.drawCentredString(A4[0]/2, 1.2*cm, f"TRAVIS | tel: {u_tel} | e-mail: {u_mail}")
    canvas.setFont(F_BOLD, 6)
    canvas.drawCentredString(A4[0]/2, 0.8*cm, "wpis do Rejestru Organizatorów i Pośredników Turystycznych nr 41059")
    
    # Mini logo w stopce (opcjonalne, małe białe napisy)
    canvas.restoreState()

def generate_pdf(tytul, termin, plan, ceny, zawiera, nie_zawiera, foto_main, galeria):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=1.5*cm, rightMargin=1.5*cm, topMargin=1.2*cm, bottomMargin=3.5*cm)
    
    styles = getSampleStyleSheet()
    style_title = ParagraphStyle('T', fontName=F_BOLD, fontSize=20, textColor=NAVY, alignment=1)
    style_term = ParagraphStyle('S', fontName=F_REG, fontSize=11, textColor=NAVY, alignment=1, spaceAfter=20)
    style_h = ParagraphStyle('H', fontName=F_BOLD, fontSize=10, textColor=NAVY, spaceAfter=6, textTransform='uppercase')
    style_p = ParagraphStyle('P', fontName=F_REG, fontSize=8.5, leading=12, textColor=colors.black)
    
    story = []
    logo_url = "https://travis.pl/wp-content/uploads/2025/07/logo_travis500.png"

    # 1. LOGO GŁÓWNE
    try:
        logo = Image(BytesIO(requests.get(logo_url).content), width=5.5*cm, height=1.5*cm, kind='proportional')
        logo.hAlign = 'CENTER'
        story.append(logo)
    except: pass
    story.append(Spacer(1, 15))

    # 2. TYTUŁ
    story.append(Paragraph(tytul, style_title))
    story.append(Paragraph(f"Termin: {termin}", style_term))

    # 3. ZDJĘCIE GŁÓWNE
    if foto_main:
        img = Image(foto_main, width=17.5*cm, height=7*cm, kind='proportional')
        img.hAlign = 'CENTER'
        story.append(img)
        story.append(Spacer(1, 20))

    # FUNKCJA DO ZAOKRĄGLONYCH BLOKÓW
    def rounded_card(content):
        t = Table([[content]], colWidths=[17.5*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), WHITE),
            ('ROUNDEDCORNERS', [12, 12, 12, 12]),
            ('LEFTPADDING', (0,0), (-1,-1), 15),
            ('RIGHTPADDING', (0,0), (-1,-1), 15),
            ('TOPPADDING', (0,0), (-1,-1), 12),
            ('BOTTOMPADDING', (0,0), (-1,-1), 12),
        ]))
        return t

    # 4. PROGRAM
    story.append(Paragraph("Program wycieczki", style_h))
    story.append(rounded_card(Paragraph(plan.replace('\n', '<br/>'), style_p)))
    story.append(Spacer(1, 15))

    # 5. CENA I ŚWIADCZENIA (Dwa bloki)
    c1 = [Paragraph("Koszty", style_h), Paragraph(ceny.replace('\n', '<br/>'), style_p)]
    c2 = [Paragraph("Świadczenia", style_h), Paragraph(zawiera.replace('\n', '<br/>'), style_p)]
    
    # Małe zaokrąglone bloki obok siebie
    t_side = Table([
        [Table([[c1]], colWidths=[8.4*cm], style=[('BACKGROUND', (0,0), (-1,-1), WHITE), ('ROUNDEDCORNERS', [12,12,12,12]), ('PADDING', (0,0), (-1,-1), 10)]),
         Table([[c2]], colWidths=[8.4*cm], style=[('BACKGROUND', (0,0), (-1,-1), WHITE), ('ROUNDEDCORNERS', [12,12,12,12]), ('PADDING', (0,0), (-1,-1), 10)])]
    ], colWidths=[8.7*cm, 8.7*cm])
    story.append(t_side)

    # 6. GALERIA
    if galeria:
        story.append(Spacer(1, 15))
        story.append(Paragraph("Galeria", style_h))
        row = []
        g_data = []
        for i, f in enumerate(galeria):
            img = Image(f, width=5.5*cm, height=3.5*cm, kind='proportional')
            row.append(img)
            if (i + 1) % 3 == 0:
                g_data.append(row)
                row = []
        if row: g_data.append(row)
        story.append(Table(g_data, colWidths=[5.8*cm]*3))

    doc.addPageTemplates([PageTemplate(id='Travis', frames=Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height), onPage=draw_page_decorations)])
    doc.build(story)
    return buffer.getvalue()

# --- STREAMLIT UI ---
st.title("🌊 Generator Travis Premium")

with st.sidebar:
    st.header("Dane kontaktowe")
    st.session_state['tel'] = st.text_input("Telefon", "789 563 405")
    st.session_state['mail'] = st.text_input("E-mail", "biuro@travis.pl")
    f_main = st.file_uploader("Zdjęcie główne", type=['jpg', 'png'])
    f_gal = st.file_uploader("Zdjęcia do galerii", type=['jpg', 'png'], accept_multiple_files=True)

u_tytul = st.text_input("Tytuł")
u_termin = st.text_input("Termin")
u_plan = st.text_area("Plan podróży")
col1, col2 = st.columns(2)
with col1: u_ceny = st.text_area("Ceny")
with col2: u_zawiera = st.text_area("Świadczenia")

if st.button("🚀 GENERUJ PDF"):
    if u_tytul:
        pdf = generate_pdf(u_tytul, u_termin, u_plan, u_ceny, u_zawiera, "", f_main, f_gal)
        st.download_button("📥 Pobierz PDF", data=pdf, file_name=f"Oferta_{u_tytul}.pdf", mime="application/pdf")
