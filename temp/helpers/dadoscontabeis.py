import pandas as pd
import streamlit as st

import helpers.criarGraficos as grf
import helpers.analises as anls
import helpers.demonstrativos as demo


# @st.cache_data
def ordena_dataframe_decrescente(df, inicio, fim):

    # Classifique os trimestres de forma personalizada
    trimestres_ordenados = ["4", "3", "2", "1"]
    anos = [str(ano) for ano in range(fim + 1, inicio - 1, -1)]
    trimestres_ordenados = [f"{tri}T{ano}" for ano in anos for tri in trimestres_ordenados]

    # Ordenar colunas por PERIODO
    df['TRIMESTRE'] = pd.Categorical(df['TRIMESTRE'], categories=trimestres_ordenados, ordered=True)
    bpp = df.sort_values('TRIMESTRE')

    return df

def ordena_tabular_anual(df):
    # Reverte a ordem das colunas (exceto a coluna 'ÍNDICES' que foi resetada como index)
    colunas_ordenadas = ['ÍNDICES'] + df.columns[1:][::-1].tolist()
    # Reindexa o DataFrame para aplicar a nova ordem de colunas
    return df[colunas_ordenadas]

# @st.cache_data
# def ordenar_dataframe_crescente(df, inicio, fim):

#     # Classifique os trimestres de forma personalizada
#     trimestres_ordenados = ["1", "2", "3", "4"]
#     anos = [str(ano) for ano in range(fim + 1, inicio - 1, -1)]
#     trimestres_ordenados = [f"{tri}T{ano}" for ano in anos for tri in trimestres_ordenados]

#     # Ordenar colunas por PERIODO
#     df['PERIODO'] = pd.Categorical(df['PERIODO'], categories=trimestres_ordenados, ordered=True)
#     bpp = df.sort_values('PERIODO')

#     return df

# Função para extrair a receita liquida trimestral
# @st.cache_data
def data_receita_liquida_custos_trimestral(df, inicio, fim):
# Retorna os resultado dos custos, receitas liquidas e lucro liquido.
    # Filtra as contas receita liquida e custos
    df_filtro_contas = (df['CONTA'] == "3.02") | (df['CONTA'] == "3.01") | (df['CONTA'] == "3.11") 
    df = df.loc[df_filtro_contas]            

    df = df[(df["ANO"] >= inicio) & (df["ANO"] <= fim )]


    # Altera a estrutura dos dados para o grafico
    df_pivot = df.pivot_table(index='PERIODO', columns='DESCRIÇÃO', values='VALOR', observed=False).reset_index()   

    # Remove o nome da coluna indice
    df_pivot.columns.name = None

    # Altera os nomes das colunas
    df_pivot.columns = ['PERIODO', 'CUSTOS', 'LUCRO LIQUIDO', 'RECEITA LIQUIDA' ]

    # Cria a coluna trimestre e ano, e ordena os dados
    df_final = anls.cria_coluna_mes_ano(df_pivot)

    return df_final    

# Função para extrair a receita liquida anual
# @st.cache_data
def data_receita_liquida_custos_anual(df, ano_inicio, ano_fim):

    # Filtra os valores para periodo selecionado
    df = df[(df["ANO"] >= ano_inicio) & (df["ANO"] <= ano_fim )]

    # Filtra as contas receita liquida e custos
    df_filtro_contas = (df['CONTA'] == "3.02") | (df['CONTA'] == "3.01") | (df['CONTA'] == "3.11") 
    df = df[df_filtro_contas]            
    
    # Altera a estrutura dos dados para o grafico
    df_pivot = df.pivot_table(index='ANO', columns='DESCRIÇÃO', values='VALOR').reset_index()    

    # Remove o nome da coluna indice
    df_pivot.columns.name = None
   
    # Altera os nomes das colunas
    df_pivot.columns = ['ANO', 'CUSTOS', 'RECEITA LIQUIDA', 'LUCRO LIQUIDO']
    return df_pivot    

