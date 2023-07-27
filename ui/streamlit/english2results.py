from langchain.chains import GraphCypherQAChain
from langchain.graphs import Neo4jGraph
from langchain.prompts.prompt import PromptTemplate
from langchain.llms.bedrock import Bedrock
from retry import retry
from timeit import default_timer as timer
import streamlit as st
import ingestion.bedrock_util as bedrock_util

host = st.secrets["NEO4J_HOST"]+":"+st.secrets["NEO4J_PORT"]
user = st.secrets["NEO4J_USER"]
password = st.secrets["NEO4J_PASSWORD"]
db = st.secrets["NEO4J_DB"]

bedrock = bedrock_util.get_client()

model_name = st.secrets["CYPHER_MODEL"]
if model_name == '':
    model_name = 'anthropic.claude-v2'
    

CYPHER_GENERATION_TEMPLATE = """Human: You are an expert Neo4j Cypher translator who understands the question in english and convert to Cypher strictly based on the Neo4j Schema provided and following the instructions below:
1. Generate Cypher query compatible ONLY for Neo4j Version 5
2. Do not use EXISTS, SIZE keywords in the cypher. Use alias when using the WITH keyword
3. Use only Nodes and relationships mentioned in the schema
4. Always enclose the Cypher output inside 3 backticks. Do not add 'cypher' after the backticks
5. Always do a case-insensitive and fuzzy search for any properties related search. Eg: to search for a Company name use `toLower(c.name) contains 'neo4j'`
6. Always use aliases to refer the node in the query
7. Cypher is NOT SQL. So, do not mix and match the syntaxes
8. `OWNS` relationship is syonymous with `BUY`
Schema:
{schema}
Human: Which of the managers own Amazon?
Assistant: MATCH p=(m:Manager)-[:OWNS]->(c:Company) WHERE toLower(c.nameOfIssuer) CONTAINS 'amazon' RETURN p;
Human: If a manager owns Meta, do they also own Amazon?
Assistant: MATCH p=(m:Manager)-[:OWNS]->(c:Company) WHERE toLower(c.nameOfIssuer) CONTAINS 'amazon ' MATCH q=(m)-[:OWNS]->(d:Company) WHERE toLower(d.nameOfIssuer) CONTAINS 'meta ' RETURN p,q
Human: If a manager owns Google, do they also own Apple?
Assistant: MATCH p=(m:Manager)-[:OWNS]->(c:Company) WHERE toLower(c.nameOfIssuer) CONTAINS 'google ' MATCH q=(m)-[:OWNS]->(d:Company) WHERE toLower(d.nameOfIssuer) CONTAINS 'apple ' RETURN p,q
Human: {question}
Assistant:"""
CYPHER_GENERATION_PROMPT = PromptTemplate(
    input_variables=["schema","question"], template=CYPHER_GENERATION_TEMPLATE
)

@retry(tries=5, delay=5)
def get_results(messages):
    start = timer()
    try:
        graph = Neo4jGraph(
            url=host, 
            username=user, 
            password=password
        )
        chain = GraphCypherQAChain.from_llm(
            Bedrock(
                model_id=model_name,
                client=bedrock,
                model_kwargs = {
                    "temperature":0,
                    "top_k":1, "top_p":0.999,
                    "anthropic_version":"bedrock-2023-05-31",
                    "max_tokens_to_sample": 2048
                }
            ), 
            graph=graph, verbose=True,
            return_intermediate_steps=True,
            cypher_prompt=CYPHER_GENERATION_PROMPT
        )
        if messages:
            question = messages.pop()
        else: 
            question = 'Which of the managers own Amazon?'
        return chain(question)
    # except Exception as ex:
    #     print(ex)
    #     return "LLM Quota Exceeded. Please try again"
    finally:
        print('Cypher Generation Time : {}'.format(timer() - start))

