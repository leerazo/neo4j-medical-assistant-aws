import streamlit as st
import rag_vector_only
import rag_vector_graph
from PIL import Image
from ui_utils import render_header_svg
from langchain.globals import set_llm_cache
from langchain.cache import InMemoryCache

set_llm_cache(InMemoryCache())


st.set_page_config(page_icon="images/logo-mark-fullcolor-RGB-transBG.svg", layout="wide")

render_header_svg("images/vg-top-header.svg", 350)

render_header_svg("images/bottom-header.svg", 200)

def rag_v(question):
  res = rag_vector_only.get_results(question)
  st.markdown(res['result'])
  with st.expander("Context:"):
    st.json(res['context'])


def rag_vg(question):
  res = rag_vector_graph.get_results(question)
  st.markdown(res['result'])
  with st.expander("Context:"):
    st.json(res['context'])

question = st.text_input("Ask question on the SEC Filings", value="")

col1, col2 = st.columns(2)
with col1:
  st.markdown("### Baseline RAG (vector only)")
  with st.expander("Vector Only Search does not have context and it is something like this:"):
    vec_only = Image.open('./images/vector-only.png')
    st.markdown("#### Relationships are ignored. So, lesser context")
    st.image(vec_only)
    v = Image.open('./images/vector-only1.png')
    st.markdown("#### Sample Doc Chunk")
    st.image(v)
with col2:
  st.markdown("### GraphRAG (vector + graph)")
  with st.expander("Vector+Graph has full context like this:"):
    schema = Image.open('./images/schema.png')
    st.markdown("#### Relationships make this context-rich")
    st.image(schema)
    vg = Image.open('./images/vector-graph.png')
    st.markdown("#### Sample Doc Chunk")
    st.image(vg)

if question:
  with col1:
    with st.spinner('Running RAG using Vectors ...'):
      rag_v(question)
      st.success('Done!')
  with col2:
    with st.spinner('Running RAG using Vectors & Graphs ...'):
      rag_vg(question)
      st.success('Done!')

st.markdown("---")

st.markdown("""
<style>
  table {
    width: 100%;
    border-collapse: collapse;
    border: none !important;
    font-family: "Source Sans Pro", sans-serif;
    color: rgba(49, 51, 63, 0.6);
    font-size: 0.9rem;
  }

  tr {
    border: none !important;
  }
  
  th {
    text-align: center;
    colspan: 3;
    border: none !important;
    color: #0F9D58;
  }
  
  th, td {
    padding: 2px;
    border: none !important;
  }
</style>

<table>
  <tr>
    <th colspan="3">Sample Questions to try out</th>
  </tr>
  <tr>
    <td>Which asset managers have investments in outside USA? Explain with evidence</td>
    <td>Which companies and asset managers are vulnerable to chip shortage?</td>
    <td>Which asset managers are exposed to defense industries based on the companies they own shares in?</td>
  </tr>
  <tr>
    <td>Which asset managers have investments in regulated industries?</td>
    <td>Which company sells analytics solutions?</td>
    <td></td>
  </tr>
  <tr>
    <td></td>
    <td></td>
  </tr>
</table>
<!--
            <table>
  <tr>
    <th colspan="3">Sample Questions to try out</th>
  </tr>
  <tr>
    <td>Which asset managers are most affected during covid?</td>
    <td>Which asset managers and companies are vulnerable to chip shortage?</td>
    <td>Which asset managers and companies are vulnerable to lithium shortage?</td>
  </tr>
  <tr>
    <td>Which asset managers have investments in regulated industries?</td>
    <td>Which asset managers have investments in outside USA? Explain with evidence</td>
    <td>Which asset managers own all the FAANG stocks?</td>
  </tr>
  <tr>
    <td></td>
    <td></td>
  </tr>
</table>
            -->
""", unsafe_allow_html=True)