# Função para criar os dados anuais para o gráfico
# @st.cache_data
def data_bp_anual(df, inicio, fim):
    # Filtro e ordenação das colunas
    df = df[['CONTA', 'DESCRIÇÃO', 'VALOR','PERIODO', 'ANO', 'MES' ]]

    df = df[(df["ANO"] >= inicio) & (df["ANO"] <= fim )]

    # Contas
    df_ativo = df.loc[df['CONTA'] == '1'].copy()
    df_ativo_circ = df.loc[df['CONTA'] == '1.01'].copy()
    df_ativo_n_circ = df.loc[df['CONTA'] == '1.02'].copy()
    df_passivo_circ = df.loc[df['CONTA'] == '2.01'].copy()
    df_passivo_n_circ = df.loc[df['CONTA'] == '2.02'].copy()
    df_patrimonio_liq = df.loc[df['CONTA'] == '2.03'].copy()

    lista_passivo = []
    meses = df['MES'].unique()
    for a in range(inicio, fim + 1):
        for m in meses:
            passivo_total = df.loc[(df['ANO'] == a) & (df['MES'] == m) & (df['CONTA'] == "2"), "VALOR"].values[0]
            pat_liq = df.loc[(df['ANO'] == a) & (df['MES'] == m) & (df['CONTA'] == "2.03"), "VALOR"].values[0]
            periodo = df.loc[(df['ANO'] == a) & (df['MES'] == m) & (df['CONTA'] == "2"), "PERIODO"].values[0]           

            passivo = passivo_total - pat_liq

            # Cria dataframe com os resultados do calculo do passivo total
            lista_passivo.append({'CONTA': "2", 'DESCRIÇÃO': "Passivo sem patri liq", 'VALOR': round(passivo,2), 'PERIODO': periodo, 'ANO': a, 'MES': m})                

    # Transforma a lista em dataframe
    df_passivo = pd.DataFrame(lista_passivo)  

    return df_ativo, df_ativo_circ, df_ativo_n_circ, df_passivo_circ, df_passivo_n_circ, df_patrimonio_liq, df_passivo

# Função para criar os dados trimestrais para o gráfico
# @st.cache_data
def data_bp_trimestral(df, inicio, fim):
    # Filtro e ordenação das colunas
    df = df[['CONTA', 'DESCRIÇÃO', 'VALOR','PERIODO', 'ANO', 'MES' ]]
    df = df.dropna()
    df = df.sort_values('PERIODO')
    # Filtro ano
    df = df.loc[(df["ANO"] >= inicio) & (df["ANO"] <= fim )]

    lista = []
    meses = df['MES'].unique()
    for a in range(inicio, fim + 1):
        for m in meses:
            passivo_total = df.loc[(df['ANO'] == a) & (df['MES'] == m) & (df['CONTA'] == "2"), "VALOR"].values[0]
            pat_liq = df.loc[(df['ANO'] == a) & (df['MES'] == m) & (df['CONTA'] == "2.03"), "VALOR"].values[0]

            periodo = df.loc[(df['ANO'] == a) & (df['MES'] == m) & (df['CONTA'] == "2"), "PERIODO"].values[0]           

            # Calculo do passivo 
            passivo = passivo_total - pat_liq

            lista.append({'CONTA': "2", 'DESCRIÇÃO': "Passivo sem patri liq", 'VALOR': round(passivo,2), 'PERIODO': periodo, 'ANO': a, 'MES': m})
         
    # Transforma a lista em dataframe
    df_passivo_sem_patrimonio = pd.DataFrame(lista) 

    return df, df_passivo_sem_patrimonio

