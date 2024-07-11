import os
import pandas as pd
import streamlit as st
import openai
from dotenv import load_dotenv
from streamlit_extras.grid import grid

# Carregar variáveis de ambiente
load_dotenv()

# Inicialização da API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

def generate_analysis_dashboard(df):
    # Extração dos índices
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
    
    # Gerar a análise com o GPT-4
    input_text = (
        f"Com base nos seguintes índices financeiros: {indices}, forneça uma análise explícita "
        f"período a período sobre os índices apresentados e possíveis diagnósticos financeiros. "
        f"Aqui está o que cada sigla signifca: Liq_corrente = liquidez corrente, Div_liq_ebit = "
        f"divida liquida da empresa dividido pelo ebit atual, Div_liq_pl = divida liquida dividido "
        f"pelo patrimônio liquido, PL_ativos = patrimonio liquido dividido pelos ativos, "
        f"Passivos_ativos = passivos divididos pelos ativos, Margem_Bruta = margem bruta, "
        f"Margem_liquida = margem líquida, Div_liq_ebitda = divida líquida dividida pelo ebitda, "
        f"Ebit_rec_liq = receita liquida Ebit, Ebitda_rec_liq = receita liquida Ebitda, ROIC = "
        f"retorno no capital investido, GA = giros ativos, CAGR RECEITAS = receitas da Taxa composta "
        f"de crescimento anual, CAGR LUCROS = lucro da Taxa composta de crescimento anual, "
        f"Margem_liquida = margem líquida, ROE = Retorno sobre patrimônio líquido, ROA = Retorno "
        f"sobre ativos. Não mencionar as siglas no texto da análise, apenas seus significados. Os dados "
        f"apresentados se referem ao grupo brasileiro Arezzo que atua no ramo de calçados e roupas. Faça "
        f"a análise dos indicadores em relação a dados históricos setoriais como a Abicalçados e Relatórios "
        f"de Relações com Investidores (RI) da própria Arezzo."
    )
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Você é um assistente financeiro que fornece análises detalhadas e explicativas."},
            {"role": "user", "content": input_text}
        ],
        max_tokens=1500
    )
    
    return response.choices[0].message['content'].strip()

# Função de exemplo para carregar o dataframe no session_state
def load_data():
    # Exemplo de dataframe, substitua pelo seu carregamento de dados real
    df = pd.DataFrame({
        'EMPRESA': ['Empresa X']*16,
        'ÍNDICES': ['Liq_corrente', 'Div_liq_ebit', 'Div_liq_pl', 'PL_ativos', 'Passivos_ativos', 'Margem_Bruta', 'Div_liq_ebitda', 'Ebitda_rec_liq', 'Ebit_rec_liq', 'ROIC', 'GA', 'CAGR RECEITAS', 'CAGR LUCROS', 'Margem_liquida', 'ROE', 'ROA'],
        'VALOR': [1.5, 2.0, 0.8, 0.6, 1.2, 40, 1.8, 15, 12, 10, 1.5, 5, 10, 8, 15, 7]
    })
    st.session_state['data'] = df

# Função principal do dashboard
def dashboard():
    # Verifique se os dados estão carregados no session_state
    if 'data' not in st.session_state:
        st.write("Carregando dados...")
        load_data()
        st.experimental_rerun()
        return

    # Recebe o dataframe do session state 
    df = st.session_state['data']
    
    # Cria layout
    my_grid = grid(2, 2, vertical_align="bottom")

    # Armazena o nome da empresa
    EMPRESA = df['EMPRESA'].unique()

    # Filtros de exemplo
    Liq_corrente = df.loc[df["ÍNDICES"] == "Liq_corrente", "VALOR"].values[0]
    Div_liq_ebit = df.loc[df["ÍNDICES"] == "Div_liq_ebit", "VALOR"].values[0]

    # Row 1:
    my_grid.markdown(f"Empresa: {EMPRESA[0]}")
    my_grid.markdown("Indicadores de Endividamento")
    my_grid.empty()

    # Row 2:
    col1, col2, col3, col4 = st.columns(4)    

    col1.markdown("_Protótipo v0.2.0_")
    col2.metric(label="DÍV LÍQ/EBIT", value=Div_liq_ebit)
    col3.metric(label="LÍQ. CORRENTE", value=Liq_corrente)

    with st.expander("Para uma nova análise, clique no botão novamente", expanded=True):
        if st.button('Gerar Análise', key='botao1'):
            with st.spinner('Gerando análise...'):
                analysis = generate_analysis_dashboard(df)
            st.success('Análise gerada!')
            st.write(analysis)

        user_question = st.text_input("Pergunta:")
        if st.button("Enviar Pergunta", key='botao2'):
            if user_question:
                with st.spinner('Gerando resposta...'):
                    response = financial_assistant(user_question, df)
                st.write(response)

# Chama a função principal
dashboard()
