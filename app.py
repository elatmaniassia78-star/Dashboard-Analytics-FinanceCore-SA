import streamlit as st
import pandas as pd
import plotly.express as px

# Import modules
from modules.database import get_db_connection
from modules.processor import load_data

# CONFIG
st.set_page_config(page_title="FinanceCore Dashboard", layout="wide")

# DB CONNECTION
engine = get_db_connection()

# LOAD DATA
df_trans, df_clients = load_data(engine)

# Check data
if df_trans.empty or df_clients.empty:
    st.warning("En attente des données de la base PostgreSQL...")
    st.stop()

# SIDEBAR
st.sidebar.title("🏦 FinanceCore SA")
st.sidebar.markdown("---")

# Navigation
page = st.sidebar.radio("Navigation", ["Vue Executive", "Analyse des Risques"])

st.sidebar.markdown("---")
st.sidebar.subheader("Filtres")

# Filters values
agences = ["Toutes"] + list(df_trans['agence'].dropna().unique())
segments = ["Tous"] + list(df_trans['segment'].dropna().unique())
produits = ["Tous"] + list(df_trans['produit_bancaire'].dropna().unique())
annees = sorted(list(df_trans['annee'].dropna().unique()))

# Filters UI
filtre_agence = st.sidebar.selectbox("Agence", agences)
filtre_segment = st.sidebar.selectbox("Segment", segments)
filtre_produit = st.sidebar.selectbox("Produit", produits)

# Year filter
if len(annees) > 1:
    filtre_annee = st.sidebar.slider("Année", min(annees), max(annees), (min(annees), max(annees)))
else:
    filtre_annee = (annees[0], annees[0]) if annees else (2022, 2024)

# FILTERING
mask_t = pd.Series(True, index=df_trans.index)
mask_c = pd.Series(True, index=df_clients.index)

if filtre_agence != "Toutes":
    mask_t &= (df_trans['agence'] == filtre_agence)
    mask_c &= (df_clients['agence'] == filtre_agence)

if filtre_segment != "Tous":
    mask_t &= (df_trans['segment'] == filtre_segment)
    mask_c &= (df_clients['segment'] == filtre_segment)

if filtre_produit != "Tous":
    mask_t &= (df_trans['produit_bancaire'] == filtre_produit)

mask_t &= (df_trans['annee'] >= filtre_annee[0]) & (df_trans['annee'] <= filtre_annee[1])

# Apply filters
df_f_trans = df_trans[mask_t]
df_f_clients = df_clients[mask_c]

# PAGE 1: VUE EXECUTIVE
if page == "Vue Executive":
    st.title("📊 Vue Executive - Performances Globales")

    col1, col2, col3, col4 = st.columns(4)

    # KPIs
    vol_total = len(df_f_trans)
    ca_total = df_f_trans[df_f_trans['type_transaction'] == 'Credit']['montant'].sum()
    clients_actifs = df_f_trans['id_client'].nunique()
    marge_estimee = ca_total * 0.15

    col1.metric("Volume Transactions", f"{vol_total:,}")
    col2.metric("Chiffre d'Affaires", f"{ca_total:,.0f} €")
    col3.metric("Clients Actifs", f"{clients_actifs:,}")
    col4.metric("Marge Estimée (15%)", f"{marge_estimee:,.0f} €")

    st.markdown("---")

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("📈 Évolution Mensuelle")
        evo = df_f_trans.groupby(['mois_annee', 'type_transaction'])['montant'].sum().reset_index()
        fig_line = px.line(evo, x='mois_annee', y='montant', color='type_transaction', markers=True)
        st.plotly_chart(fig_line, use_container_width=True)

        st.subheader("🏦 CA par Agence & Produit")
        bar_data = df_f_trans[df_f_trans['type_transaction'] == 'Credit'] \
            .groupby(['agence', 'produit_bancaire'])['montant'].sum().reset_index()
        fig_bar = px.bar(bar_data, x='agence', y='montant', color='produit_bancaire', barmode='group')
        st.plotly_chart(fig_bar, use_container_width=True)

    with c2:
        st.subheader("👥 Répartition Clients")
        pie_data = df_f_trans.groupby('segment')['id_client'].nunique().reset_index()
        fig_pie = px.pie(pie_data, names='segment', values='id_client', hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)

# PAGE 2: RISQUES
elif page == "Analyse des Risques":
    st.title("⚠️ Analyse des Risques")

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Correlation")
        corr = df_f_clients[['score_credit', 'montant_total', 'taux_rejet']].corr()
        fig_heat = px.imshow(corr, text_auto=True)
        st.plotly_chart(fig_heat, use_container_width=True)

    with c2:
        st.subheader("Score vs Montant")
        fig_scatter = px.scatter(
            df_f_clients,
            x='score_credit',
            y='montant_total',
            color='categorie_risque',
            hover_data=['nom', 'taux_rejet']
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    st.subheader("Top Clients à Risque")

    top_risques = df_f_clients.sort_values(
        by=['score_credit', 'taux_rejet'],
        ascending=[True, False]
    ).head(10)

    st.dataframe(top_risques)

    st.download_button(
        "📥 Export CSV",
        data=top_risques.to_csv(index=False).encode('utf-8'),
        file_name="clients_risque.csv"
    )