# @st.cache_data
def data_margens_anual(df, inicio, fim):
    # Cria lista dos indices que serão calculados
    indices = [
        "Líquidez Geral", "Líquidez Corrente", "Líquidez Seca",
        "Líquidez Imediata", "Solvência Geral", "Margem de Lucro", 
        "Margem Líquida", "Giro do Ativo" 
        ]

    # Filtra os valores e calcula cada indices e margens listados
    ind_geral = []
    meses = df['MES'].unique()
    for i in indices:   
        for a in range(inicio, fim + 1):
            for m in meses:                                    
                if i == "Líquidez Geral":                             
                    ativo_circ = df.loc[(df['ANO'] == a) & (df['CONTA'] == "1.01"), "VALOR"].values[0]
                    real_lp = df.loc[(df['ANO'] == a) & (df['CONTA'] == "1.02.01"), "VALOR"].values[0]
                    passivo_circ = df.loc[(df['ANO'] == a) & (df['CONTA'] == "2.01"), "VALOR"].values[0]
                    passivo_ncirc = df.loc[(df['ANO'] == a) & (df['CONTA'] == "2.02"), "VALOR"].values[0]
                    res = (ativo_circ + real_lp) / (passivo_circ + passivo_ncirc)                                

                elif i == "Líquidez Corrente":                        
                    ativo_circ = df.loc[(df['ANO'] == a) & (df['CONTA'] == "1.01"), "VALOR"].values[0]
                    passivo_circ = df.loc[(df['ANO'] == a) & (df['CONTA'] == "2.01"), "VALOR"].values[0]
                    res = ativo_circ / passivo_circ

                elif i == "Líquidez Seca":                    
                    ativo_circ = df.loc[(df['ANO'] == a) & (df['CONTA'] == "1.01"), "VALOR"].values[0]
                    passivo_circ = df.loc[(df['ANO'] == a) & (df['CONTA'] == "2.01"), "VALOR"].values[0]
                    estoque = df.loc[(df['ANO'] == a) & (df['CONTA'] == "1.01.04"), "VALOR"].values[0]
                    res = (ativo_circ - estoque)/ passivo_circ
                    
                elif i == "Líquidez Imediata":                    
                    caixa_eq = df.loc[(df['ANO'] == a)& (df['CONTA'] == "1.01.01"), "VALOR"].values[0]
                    passivo_circ = df.loc[(df['ANO'] == a) & (df['CONTA'] == "2.01"), "VALOR"].values[0]
                    res = caixa_eq / passivo_circ

                elif i == "Solvência Geral":
                    ativo_total = df.loc[(df['ANO'] == a) & (df['CONTA'] == "1"), "VALOR"].values[0]
                    passivo_circ = df.loc[(df['ANO'] == a) & (df['CONTA'] == "2.01"), "VALOR"].values[0]
                    passivo_ncirc = df.loc[(df['ANO'] == a) & (df['CONTA'] == "2.02"), "VALOR"].values[0]
                    res = ativo_total / (passivo_circ + passivo_ncirc) 

                elif i == "Margem de Lucro":                                   
                    lucro_liq = df.loc[(df['ANO'] == a) & (df['CONTA'] == "3.11"), "VALOR"].values[0]
                    receita_total = df.loc[(df['ANO'] == a) & (df['CONTA'] == "3.03"), "VALOR"].values[0] 
                    res = (lucro_liq / receita_total)*100                

                elif i == "Margem Líquida":                                         
                    lucro_liq = df.loc[(df['ANO'] == a) & (df['MES'] == m) & (df['CONTA'] == "3.11"), "VALOR"].values[0]
                    receita_liq = df.loc[(df['ANO'] == a) & (df['MES'] == m) & (df['CONTA'] == "3.01"), "VALOR"].values[0]   
                    res = (lucro_liq / receita_liq)*100

                elif i == "Giro do Ativo":                                    
                    ativo_total = df.loc[(df['ANO'] == a) & (df['MES'] == m) & (df['CONTA'] == "1"), "VALOR"].values[0]
                    receita_total = df.loc[(df['ANO'] == a) & (df['MES'] == m) & (df['CONTA'] == "3.03"), "VALOR"].values[0] 
                    res = lucro_liq / receita_total

                # Insere os dados na lista
                ind_geral.append({'ÍNDICES': i, 'ANO': a, 'VALOR': round(res,2)})  

    # Cria dataframe com os dados dos indices   
    df_indicadores = pd.DataFrame(ind_geral)  

    # Altera a estrutura do dataframe
    df_indicadores_pivot = df_indicadores.pivot_table(index=('ÍNDICES'), columns='ANO', values='VALOR').reset_index()
  
    # Remove o nome da coluna indice
    df_indicadores_pivot.columns.name = None

    # Ordena os dados anuais para as tabelas
    df_indicadores_pivot = ordena_tabular_anual(df_indicadores_pivot)

    # Filtra as margens
    df_margens = df_indicadores[(df_indicadores["ÍNDICES"] == "Margem Líquida") | 
                      (df_indicadores["ÍNDICES"] == "Margem de Lucro") | 
                      (df_indicadores["ÍNDICES"] == "Margem de Lucro")]
    
    # Filtra os indices de liquidez
    df_liquidez = df_indicadores[(df_indicadores["ÍNDICES"] == "Líquidez Geral") |
                       (df_indicadores["ÍNDICES"] == "Líquidez Corrente") |
                       (df_indicadores["ÍNDICES"] == "Líquidez Seca") |
                       (df_indicadores["ÍNDICES"] == "Líquidez Imediata") |
                       (df_indicadores["ÍNDICES"] == "Solvência Geral") |
                       (df_indicadores["ÍNDICES"] == "Giro do Ativo")]

    return df_margens, df_liquidez, df_indicadores_pivot, df_indicadores

