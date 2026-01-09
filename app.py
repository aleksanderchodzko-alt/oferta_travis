import streamlit as st

st.set_page_config(page_title="TRAVIS - Generator Ofert", page_icon="✈️")

st.title("🏝️ Generator Ofert: TRAVIS BIURO PODRÓŻY")
st.markdown("---")

with st.sidebar:
    st.header("⚙️ Ustawienia")
    tytul = st.text_input("Tytuł", "MALTA 4 DNI - City Break")
    termin = st.text_input("Termin", "27 czerwca - 1 lipca")
    c1 = st.text_input("46-50 osób", "3 395,00 zł")
    c2 = st.text_input("40-45 osób", "3 470,00 zł")
    c3 = st.text_input("35-39 osób", "3 545,00 zł")

st.header(f"📍 {tytul}")
st.write(f"📅 **Termin:** {termin}")

col1, col2 = st.columns(2)
with col1:
    st.subheader("🗺️ Program")
    st.markdown("**Dzień 1:** Olsztyn -> Malta. Transfer i kolacja.")
    st.markdown("**Dzień 2:** Valletta (Katedra św. Jana), Mdina i Rotunda.")
with col2:
    st.write("")
    st.markdown("**Dzień 3:** Całodniowe Gozo: Victoria, Cytadela i solniska.")
    st.markdown("**Dzień 4:** Błękitna Grota, Klify Dingli i Hagar Qim.")

st.markdown("---")
st.subheader("💵 Koszty")
st.table({
    "Liczba osób": ["46-50 osób", "40-45 osób", "35-39 osób"],
    "Cena za osobę": [c1, c2, c3]
})

st.info("💡 **Cena zawiera:** Przelot (8kg+20kg), transfery z Olsztyna, 3 noclegi (HB), ubezpieczenie i opiekę pilota.")
st.warning("⚠️ **Dodatkowo płatne (ok. 130 euro):** Bilety wstępu, lokalni przewodnicy i rejsy.")
