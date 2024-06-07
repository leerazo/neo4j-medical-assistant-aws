import time

import numpy as np 
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from neo4j_driver import run_query
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Intelligent Medical Assistant",
    page_icon="🧠",
    layout="wide",
)

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto&display=swap');
    </style>
    <div style='text-align: center; font-size: 2.5rem; font-weight: 600; font-family: "Roboto"; color: #018BFF; line-height:1; '>Intelligent Medical Assistant</div>
""", unsafe_allow_html=True)

@st.cache_data
def get_data() -> pd.DataFrame:
    return run_query("""
      MATCH (n:Case) return n.id as Id, 
      n.summary as Summary ORDER BY Id""")

df_cases = get_data()
placeholder = st.empty()

with placeholder.container():
        df_diseases = run_query("""MATCH (n:Disease) return n.name as name""")
        df_body_systems = run_query("""MATCH (n:BodySystem) return n.name as name""")
        df_patients = run_query("""MATCH (n:Person) return n.id as name""")

        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric(
            label="Cases",
            value=len(df_cases)
        )
        kpi2.metric(
            label="Patients",
            value=len(df_patients)
        )
        kpi3.metric(
            label="Diseases",
            value=len(df_diseases)
        )    
        kpi4.metric(
            label="Body Systems",
            value=len(df_body_systems)
        )
    
        ep_team_col = st.columns(1)
        st.markdown("### Patients, Diseases & Affected Body Parts (Top N)")
        df_te_1 = run_query("""
            MATCH (e:BodySystem) 
            return e.id as id, e.name as label, '#33a02c' as color""")
        df_te_2 = run_query("""
            MATCH (t:Disease) 
            return t.id as id, t.name as label, '#1f78b4' as color""")
        df_te_3 = run_query("""
            MATCH (t:Person) 
            return t.id as id, t.id + ' (' + t.gender + ')' as label, '#fdbf6f' as color""")
        df_te = pd.concat([df_te_1, df_te_2], ignore_index=True)
        df_te = pd.concat([df_te, df_te_3], ignore_index=True)
        df_dis_bs = run_query("""
            MATCH (:Person)-[:HAS_DISEASE]->(d:Disease)-[a:AFFECTS]->(t:BodySystem)
            return DISTINCT t.id as source, d.id as target, count(a) as value, 
                '#a6cee3' as link_color LIMIT 50""")
        df_dis_patient = run_query(f"""
            MATCH (p:Person)-[:HAS_DISEASE]->(d:Disease)-[a:AFFECTS]->(t:BodySystem)
            WHERE t.id in [{','.join(f"'{x}'" for x in df_dis_bs['source'])}]
            return d.id as source, p.id as target, count(d) as value, 
                '#fdbf6f' as link_color LIMIT 50""")
        df_dis_bs_patient = pd.concat([df_dis_bs, df_dis_patient], ignore_index=True)
        label_mapping = dict(zip(df_te['id'], df_te.index))
        df_dis_bs_patient['src_id'] = df_dis_bs_patient['source'].map(label_mapping)
        df_dis_bs_patient['target_id'] = df_dis_bs_patient['target'].map(label_mapping)
        
        sankey = go.Figure(data=[go.Sankey(
            arrangement="snap",
            node = dict(
                pad = 15,
                thickness = 20,
                line = dict(
                    color = "black",
                    width = 0.4
                ),
                label = df_te['label'].values.tolist(),
                color = df_te['color'].values.tolist(),
                ),
            link = dict(
                source = df_dis_bs_patient['src_id'].values.tolist(),
                target = df_dis_bs_patient['target_id'].values.tolist(),
                value = df_dis_bs_patient['value'].values.tolist(),
                color = df_dis_bs_patient['link_color'].values.tolist()
            )
        )])
        st.plotly_chart(sankey, use_container_width=True)

        team_col = st.columns(1)
        st.markdown("### Top Symptoms")
        df_teams = run_query("""
            MATCH (e:Person)-[n:HAS_SYMPTOM]->(p:Symptom) 
              return DISTINCT p.description as symptom, count(n) as occurences
              ORDER BY occurences DESC LIMIT 10""")
        size_max_default = 7
        scaling_factor = 5
        fig_team = px.scatter(df_teams, x="symptom", y="occurences",
                    size="occurences", color="symptom",
                        hover_name="symptom", log_y=True, 
                        size_max=size_max_default*scaling_factor)
        st.plotly_chart(fig_team, use_container_width=True)

        # create two columns for charts
        fig_col1, fig_col2 = st.columns(2)
        with fig_col1:
            st.markdown("### Most Diagnoses")
            df = run_query("""
              MATCH (e:Person)-[:HAS_DIAGNOSIS]->(p:Diagnosis) 
              return DISTINCT p.name as diagnosis, count(e) as diagnoses
              ORDER BY diagnoses DESC LIMIT 10""")
            fig = px.scatter(df, x="diagnosis", y="diagnoses",
                      size="diagnoses", color="diagnosis",
                            hover_name="diagnosis", log_y=True, 
                            size_max=size_max_default*scaling_factor)
            st.plotly_chart(fig, use_container_width=True)
            
        with fig_col2:
            st.markdown("### Top Diseases")
            df = run_query("""
              MATCH (e:Person)-[:HAS_DISEASE]->(p:Disease) 
              return p.name as disease, count(e) as occurences
              ORDER BY occurences DESC LIMIT 10""")
            fig2 = px.scatter(df, x="disease", y="occurences",
                      size="occurences", color="disease",
                            hover_name="disease", log_y=True, 
                            size_max=size_max_default*scaling_factor)
            st.plotly_chart(fig2, use_container_width=True)
        