# @st.cache_data
def data_margens_trimestral(df, inicio, fim):
    indices = [
        "Líquidez Geral", "Líquidez Corrente", "Líquidez Seca",
        "Líquidez Imediata", "Solvência Geral", "Margem de Lucro", 
        "Margem Líquida", "Giro do Ativo" 
        ]
    
    ind_geral = []
    meses = df['MES'].unique()
    for i in indices:   
        for a in range(inicio, fim + 1):
            for m in meses:                                    
                if i == "Líquidez Geral":                             
                    ativo_circ = df.loc[(df['ANO'] == a) & (df['MES'] == m) & (df['CONTA'] == "1.01"), "VALOR"].values[0]
                    real_lp = df.loc[(df['ANO'] == a) & (df['MES'] == m) & (df['CONTA'] == "1.02.01"), "VALOR"].values[0]
                    passivo_circ = df.loc[(df['ANO'] == a) & (df['MES'] == m) & (df['CONTA'] == "2.01"), "VALOR"].values[0]
                    passivo_ncirc = df.loc[(df['ANO'] == a) & (df['MES'] == m) & (df['CONTA'] == "2.02"), "VALOR"].values[0]
                    trimestre = df.loc[(df['ANO'] == a) & (df['MES'] == m) & (df['CONTA'] == "1"), "PERIODO"].values[0]
                    res = (ativo_circ + real_lp) / (passivo_circ + passivo_ncirc)                                

                elif i == "Líquidez Corrente":                        
                    ativo_circ = df.loc[(df['ANO'] == a) & (df['MES'] == m) & (df['CONTA'] == "1.01"), "VALOR"].values[0]
                    passivo_circ = df.loc[(df['ANO'] == a) & (df['MES'] == m) & (df['CONTA'] == "2.01"), "VALOR"].values[0]
                    trimestre = df.loc[(df['ANO'] == a) & (df['MES'] == m) & (df['CONTA'] == "1.01"), "PERIODO"].values[0]
                    res = ativo_circ / passivo_circ

                elif i == "Líquidez Seca":                    
                    ativo_circ = df.loc[(df['ANO'] == a) & (df['MES'] == m) & (df['CONTA'] == "1.01"), "VALOR"].values[0]
                    passivo_circ = df.loc[(df['ANO'] == a) & (df['MES'] == m) & (df['CONTA'] == "2.01"), "VALOR"].values[0]
                    estoque = df.loc[(df['ANO'] == a) & (df['MES'] == m) & (df['CONTA'] == "1.01.04"), "VALOR"].values[0]
                    trimestre = df.loc[(df['ANO'] == a) & (df['MES'] == m) & (df['CONTA'] == "1.01"), "PERIODO"].values[0]
                    res = (ativo_circ - estoque)/ passivo_circ
                    
                elif i == "Líquidez Imediata":                    
                    caixa_eq = df.loc[(df['ANO'] == a) & (df['MES'] == m) & (df['CONTA'] == "1.01.01"), "VALOR"].values[0]
                    passivo_circ = df.loc[(df['ANO'] == a) & (df['MES'] == m) & (df['CONTA'] == "2.01"), "VALOR"].values[0]      
                    trimestre = df.loc[(df['ANO'] == a) & (df['MES'] == m) & (df['CONTA'] == "2.01"), "PERIODO"].values[0]    
                    res = caixa_eq / passivo_circ

                elif i == "Solvência Geral":
                    ativo_total = df.loc[(df['ANO'] == a) & (df['MES'] == m) & (df['CONTA'] == "1"), "VALOR"].values[0]
                    passivo_circ = df.loc[(df['ANO'] == a) & (df['MES'] == m) & (df['CONTA'] == "2.01"), "VALOR"].values[0]
                    passivo_ncirc = df.loc[(df['ANO'] == a) & (df['MES'] == m) & (df['CONTA'] == "2.02"), "VALOR"].values[0]
                    trimestre = df.loc[(df['ANO'] == a) & (df['MES'] == m) & (df['CONTA'] == "2.01"), "PERIODO"].values[0]
                    res = ativo_total / (passivo_circ + passivo_ncirc) 

                elif i == "Margem de Lucro":                                   
                    lucro_liq = df.loc[(df['ANO'] == a) & (df['MES'] == m) & (df['CONTA'] == "3.11"), "VALOR"].values[0]
                    receita_total = df.loc[(df['ANO'] == a) & (df['MES'] == m) & (df['CONTA'] == "3.03"), "VALOR"].values[0] 
                    trimestre = df.loc[(df['ANO'] == a) & (df['MES'] == m) & (df['CONTA'] == "3.03"), "PERIODO"].values[0]       
                    res = (lucro_liq / receita_total)*100                

                elif i == "Margem Líquida":                                         
                    lucro_liq = df.loc[(df['ANO'] == a) & (df['MES'] == m) & (df['CONTA'] == "3.11"), "VALOR"].values[0]
                    receita_liq = df.loc[(df['ANO'] == a) & (df['MES'] == m) & (df['CONTA'] == "3.01"), "VALOR"].values[0]   
                    trimestre = df.loc[(df['ANO'] == a) & (df['MES'] == m) & (df['CONTA'] == "3.01"), "PERIODO"].values[0]           
                    res = (lucro_liq / receita_liq)*100

                elif i == "Giro do Ativo":                                    
                    ativo_total = df.loc[(df['ANO'] == a) & (df['MES'] == m) & (df['CONTA'] == "1"), "VALOR"].values[0]
                    receita_total = df.loc[(df['ANO'] == a) & (df['MES'] == m) & (df['CONTA'] == "3.03"), "VALOR"].values[0] 
                    trimestre = df.loc[(df['ANO'] == a) & (df['MES'] == m) & (df['CONTA'] == "1"), "PERIODO"].values[0]             
                    res = lucro_liq / receita_total

                ind_geral.append({'ÍNDICES': i, 'TRIMESTRE': trimestre, 'VALOR': round(res,2), 'MES': m, "ANO": a})  

    # Cria, ordenar e pivotar dataframe com dados dos indices   
    df_indicadores = pd.DataFrame(ind_geral)  
    
    # Ordena dados trimestrais para tabelas
    df_indicadores = ordena_dataframe_decrescente(df_indicadores, inicio, fim)

    # Altera estrutura do df
    df_indicadores_pivot = df_indicadores.pivot_table(index=('ÍNDICES'), columns='TRIMESTRE', values='VALOR', observed=False).reset_index()

    # Remove o nome da coluna indice
    df_indicadores_pivot.columns.name = None

    df_margens = df_indicadores[(df_indicadores["ÍNDICES"] == "Margem Líquida") | 
                      (df_indicadores["ÍNDICES"] == "Margem de Lucro") | 
                      (df_indicadores["ÍNDICES"] == "Margem de Lucro")]

    df_liquidez = df_indicadores[(df_indicadores["ÍNDICES"] == "Líquidez Geral") |
                       (df_indicadores["ÍNDICES"] == "Líquidez Corrente") |
                       (df_indicadores["ÍNDICES"] == "Líquidez Seca") |
                       (df_indicadores["ÍNDICES"] == "Líquidez Imediata") |
                       (df_indicadores["ÍNDICES"] == "Solvência Geral") |
                       (df_indicadores["ÍNDICES"] == "Giro do Ativo")]

    return df_margens, df_liquidez, df_indicadores_pivot, df_indicadores

