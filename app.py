import streamlit as st
from flights import run_search, get_best_prices

st.set_page_config(page_title="Monitor de Voos BSB", layout="wide")

st.title("✈️ Monitor de Passagens - BSB")

if st.button("🔄 Atualizar preços agora"):
    with st.spinner("Buscando preços..."):
        run_search()
    st.success("Atualizado com sucesso!")

st.subheader("🔥 Menores preços históricos")

df = get_best_prices()

if df.empty:
    st.warning("Nenhum dado ainda. Clique em atualizar.")
else:
    st.dataframe(df, use_container_width=True)
