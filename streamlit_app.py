import pandas as pd
import streamlit as st
from openai import OpenAI
from lang import financial_assistant

# Verificar se a chave da API está carregada corretamente
api_key = st.secrets["OPENAI_API_KEY"]
if not api_key:
    raise ValueError("A chave da API OpenAI não foi encontrada. Verifique o arquivo de segredos.")

# Inicialização do cliente OpenAI
client = OpenAI(api_key=api_key)

def generate_analysis_dashboard(df):
    required_indices = [
        "Liq_corrente", "Div_liq_ebit", "Div_liq_pl", "PL_ativos", "Passivos_ativos", 
        "Margem_Bruta", "Div_liq_ebitda", "Ebitda_rec_liq", "Ebit_rec_liq", "ROIC", 
        "GA", "CAGR RECEITAS", "CAGR LUCROS", "Margem_liquida", "ROE", "ROA"
    ]

    # Verificar se todos os índices necessários estão presentes no DataFrame
    missing_indices = [index for index in required_indices if index not in df["ÍNDICES"].values]
    if missing_indices:
        raise ValueError(f"Os seguintes índices estão faltando no DataFrame: {missing_indices}")

    # Extração dos índices
    indices = {index: df.loc[df["ÍNDICES"] == index, "VALOR"].values[0] for index in required_indices}

    # Gerar a análise com o GPT-4
    input_text = (
        f"Com base nos seguintes índices financeiros: {indices}, forneça uma análise explícita "
        f"período a período sobre os índices apresentados e possíveis diagnósticos financeiros. "
        f"Aqui está o que cada sigla significa: Liq_corrente = liquidez corrente, Div_liq_ebit = "
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

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Você é um assistente financeiro que fornece análises detalhadas e explicativas."},
            {"role": "user", "content": input_text}
        ],
        max_tokens=1500
    )

    return response.choices[0].message.content.strip()

def dashboard():
    st.title("Análise Financeira")

    # Criando um DataFrame de exemplo
    data = {
        "ÍNDICES": [
            "Liq_corrente", "Div_liq_ebit", "Div_liq_pl", "PL_ativos", "Passivos_ativos", 
            "Margem_Bruta", "Div_liq_ebitda", "Ebitda_rec_liq", "Ebit_rec_liq", "ROIC", 
            "GA", "CAGR RECEITAS", "CAGR LUCROS", "Margem_liquida", "ROE", "ROA"
        ],
        "VALOR": [
            1.5, 2.0, 1.2, 0.8, 0.6, 0.4, 3.5, 2.5, 1.8, 10.0, 
            1.2, 5.0, 3.0, 0.7, 15.0, 8.0
        ]
    }
    df = pd.DataFrame(data)
    st.write(df)

    try:
        analysis = None
        if st.button('Gerar Análise'):
            with st.spinner('Gerando análise...'):
                analysis = generate_analysis_dashboard(df)
            st.success('Análise gerada!')
            st.write(analysis)
    except ValueError as e:
        st.error(f"Erro: {e}")
    user_question = st.text_input("Pergunta:")
    if st.button("Enviar Pergunta", key='botao2'):
        if user_question:
            with st.spinner('Gerando resposta...'):
                response = financial_assistant(user_question, df)
                st.write(response)

if __name__ == "__main__":
    dashboard()