def data_grafico_margens_dashboard(df):
    # Recebe o dataframe do session state 
    # df = st.session_state['data']
    ano_fim = df['ANO'].max()
    ano_inicio = ano_fim - 5    
    df = df[(df["ANO"] >= ano_inicio) & (df["ANO"] <= ano_fim)]
    df = df[(df["PERIODO"] == 'ANUAL') & (df["DEMONSTRATIVO"] == 'Demonstração do Resultado')]

    # df = ordenar_grafico_AH(df,inicio, fim)
    df = df.sort_values('ANO') 

    indices = ["Lucro", "Líquida"]    
    ind_geral = []
    for i in indices:   
        resultado = 0  # Inicializa a variável resultado
        for a in range(ano_inicio, ano_fim + 1):
            if i == "Lucro":                                   
                lucro_liquido = df.loc[(df['ANO'] == a) & (df['CONTA'] == "3.11"), "VALOR"].values[0]
                receita_total = df.loc[(df['ANO'] == a) & (df['CONTA'] == "3.03"), "VALOR"].values[0] 
                resultado = (lucro_liquido / receita_total)*100 

            elif i == "Líquida":                                         
                lucro_liquido = df.loc[(df['ANO'] == a) & (df['CONTA'] == "3.11"), "VALOR"].values[0]
                receita_liquida = df.loc[(df['ANO'] == a) & (df['CONTA'] == "3.01"), "VALOR"].values[0]   
                resultado = (lucro_liquido / receita_liquida)*100                                

            ind_geral.append({'MARGENS': i, 'ANO': a, 'VALOR': round(resultado,2)})                
    
    # Cria, ordenar e pivotar dataframe com dados dos indices   
    df_margens = pd.DataFrame(ind_geral)
    
    return df_margens

