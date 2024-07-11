import os
import streamlit as st
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate)
from langchain.memory import ConversationBufferMemory
import streamlit.components.v1 as components
import pandas as pd
#import helpers.dadoscontabeis as data_contabil  # Certifique-se de descomentar e usar isso corretamente se necessário

# Initialize session state for 'data' if it does not exist
if 'data' not in st.session_state:
    st.session_state['data'] = pd.DataFrame()  # or load your initial data here

df = st.session_state['data']

indices = {}
if not df.empty:
    # Assumindo que data_contabil.data_dashboard(df) retorna um dataframe adequado.
    # df_data_dash = data_contabil.data_dashboard(df)
    df_data_dash = df  # Use this line if the above line is not available

    indices = {
        "Liq_corrente": df.loc[df["ÍNDICES"] == "Liq_corrente", "VALOR"].values[0],
        "Div_liq_ebit": df.loc[df["ÍNDICES"] == "Div_liq_ebit", "VALOR"].values[0],
        "Div_liq_pl": df.loc[df["ÍNDICES"] == "Div_liq_pl", "VALOR"].values[0],
        "PL_ativos": df.loc[df["ÍNDICES"] == "PL_ativos", "VALOR"].values[0],
        "Passivos_ativos": df.loc[df["ÍNDICES"] == "Passivos_ativos", "VALOR"].values[0],
        "Margem_Bruta": df.loc[df["ÍNDICES"] == "Margem_Bruta", "VALOR"].values[0],
        "Div_liq_ebitda": df.loc[df["ÍNDICES"] == "Div_liq_ebitda", "VALOR"].values[0],
        "Ebitda_rec_liq": df.loc[df["ÍNDICES"] == "Ebitda_rec_liq", "VALOR"].values[0],
        "Ebit_rec_liq": df.loc[df["ÍNDICES"] == "Ebit_rec_liq", "VALOR"].values[0],
        "ROIC": df.loc[df["ÍNDICES"] == "ROIC", "VALOR"].values[0],
        "GA": df.loc[df["ÍNDICES"] == "GA", "VALOR"].values[0],
        "CAGR RECEITAS": df.loc[df["ÍNDICES"] == "CAGR RECEITAS", "VALOR"].values[0],
        "CAGR LUCROS": df.loc[df["ÍNDICES"] == "CAGR LUCROS", "VALOR"].values[0],
        "Margem_liquida": df.loc[df["ÍNDICES"] == "Margem_liquida", "VALOR"].values[0],
        "ROE": df.loc[df["ÍNDICES"] == "ROE", "VALOR"].values[0],
        "ROA": df.loc[df["ÍNDICES"] == "ROA", "VALOR"].values[0]
    }

def initialize_chat_history():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

def financial_assistant(user_question, df=None, indices=None):
    # Inicializar chat_history se não existir
    initialize_chat_history()

    # Carregar variáveis de ambiente do arquivo .env
    load_dotenv()

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    if not OPENAI_API_KEY:
        st.error("API Key for OpenAI is missing. Please check your .env file.")
        return

    # Definir a memória da conversa
    memory = ConversationBufferMemory(return_messages=True)

    if indices is None:
        indices = {}

    indices_str = "\n".join([f"{key}: {value}" for key, value in indices.items()])

    system_template = f"""Você é um assistente financeiro. Use as seguintes informações de contexto para responder às perguntas dos usuários.
    Se você não souber a resposta, diga apenas que não sabe, não tente inventar uma resposta.

    Informações de contexto:
    1. O mercado de ações é um componente essencial da economia global.
    2. A diversificação é uma estratégia fundamental para reduzir riscos em investimentos.
    3. As taxas de juros influenciam diretamente os preços dos títulos e ações.
    4. O planejamento financeiro inclui a gestão de receitas, despesas, investimentos e aposentadoria.
    5. A análise fundamentalista e técnica são métodos comuns para avaliar ações.
    6. A poupança de emergência deve cobrir pelo menos seis meses de despesas essenciais.
    7. Os impostos sobre investimentos variam dependendo do país e do tipo de investimento.

    Aqui estão alguns índices financeiros da empresa:
    {indices_str}

    Agora, responda à pergunta do usuário da melhor maneira possível.
    """

    messages = [
        SystemMessagePromptTemplate.from_template(system_template),
        HumanMessagePromptTemplate.from_template("{question}"),
    ]
    prompt = ChatPromptTemplate.from_messages(messages)

    def render_chat_history(chat_history):
        html = '<div style="max-height: 400px; overflow-y: auto;">'
        for chat in chat_history:
            html += f'''
            <div style="background-color: #f1f1f1; border-radius: 10px; padding: 10px; margin-bottom: 10px;">
                <strong>Você:</strong> {chat['input']}
            </div>
            <div style="background-color: #e1e1fb; border-radius: 10px; padding: 10px; margin-bottom: 10px;">
                <strong>Assistente:</strong> {chat['response']}
            </div>
            '''
        html += '</div>'
        return html

    # Use um modelo ChatOpenAI
    llm = ChatOpenAI(model_name='gpt-4', max_tokens=4000, temperature=0, openai_api_key=OPENAI_API_KEY)

    # Adicionar informações do DataFrame ao contexto, se fornecido
    df_context = ""
    if df is not None and not df.empty:
        df_context = df.to_string(index=False)

    # Gerar a mensagem completa a ser enviada para o modelo
    full_system_template = system_template + "\n\nInformações adicionais do DataFrame:\n" + df_context
    messages_with_df = [
        SystemMessagePromptTemplate.from_template(full_system_template),
        HumanMessagePromptTemplate.from_template("{question}"),
    ]
    prompt_with_df = ChatPromptTemplate.from_messages(messages_with_df)
    formatted_messages = prompt_with_df.format_messages(question=user_question)

    # Obter a resposta do modelo
    response = llm(formatted_messages)

    # Atualizar a memória com a resposta do modelo
    memory.save_context({"input": user_question}, {"response": response.content})

    # Atualizar o histórico de conversa no estado da sessão
    st.session_state.chat_history.append({"input": user_question, "response": response.content})

    # Exibir o histórico de conversa
    chat_history_html = render_chat_history(st.session_state.chat_history)
    components.html(chat_history_html, height=400, scrolling=True)

# Testando a função no Streamlit
user_question = st.text_input("Pergunta:")

if st.button("Enviar Pergunta"):
    if user_question:
        with st.spinner('Gerando resposta...'):
            financial_assistant(user_question, df, indices)
