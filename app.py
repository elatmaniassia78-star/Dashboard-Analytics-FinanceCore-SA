import streamlit as st
from script.db import run_query
import sys
import os

sys.path.append(os.path.abspath("."))
st.set_page_config(page_title="Finance Dashboard", layout="wide")

st.title("📊 FinanceCore Dashboard")

df = run_query("SELECT * FROM v_kpi_transactions")
df2 = run_query("""
SELECT 
    c.nom_segment
FROM client c
""")
df3= run_query("""
SELECT 
    t.annee
FROM transaction t
""")
# Sidebar
st.sidebar.title("Filtres")

agence = st.sidebar.selectbox("agence", ["All"] + list(df["nom_agence"].dropna().unique()))
segment = st.sidebar.selectbox("segment", ["All"] + list(df2["nom_segment"].dropna().unique()))

year_min, year_max = int(df3["annee"].min()), int(df3["annee"].max())
years = st.sidebar.slider("Année", year_min, year_max, (year_min, year_max))

params = {
    "agence": None if agence == "All" else agence,
    "segment": None if segment == "All" else segment,
    "year_start": years[0],
    "year_end": years[1]
}

st.session_state["filters"] = params

# Export global
st.sidebar.download_button(
    "📥 Export CSV",
    df.to_csv(index=False),
    file_name="data.csv"
)

st.write("Use sidebar to navigate 👈")