# @st.cache_data
def calcula_indicadores_grafico_dashboard(df):

    fim = df['ANO'].max()
    inicio = fim - 5    
    df = df[(df["ANO"] >= inicio) & (df["ANO"] <= fim)]
    df = df[(df["PERIODO"] == 'ANUAL')]

    # df = ordenar_grafico_AH(df,inicio, fim)
    df = df.sort_values('ANO') 

    indices = ["EBITDA", "EBIT", "Bruta"]        
    ind_geral = []
    for i in indices:   
        resultado = 0  # Inicializa a variável resultado
        for a in range(inicio, fim + 1):
                    if i == "EBITDA": 
                        ebit = df.loc[(df['ANO'] == a) & (df['CONTA'] == "3.05"), "VALOR"].values[0]
                        depr_amort = df.loc[(df['ANO'] == a) & (df['CONTA'] == "6.01.01.02"), "VALOR"].values[0]
                        ebitda = ebit + depr_amort # Calculo EBITDA = ebit + depreciação e amortização
                        receita_liquida = df.loc[(df['ANO'] == a) & (df['CONTA'] == "3.01"), "VALOR"].values[0]   

                        resultado =  (ebitda / receita_liquida) * 100

                    elif i == "EBIT": 
                        ebit = df.loc[(df['ANO'] == a) & (df['CONTA'] == "3.05"), "VALOR"].values[0]
                        receita_liquida = df.loc[(df['ANO'] == a) & (df['CONTA'] == "3.01"), "VALOR"].values[0]   

                        resultado =  (ebit / receita_liquida) * 100  

                    elif i == "Bruta":  #REVER  
                        lucro_bruto = df.loc[(df['ANO'] == a) & (df['CONTA'] == "3.03"), "VALOR"].values[0] 
                        receita_liquida = df.loc[(df['ANO'] == a) & (df['CONTA'] == "3.01"), "VALOR"].values[0]   

                        resultado = (lucro_bruto / receita_liquida)*100             
    
                    ind_geral.append({'MARGENS': i, 'ANO': a, 'VALOR': round(resultado,2)})                

    # Cria, ordenar e pivotar dataframe com dados dos indices   
    df_dash = pd.DataFrame(ind_geral)  
    return df_dash

