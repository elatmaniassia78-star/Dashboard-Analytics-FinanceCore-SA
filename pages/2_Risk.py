import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import streamlit as st
import plotly.express as px
from script.db import run_query
from script.requete import risk_query, top_risk_clients

st.title(" Analyse des Risques")

df = run_query(risk_query())

# Heatmap
corr = df[["score_credit_client", "montant"]].corr()
fig = px.imshow(corr, text_auto=True, title="Corrélation")
st.plotly_chart(fig, use_container_width=True)

# Scatter
fig2 = px.scatter(
    df,
    x="score_credit_client",
    y="montant",
    color="categorie_risque",
    title="Score vs Montant"
)
st.plotly_chart(fig2, use_container_width=True)

# Top clients
df_top = run_query(top_risk_clients())

def color_score(val):
    if val < 580:
        return "color:red"
    elif val < 700:
        return "color:orange"
    return "color:green"

st.subheader("Top 10 clients à risque")
st.dataframe(df_top.style.applymap(color_score, subset=["score_credit_client"]))

# Export
st.download_button(
    "📥 Télécharger CSV",
    df_top.to_csv(index=False),
    file_name="clients_risque.csv"
)