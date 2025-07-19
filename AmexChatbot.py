import os
import streamlit as st
from langchain_community.utilities import SQLDatabase
from langchain_community.llms import OpenAI
from langchain_experimental.sql import SQLDatabaseChain
from langchain.prompts.chat import HumanMessagePromptTemplate
from langchain_community.chat_models import ChatOpenAI
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

# -------- Streamlit Page Config --------
st.set_page_config(page_title="Amex Chatbot", page_icon="💳", layout="wide")
st.title("💳 Amex Insights Chatbot")
st.markdown("Ask questions related to customer behavior, offers, and more...")

# -------- Session State --------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# -------- LLM and DB Setup --------
OPENAI_API_KEY = "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"  # Keep your key secret!
llm = ChatOpenAI(temperature=0, openai_api_key=OPENAI_API_KEY)

# MySQL Setup
host = 'localhost'
port = '3308'
username = 'root'
password = ''
database_schema = 'gen_ai'

mysql_uri = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database_schema}"
db = SQLDatabase.from_uri(mysql_uri, include_tables=['amex_data_5000'], sample_rows_in_table_info=2)
db_chain = SQLDatabaseChain.from_llm(llm, db, verbose=True)

# -------- Helper Functions --------
def retrieve_from_db(query: str) -> str:
    db_context = db_chain(query)
    return db_context['result'].strip()

def generate_response(query: str) -> str:
    db_context = retrieve_from_db(query)

    system_message = SystemMessage(content="""
    You are a customer insights assistant working with American Express (Amex).
    Your role is to analyze customer behavior and provide helpful responses based on customer interaction data.
    
    The database includes:
    - Customer ID
    - Offer ID
    - Date and Time of Interaction
    - Whether the offer was accepted (offer_action)
    - A series of demographic and behavioral features (var_1 to var_50)
    """)
    
    human_template = HumanMessagePromptTemplate.from_template(
        "Input:\n{human_input}\n\nContext:\n{db_context}\n\nOutput:"
    )

    human_message = human_template.format(human_input=query, db_context=db_context)
    messages = [system_message, human_message]

    return llm(messages).content.strip()

# -------- Streamlit Chat UI --------
with st.container():
    for user_msg, bot_msg in st.session_state.chat_history:
        with st.chat_message("user"):
            st.markdown(user_msg)
        with st.chat_message("assistant"):
            st.markdown(bot_msg)

prompt = st.chat_input("Ask your question here...")
if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing..."):
            try:
                response = generate_response(prompt)
                st.markdown(response)
                st.session_state.chat_history.append((prompt, response))
            except Exception as e:
                st.error(f"Error: {str(e)}")



# cd "C:\Users\HP\OneDrive\Desktop\GenAI Ramana"
#streamlit run AmexChatbot.py

