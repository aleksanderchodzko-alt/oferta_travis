import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, Frame, PageTemplate
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from io import BytesIO

# --- USTAWIENIA KOLORYSTYCZNE TRAVIS ---
COLOR_NAVY = colors.HexColor("#002d5a")
COLOR_BG = colors.HexColor("#f4f4f4")  # Lekko szare tło
COLOR_WHITE = colors.white

# --- FUNKCJA TŁA I STOPKI (ZASZYTA) ---
def draw_fixed_elements(canvas, doc):
    canvas.saveState()
    # 1. Rysowanie tła na całą stronę
    canvas.setFillColor(COLOR_BG)
    canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
    
    # 2. Ozdobnik graficzny (pasek boczny lub górny)
    canvas.setFillColor(COLOR_NAVY)
    canvas.rect(0, A4[1]-0.5*cm, A4[0], 0.5*cm, fill=1, stroke=0) # Pasek na samej górze
    
    # 3. Stopka (Poprawiona i sformatowana)
    footer_y = 1.5 * cm
    canvas.setFont("Helvetica-Bold", 8)
    canvas.setFillColor(COLOR_NAVY)
    canvas.drawCentredString(A4[0]/2, footer_y + 15, f"Biuro Podróży TRAVIS | tel: {st.session_state.get('tel', '')} | e-mail: {st.session_state.get('mail', '')}")
    canvas.setFont("Helvetica", 7)
    canvas.drawCentredString(A4[0]/2, footer_y + 5, "wpis do Rejestru Organizatorów i Pośredników Turystycznych pod numerem 41059")
    
    # Linia nad stopką
    canvas.setStrokeColor(COLOR_NAVY)
    canvas.setLineWidth(0.5)
    canvas.line(2*cm, footer_y + 25, A4[0]-2*cm, footer_y + 25)
    canvas.restoreState()

# --- GENERATOR PDF ---
def generate_pdf(tytul, termin, plan, cennik_data, zawiera, nie_zawiera, foto):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=1.5*cm, rightMargin=1.5*cm, topMargin=2*cm, bottomMargin=3*cm)
    
    styles = getSampleStyleSheet()
    style_title = ParagraphStyle('T', fontName='Helvetica-Bold', fontSize=22, textColor=COLOR_NAVY, spaceAfter=10, alignment=1)
    style_h = ParagraphStyle('H', fontName='Helvetica-Bold', fontSize=14, textColor=COLOR_NAVY, spaceBefore=15, spaceAfter=8)
    style_p = ParagraphStyle('P', fontName='Helvetica', fontSize=10, leading=14, textColor=colors.black)
    style_inc = ParagraphStyle('Inc', fontName='Helvetica', fontSize=9, leading=12, textColor=colors.HexColor("#1e5631"))
    style_exc = ParagraphStyle('Exc', fontName='Helvetica', fontSize=9, leading=12, textColor=colors.HexColor("#8b0000"))

    story = []

    # 1. LOGO (Z zachowaniem proporcji)
    logo_url = "https://travis.pl/wp-content/uploads/2025/07/logo_travis500.png"
    logo = Image(logo_url, width=4.5*cm, height=1.3*cm) # Zgrabne i mniejsze
    logo.hAlign = 'LEFT'
    story.append(logo)
    story.append(Spacer(1, 10))

    # 2. ZDJĘCIE GŁÓWNE
    if foto:
        img = Image(foto, width=17*cm, height=8*cm, kind='proportional')
        img.hAlign = 'CENTER'
        story.append(img)
    
    story.append(Spacer(1, 20))
    story.append(Paragraph(tytul.upper(), style_title))
    story.append(Paragraph(f"TERMIN: {termin}", ParagraphStyle('Sub', alignment=1, fontSize=12, textColor=COLOR_NAVY)))
    story.append(Spacer(1, 20))

    # 3. PLAN WYCIECZKI (W białym bloku)
    story.append(Paragraph("PROGRAM WYCIECZKI", style_h))
    plan_box = [[Paragraph(plan.replace('\n', '<br/>'), style_p)]]
    t_plan = Table(plan_box, colWidths=[17*cm])
    t_plan.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), COLOR_WHITE),
        ('BOX', (0,0), (-1,-1), 0.5, COLOR_NAVY),
        ('LEFTPADDING', (0,0), (-1,-1), 15),
        ('RIGHTPADDING', (0,0), (-1,-1), 15),
        ('TOPPADDING', (0,0), (-1,-1), 15),
        ('BOTTOMPADDING', (0,0), (-1,-1), 15),
    ]))
    story.append(t_plan)

    # 4. TABELA CEN (Zgrabniejsza i mniejsza)
    story.append(Paragraph("KOSZT UCZESTNICTWA", style_h))
    t_prices = Table(cennik_data, colWidths=[6*cm, 4*cm])
    t_prices.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), COLOR_NAVY),
        ('TEXTCOLOR', (0,0), (-1,0), COLOR_WHITE),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BACKGROUND', (0,1), (-1,-1), COLOR_WHITE),
        ('GRID', (0,0), (-1,-1), 0.5, COLOR_NAVY),
        ('FONTSIZE', (0,0), (-1,-1), 9),
    ]))
    t_prices.hAlign = 'LEFT'
    story.append(t_prices)

    # 5. ZAWIERA / NIE ZAWIERA
    story.append(Spacer(1, 20))
    data_inf = [
        [Paragraph("CENA ZAWIERA", style_h), Paragraph("CENA NIE ZAWIERA", style_h)],
        [Paragraph(zawiera.replace('\n', '<br/>'), style_inc), Paragraph(nie_zawiera.replace('\n', '<br/>'), style_exc)]
    ]
    t_inf = Table(data_inf, colWidths=[8.5*cm, 8.5*cm])
    t_inf.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    story.append(t_inf)

    # Budowanie dokumentu z tłem
    doc.addPageTemplates([PageTemplate(id='Travis', frames=Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height), onPage=draw_fixed_elements)])
    doc.build(story)
    return buffer.getvalue()

# --- INTERFEJS STREAMLIT ---
st.title("🏝️ Generator Ofert Travis")

with st.sidebar:
    st.header("⚙️ Konfiguracja")
    st.session_state['tel'] = st.text_input("Telefon", "789 563 405")
    st.session_state['mail'] = st.text_input("E-mail", "biuro@travis.pl")
    foto = st.file_uploader("Zdjęcie główne", type=['jpg', 'png'])

col1, col2 = st.columns(2)
with col1:
    u_tytul = st.text_input("Nazwa wycieczki")
    u_termin = st.text_input("Termin")
with col2:
    u_ceny = st.text_area("Ceny (np. 46-50 os. | 3395 zł)", height=70)

u_plan = st.text_area("Plan wycieczki", height=200)
u_zawiera = st.text_area("Zawiera", height=100)
u_nie_zawiera = st.text_area("Nie zawiera", height=100)

if st.button("🚀 GENERUJ NOWOCZESNY PDF"):
    # Przygotowanie danych tabeli cen
    prices = [["Grupa", "Cena"]]
    for line in u_ceny.split('\n'):
        if '|' in line: prices.append(line.split('|'))
    
    pdf = generate_pdf(u_tytul, u_termin, u_plan, prices, u_zawiera, u_nie_zawiera, foto)
    st.download_button("📥 Pobierz gotowy PDF", data=pdf, file_name="oferta_travis.pdf", mime="application/pdf")