# @st.cache_data
def data_dashboard(df):

    # Armazena o valor do ano mais recente
    ano_fim = df['ANO'].max()

    # Calcula qual o ano, 5 anos antes
    periodo_5anos = int(ano_fim) - 5

    # Filtra os dados
    df_5anos = df[(df["PERIODO"] == 'ANUAL') & (df["ANO"] == periodo_5anos)]
    df = df[(df["PERIODO"] == 'ANUAL') & (df["ANO"] == ano_fim)]

    # Filtra todos so valores necessários para os calculos
    patrimonio_liquido = df.loc[(df['ANO'] == ano_fim) & (df['CONTA'] == "2.03"), "VALOR"].values[0]
    emprestimo_curto_prazo = df.loc[(df['ANO'] == ano_fim) & (df['CONTA'] == "2.01.04"), "VALOR"].values[0] 
    emprestimo_longo_prazo = df.loc[(df['ANO'] == ano_fim) & (df['CONTA'] == "2.02.01"), "VALOR"].values[0]      
    equivalente_caixa = df.loc[(df['ANO'] == ano_fim) & (df['CONTA'] == "1.01.01"), "VALOR"].values[0]
    aplicacao_financeira = df.loc[(df['ANO'] == ano_fim) & (df['CONTA'] == "1.01.02"), "VALOR"].values[0]
    ebit = df.loc[(df['ANO'] == ano_fim) & (df['CONTA'] == "3.05"), "VALOR"].values[0]
    ativo_circulante = df.loc[(df['ANO'] == ano_fim) & (df['CONTA'] == "1.01"), "VALOR"].values[0]
    passivo_circulante = df.loc[(df['ANO'] == ano_fim) &  (df['CONTA'] == "2.01"), "VALOR"].values[0]
    passivo_total = df.loc[(df['ANO'] == ano_fim) & (df['CONTA'] == "2"), "VALOR"].values[0] 
    ativo_total = df.loc[(df['ANO'] == ano_fim) & (df['CONTA'] == "1"), "VALOR"].values[0]
    lucro_bruto = df.loc[(df['ANO'] == ano_fim) & (df['CONTA'] == "3.03"), "VALOR"].values[0] 
    lucro_liquido = df.loc[(df['ANO'] == ano_fim) & (df['CONTA'] == "3.11"), "VALOR"].values[0]
    receita_liquida = df.loc[(df['ANO'] == ano_fim) & (df['CONTA'] == "3.01"), "VALOR"].values[0] 
    impostos = df.loc[(df['ANO'] == ano_fim) & (df['CONTA'] == "3.08"), "VALOR"].values[0] 
    depreciacao_amortizacao = df.loc[(df['ANO'] == ano_fim) & (df['CONTA'] == "6.01.01.02"), "VALOR"].values[0]

    # Filtra dados no periodo de 5 anos
    rec_liq_cagr_vi = df_5anos.loc[(df_5anos['ANO'] == periodo_5anos) & (df_5anos['CONTA'] == "3.01"), "VALOR"].values[0] 
    cagr_lucro_liquido_vi = df_5anos.loc[(df_5anos['ANO'] == periodo_5anos) &  (df_5anos['CONTA'] == "3.11"), "VALOR"].values[0]


    # Calcula os indicadores
    # divida bruta = emprestimo curto + emprestimo longo prazo
    divida_bruta =  emprestimo_curto_prazo + emprestimo_longo_prazo   

    # caixa e equivalente de caixa e aplic. finan. curto prazo = caixa equivalente + aplicação financeira
    # caixa_equivalente_aplicacao_financeira = equivalente_caixa + aplicacao_financeira  

    # divida liquida = divida bruta - caixa e equivalente de caixa e aplicações financeiras
    # divida_liquida = divida_bruta - caixa_equivalente_aplicacao_financeira 

    # EBITDA = ebit + depreciação e amortização
    ebitda = ebit + depreciacao_amortizacao          

    indices = [
         "Div_liq_pl", "Div_liq_ebit", "CAGR RECEITAS", "CAGR LUCROS", "GA", "ROIC", "Ebit_rec_liq", "Ebitda_rec_liq", "Div_liq_ebitda", "Margem_liquida", "PL_ativos", "Passivos_ativos", "Liq_corrente", "Margem_Bruta", "ROE", "ROA"     
            ]
        
    dash_geral = []
    for i in indices:   
                    if i == "PL_ativos":                             
                        res = (ativo_total - passivo_total) / ativo_total

                    elif i == "CAGR RECEITAS":       
                        res =  ((receita_liquida / rec_liq_cagr_vi) ** (1/5) - 1) * 100
                        

                    elif i == "CAGR LUCROS":       
                        res =  ((lucro_liquido / cagr_lucro_liquido_vi) ** (1/5) - 1) * 100

                    elif i == "ROIC":       
                        res =  ((ebit + impostos) / (patrimonio_liquido + divida_bruta)) * 100

                    elif i == "GA":       
                        res =  receita_liquida / ativo_total

                    elif i == "Div_liq_pl":       
                        res =  depreciacao_amortizacao / patrimonio_liquido
                    
                    elif i == "Div_liq_ebit":  
                        res =  depreciacao_amortizacao / ebit

                    elif i == "Div_liq_ebitda": 
                        res =  depreciacao_amortizacao / ebitda 

                    elif i == "Ebitda_rec_liq": 
                        res =  (ebitda / receita_liquida) * 100

                    elif i == "Ebit_rec_liq": 
                        res =  (ebit / receita_liquida) * 100

                    elif i == "Passivos_ativos":                        
                        res =  passivo_total / ativo_total

                    elif i == "Liq_corrente":                    
                        res = ativo_circulante/ passivo_circulante
                        
                    elif i == "ROE":             
                        if ativo_total == passivo_total:
                            res = 1
                        else: res = lucro_liquido / (ativo_total - passivo_total)

                    elif i == "ROA":                    
                        res = lucro_liquido / ativo_total

                    elif i == "Margem_Bruta":  #REVER                                  
                        res = (lucro_bruto / receita_liquida)*100    

                    elif i == "Margem_liquida":        
                        res = (lucro_liquido / receita_liquida)*100                 
    
                    dash_geral.append({'ANO': ano_fim, 'ÍNDICES': i, 'VALOR': round(res,2)})                

    # Cria, ordenar e pivotar dataframe com dados dos indices   
    df_dash = pd.DataFrame(dash_geral)
    return df_dash



