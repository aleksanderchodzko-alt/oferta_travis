import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageTemplate, Frame
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Rect
from io import BytesIO
import requests

# --- OBSŁUGA CZCIONEK (Polskie znaki i nowoczesny krój) ---
@st.cache_data
def load_fonts():
    try:
        r_reg = requests.get("https://github.com/google/fonts/raw/main/apache/roboto/Roboto-Regular.ttf")
        r_bold = requests.get("https://github.com/google/fonts/raw/main/apache/roboto/Roboto-Bold.ttf")
        pdfmetrics.registerFont(TTFont('Roboto', BytesIO(r_reg.content)))
        pdfmetrics.registerFont(TTFont('Roboto-Bold', BytesIO(r_bold.content)))
        return 'Roboto', 'Roboto-Bold'
    except:
        return 'Helvetica', 'Helvetica-Bold'

F_REG, F_BOLD = load_fonts()

# --- KOLORY ---
NAVY = colors.HexColor("#002d5a")
VERY_LIGHT_GRAY = colors.HexColor("#fdfdfd") # Prawie białe tło strony
WHITE = colors.white
BORDER_COLOR = colors.HexColor("#eef0f2")

# --- FUNKCJA TŁA I ZAOKRĄGLONYCH BLOKÓW ---
def draw_page_setup(canvas, doc):
    canvas.saveState()
    # Bardzo jasne szare tło strony
    canvas.setFillColor(VERY_LIGHT_GRAY)
    canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
    
    # Stała stopka
    canvas.setFont(F_REG, 7)
    canvas.setFillColor(NAVY)
    footer_text = f"Biuro Podróży TRAVIS | tel: {st.session_state.get('tel', '')} | e-mail: {st.session_state.get('mail', '')}"
    canvas.drawCentredString(A4[0]/2, 1.5*cm, footer_text)
    canvas.setFont(F_BOLD, 7)
    canvas.drawCentredString(A4[0]/2, 1.1*cm, "wpis do Rejestru Organizatorów i Pośredników Turystycznych pod numerem 41059")
    canvas.restoreState()

def generate_pdf(tytul, termin, plan, ceny, zawiera, nie_zawiera, foto_main, galeria):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=1.5*cm, rightMargin=1.5*cm, topMargin=1.5*cm, bottomMargin=2.5*cm)
    
    styles = getSampleStyleSheet()
    style_title = ParagraphStyle('Title', fontName=F_BOLD, fontSize=20, textColor=NAVY, alignment=1)
    style_term = ParagraphStyle('Term', fontName=F_REG, fontSize=11, textColor=NAVY, alignment=1, spaceAfter=20)
    style_h = ParagraphStyle('H', fontName=F_BOLD, fontSize=10, textColor=NAVY, spaceAfter=8, textTransform='uppercase')
    style_p = ParagraphStyle('P', fontName=F_REG, fontSize=9, leading=13, textColor=colors.black)
    
    story = []

    # 1. LOGO NA ŚRODKU I WIĘKSZE
    logo_url = "https://travis.pl/wp-content/uploads/2025/07/logo_travis500.png"
    try:
        resp = requests.get(logo_url)
        logo = Image(BytesIO(resp.content), width=6*cm, height=1.8*cm, kind='proportional')
        logo.hAlign = 'CENTER'
        story.append(logo)
    except: pass
    story.append(Spacer(1, 20))

    # 2. BLOK TYTUŁOWY
    story.append(Paragraph(tytul, style_title))
    story.append(Paragraph(f"Termin: {termin}", style_term))

    # 3. ZDJĘCIE GŁÓWNE (Zaokrąglone krawędzie wizualnie przez margines)
    if foto_main:
        img = Image(foto_main, width=17.5*cm, height=7.5*cm, kind='proportional')
        img.hAlign = 'CENTER'
        story.append(img)
        story.append(Spacer(1, 25))

    # 4. ZAOKRĄGLONE BLOKI (Użycie tabel z rounded corners style)
    def rounded_block(content_list, width=17.5*cm):
        t = Table([[content_list]], colWidths=[width])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), WHITE),
            ('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR),
            ('LEFTPADDING', (0,0), (-1,-1), 20),
            ('RIGHTPADDING', (0,0), (-1,-1), 20),
            ('TOPPADDING', (0,0), (-1,-1), 15),
            ('BOTTOMPADDING', (0,0), (-1,-1), 15),
            ('ROUNDEDCORNERS', [15, 15, 15, 15]) # Efekt zaokrąglenia
        ]))
        return t

    # PROGRAM
    story.append(Paragraph("Program podróży", style_h))
    story.append(rounded_block(Paragraph(plan.replace('\n', '<br/>'), style_p)))
    story.append(Spacer(1, 15))

    # KOSZTY I ŚWIADCZENIA (Dwa bloki obok siebie)
    col_w = 8.5*cm
    c1 = [Paragraph("Koszty", style_h), Paragraph(ceny.replace('\n', '<br/>'), style_p)]
    c2 = [Paragraph("Cena zawiera", style_h), Paragraph(zawiera.replace('\n', '<br/>'), style_p)]
    
    t_split = Table([[rounded_block(c1, width=col_w), rounded_block(c2, width=col_w)]], colWidths=[9*cm, 9*cm])
    t_split.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('LEFTPADDING', (0,0), (-1,-1), 0)]))
    story.append(t_split)

    # 5. GALERIA
    if galeria:
        story.append(Spacer(1, 15))
        story.append(Paragraph("Galeria zdjęć", style_h))
        imgs = []
        row = []
        for i, f in enumerate(galeria):
            img = Image(f, width=5.5*cm, height=4*cm, kind='proportional')
            row.append(img)
            if (i + 1) % 3 == 0:
                imgs.append(row)
                row = []
        if row: imgs.append(row)
        t_gal = Table(imgs, colWidths=[5.8*cm]*3)
        story.append(t_gal)

    # Budowa dokumentu
    doc.addPageTemplates([PageTemplate(id='T', frames=Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height), onPage=draw_page_setup)])
    doc.build(story)
    return buffer.getvalue()

# --- INTERFEJS STREAMLIT ---
st.title("✈️ Travis Premium Generator")

with st.sidebar:
    st.header("Dane biura")
    st.session_state['tel'] = st.text_input("Telefon", "789 563 405")
    st.session_state['mail'] = st.text_input("E-mail", "biuro@travis.pl")
    f_main = st.file_uploader("Zdjęcie główne", type=['jpg', 'png'])
    f_gal = st.file_uploader("Dodaj zdjęcia do galerii", type=['jpg', 'png'], accept_multiple_files=True)

u_tytul = st.text_input("Tytuł wycieczki", placeholder="np. MALTA - WYSPA SŁOŃCA")
u_termin = st.text_input("Termin", placeholder="np. MAJ 2026")
u_plan = st.text_area("Szczegółowy program", height=150)
col_a, col_b = st.columns(2)
with col_a:
    u_ceny = st.text_area("Cennik", height=100)
with col_b:
    u_zawiera = st.text_area("Świadczenia", height=100)

if st.button("🚀 GENERUJ NOWOCZESNY PDF"):
    if u_tytul:
        pdf = generate_pdf(u_tytul, u_termin, u_plan, u_ceny, u_zawiera, "", f_main, f_gal)
        st.download_button("📥 Pobierz PDF Premium", data=pdf, file_name=f"Oferta_Travis_{u_tytul}.pdf", mime="application/pdf")
    else:
        st.error("Wpisz tytuł!")
