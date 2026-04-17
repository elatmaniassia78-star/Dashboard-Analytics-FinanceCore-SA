import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import streamlit as st
import plotly.express as px
from script.db import run_query
from script.requete import kpis_query, monthly_query, agence_query, segment_query

st.title("📊 Vue Exécutive")
filters = st.session_state.get("filters", {
    "agence": None,
    "segment": None,
    "year_start": 2000,
    "year_end": 2100
})

# KPIs
kpi = run_query(kpis_query(), filters)
filters = st.session_state.get("filters")
st.write("FILTERS:", filters)
st.write("KPI SHAPE:", kpi.shape)
st.write(kpi)
col1, col2, col3, col4 = st.columns(4)

if kpi.empty:
    st.warning("لا توجد بيانات حسب الفلاتر المختارة")
    st.stop()

col1.metric("Transactions", int(kpi.iloc[0,0]))
col2.metric("CA", round(kpi.iloc[0,1],2))
col3.metric("Clients", int(kpi.iloc[0,2]))
col4.metric("Marge", round(kpi.iloc[0,3],2))
col2.metric("CA", round(kpi.iloc[0,1],2))
col3.metric("Clients", int(kpi.iloc[0,2]))
col4.metric("Marge", round(kpi.iloc[0,3],2))

# Line chart
df_month = run_query(monthly_query(), filters)
fig = px.line(df_month, x="mois", y=["debit","credit"], title="Evolution")
st.plotly_chart(fig, use_container_width=True)

# Bar
df_agence = run_query(agence_query(), filters)
fig2 = px.bar(df_agence, x="nom_agence", y="total_ca", title="CA par agence")
st.plotly_chart(fig2)

# Pie
df_segment = run_query(segment_query(), filters)
fig3 = px.pie(df_segment, names="nom_segment", values="total")
st.plotly_chart(fig3)
sql, params = kpis_query(filters)
kpi = run_query(sql, params)