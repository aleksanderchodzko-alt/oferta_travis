import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageTemplate, Frame
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO
import requests

# --- KOLORY TRAVIS ---
NAVY = colors.HexColor("#002d5a")
BG_GRAY = colors.HexColor("#f8f9fa")
WHITE = colors.white

def draw_background(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(BG_GRAY)
    canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
    
    # Zaszyta stopka na każdej stronie
    footer_y = 1.2 * cm
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(NAVY)
    canvas.drawCentredString(A4[0]/2, footer_y + 10, f"Biuro Podróży TRAVIS | tel: {st.session_state.get('tel', '')} | e-mail: {st.session_state.get('mail', '')}")
    canvas.setFont("Helvetica-Bold", 7)
    canvas.drawCentredString(A4[0]/2, footer_y, "wpis do Rejestru Organizatorów i Pośredników Turystycznych pod numerem 41059")
    canvas.restoreState()

def generate_modern_pdf(tytul, termin, plan, ceny_data, zawiera, nie_zawiera, foto):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm, topMargin=1.5*cm, bottomMargin=2.5*cm)
    
    styles = getSampleStyleSheet()
    # Mniejsze treści (fontSize 9-10)
    style_title = ParagraphStyle('T', fontName='Helvetica-Bold', fontSize=18, textColor=NAVY, alignment=1, spaceAfter=12)
    style_h = ParagraphStyle('H', fontName='Helvetica-Bold', fontSize=11, textColor=NAVY, spaceBefore=10, spaceAfter=6)
    style_p = ParagraphStyle('P', fontName='Helvetica', fontSize=9, leading=12, textColor=colors.black)
    style_small = ParagraphStyle('S', fontName='Helvetica', fontSize=8, leading=10)

    story = []

    # 1. LOGO - Pobieranie wysokiej jakości, aby uniknąć rozmycia
    logo_url = "https://travis.pl/wp-content/uploads/2025/07/logo_travis500.png"
    try:
        resp = requests.get(logo_url)
        logo_data = BytesIO(resp.content)
        logo = Image(logo_data, width=4*cm, height=1.1*cm, kind='proportional')
        logo.hAlign = 'LEFT'
        story.append(logo)
    except:
        st.warning("Nie udało się załadować logo. Sprawdź połączenie.")

    story.append(Spacer(1, 15))

    # 2. ZDJĘCIE GŁÓWNE (Karta)
    if foto:
        img = Image(foto, width=17*cm, height=7*cm, kind='proportional')
        img.hAlign = 'CENTER'
        story.append(img)
        story.append(Spacer(1, 15))

    # 3. TYTUŁ I TERMIN
    story.append(Paragraph(tytul.upper(), style_title))
    story.append(Paragraph(f"TERMIN: {termin}", ParagraphStyle('Sub', alignment=1, fontSize=10, textColor=NAVY)))
    story.append(Spacer(1, 20))

    # 4. PLAN WYCIECZKI (Biała karta z cieniem/obramowaniem)
    story.append(Paragraph("PROGRAM WYCIECZKI", style_h))
    plan_table = Table([[Paragraph(plan.replace('\n', '<br/>'), style_p)]], colWidths=[17*cm])
    plan_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), WHITE),
        ('LEFTPADDING', (0,0), (-1,-1), 15),
        ('RIGHTPADDING', (0,0), (-1,-1), 15),
        ('TOPPADDING', (0,0), (-1,-1), 15),
        ('BOTTOMPADDING', (0,0), (-1,-1), 15),
        ('LINEBELOW', (0,0), (-1,-1), 1, NAVY), # Akcent na dole karty
    ]))
    story.append(plan_table)
    story.append(Spacer(1, 15))

    # 5. CENNIK (Mniejszy i zgrabniejszy)
    story.append(Paragraph("KOSZTY", style_h))
    t_prices = Table(ceny_data, colWidths=[5*cm, 3*cm])
    t_prices.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), NAVY),
        ('TEXTCOLOR', (0,0), (-1,0), WHITE),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('BACKGROUND', (0,1), (-1,-1), WHITE),
        ('GRID', (0,0), (-1,-1), 0.2, NAVY),
    ]))
    t_prices.hAlign = 'LEFT'
    story.append(t_prices)
    story.append(Spacer(1, 15))

    # 6. ZAWIERA / NIE ZAWIERA (Dwie białe kolumny)
    data_inf = [
        [Paragraph("CENA ZAWIERA", style_h), Paragraph("CENA NIE ZAWIERA", style_h)],
        [Table([[Paragraph(zawiera.replace('\n', '<br/>'), style_small)]], colWidths=[8*cm], style=[('BACKGROUND',(0,0),(-1,-1), WHITE), ('BOX',(0,0),(-1,-1),0.1,NAVY)]),
         Table([[Paragraph(nie_zawiera.replace('\n', '<br/>'), style_small)]], colWidths=[8*cm], style=[('BACKGROUND',(0,0),(-1,-1), WHITE), ('BOX',(0,0),(-1,-1),0.1,NAVY)])]
    ]
    t_inf = Table(data_inf, colWidths=[8.5*cm, 8.5*cm])
    t_inf.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    story.append(t_inf)

    # Budowa
    doc.addPageTemplates([PageTemplate(id='Travis', frames=Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height), onPage=draw_background)])
    doc.build(story)
    return buffer.getvalue()

# --- INTERFEJS ---
st.title("🏗️ Nowoczesny Generator Travis")

with st.sidebar:
    st.header("⚙️ Ustawienia")
    st.session_state['tel'] = st.text_input("Telefon biura", "789 563 405")
    st.session_state['mail'] = st.text_input("E-mail biura", "biuro@travis.pl")
    foto = st.file_uploader("Zdjęcie główne", type=['jpg', 'png'])

col1, col2 = st.columns(2)
with col1:
    u_tytul = st.text_input("Kierunek")
    u_termin = st.text_input("Termin")
with col2:
    u_ceny = st.text_area("Ceny (np. 46-50 os. | 3395 zł)", height=80)

u_plan = st.text_area("Plan", height=150)
u_zawiera = st.text_area("Cena zawiera", height=100)
u_nie_zawiera = st.text_area("Cena nie zawiera", height=100)

if st.button("🚀 GENERUJ PDF"):
    prices = [["Wielkość grupy", "Cena"]]
    for line in u_ceny.split('\n'):
        if '|' in line: prices.append(line.split('|'))
    
    pdf = generate_modern_pdf(u_tytul, u_termin, u_plan, prices, u_zawiera, u_nie_zawiera, foto)
    st.download_button("📥 Pobierz profesjonalną ofertę", data=pdf, file_name=f"Oferta_Travis_{u_tytul}.pdf", mime="application/pdf")
