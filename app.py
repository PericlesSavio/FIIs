import streamlit as st
from fii import FII
from funcoes import csv_para_df, fii_preco, grafico_preco, formato_dinheiro
import warnings
warnings.simplefilter("ignore")
import pandas as pd
import plotly.graph_objs as go

st.set_page_config(layout="wide", initial_sidebar_state="expanded")

def box1(texto, numero):
    return f'<div style="border: 1px solid #EEE; padding: 10px; border-radius: 5px; background-color: #DDD;"><div style="text-align:center;"><span>{texto}</span></div><div style="text-align:center;"><span style="color: #000; font-size: 40px;"><strong>{numero}</strong></span></div></div>'

def box2(texto1, numero1, texto2, numero2):
    return f'<div style="border: 1px solid #EEE; padding: 10px; border-radius: 5px; background-color: #DDD;">' \
        f'<div style="text-align:center;"><span>{texto1}</span></div>' \
        f'<div style="text-align:center;"><span style="color: #000; font-size: 28px;"><strong>{numero1}</strong></span></div>' \
        f'<div style="text-align:center;"><span>{texto2}</span></div>' \
        f'<div style="text-align:center;"><span style="color: #000; font-size: 20px;"><strong>{numero2}</strong></span></div>' \
        '</div>'





def main():
    
    fii_codigo = st.sidebar.text_input("Digite uma string:").upper()

    if st.sidebar.button("Enter"):

        atual, menor, maior, variacao12meses = fii_preco(fii_codigo)
        informes = csv_para_df(fii_codigo, 'informes').sort_values(by='data', ascending=False).reset_index()
        rendimentos = csv_para_df(fii_codigo, 'rendimentos')
        rendimentos['data'] = pd.to_datetime(rendimentos['data_pagamento'], format='%d/%m/%Y')
        rendimentos['data'] = rendimentos['data'].dt.strftime('%Y-%m-%d')
        rendimentos = rendimentos.sort_values(by='data', ascending=False)
        valor_patrimonial_cota = formato_dinheiro(informes['valor_patrimonial_cota'][0])[0]
        patrimonio_liquido = formato_dinheiro(informes['patrimonio_liquido'][0])[0]
        pvp = "{:.2f}".format(informes['cotas_emitidas'][0]*atual/informes['patrimonio_liquido'][0])[0]
        valor_de_mercado = formato_dinheiro(atual*informes['cotas_emitidas'][0])[0]
        numero_cotistas = formato_dinheiro(informes['cotistas'][0])[1]
        cotas_emitidas = formato_dinheiro(informes['cotas_emitidas'][0])[1]
        
        st.title(fii_codigo)

        import plotly.express as px


        # Convertendo a coluna 'data' para o tipo datetime
        rendimentos['data'] = pd.to_datetime(rendimentos['data'])

        # Filtrando os dados por ano
        rendimentos_2023 = rendimentos[rendimentos['data'].dt.year == 2023]
        rendimentos_2024 = rendimentos[rendimentos['data'].dt.year == 2024]

        # Calculando a soma dos proventos por mês para cada ano
        rendimentos_2023_agrupados = rendimentos_2023.groupby(rendimentos_2023['data'].dt.month)['proventos'].sum()
        rendimentos_2024_agrupados = rendimentos_2024.groupby(rendimentos_2024['data'].dt.month)['proventos'].sum()

        # Mapeando números de meses para nomes de meses
        meses = {
            1: 'Jan',
            2: 'Fev',
            3: 'Mar',
            4: 'Abr',
            5: 'Mai',
            6: 'Jun',
            7: 'Jul',
            8: 'Ago',
            9: 'Set',
            10: 'Out',
            11: 'Nov',
            12: 'Dez'
        }

        # Criando o gráfico de barras
        trace1 = go.Bar(
            x=[meses[mes] for mes in rendimentos_2023_agrupados.index],
            y=rendimentos_2023_agrupados.values,
            name='2023',
            marker=dict(color='orange'),  # Definindo a cor laranja para as barras de 2023
            hoverinfo='text',
            text=[f'Proventos: R${valor:.2f}<br>Ano: 2023' for valor in rendimentos_2023_agrupados.values],
            textposition='none'  # Colocando o texto fora das barras
        )
        trace2 = go.Bar(
            x=[meses[mes] for mes in rendimentos_2024_agrupados.index],
            y=rendimentos_2024_agrupados.values,
            name='2024',
            hoverinfo='text',
            text=[f'Proventos: R${valor:.2f}<br>Ano: 2024' for valor in rendimentos_2024_agrupados.values],
            textposition='none'  # Colocando o texto fora das barras
        )

        layout = go.Layout(
            title='Proventos por mês',
            xaxis=dict(title='Mês'),
            yaxis=dict(title='Proventos')
        )

        fig = go.Figure(data=[trace1, trace2], layout=layout)



        





        col1, col2, col3, col4, col5 = st.columns(5)        
        col1.markdown(box1("Valor Atual", "{:.2f}".format(atual)), unsafe_allow_html=True)
        col2.markdown(box1("Min. 52 semanas", "{:.2f}".format(menor)), unsafe_allow_html=True)
        col3.markdown(box1("Max. 52 semanas", "{:.2f}".format(maior)), unsafe_allow_html=True)
        col4.markdown(box1("Dividend Yield", 'X'), unsafe_allow_html=True)
        col5.markdown(box1("Variação (52 semanas)", variacao12meses), unsafe_allow_html=True)

        st.plotly_chart(grafico_preco(fii_codigo), use_container_width=True)

        col1, col2, col3 = st.columns(3)
        col1.markdown(box2('Valor Patrimonial da Cota', valor_patrimonial_cota, 'Patrimônio', patrimonio_liquido), unsafe_allow_html=True)
        col2.markdown(box2('P/VP', pvp, 'Valor de Mercado', valor_de_mercado), unsafe_allow_html=True)
        col3.markdown(box2('Número de Cotistas', numero_cotistas, 'Cotas Emitidas', cotas_emitidas), unsafe_allow_html=True)

        st.plotly_chart(fig, use_container_width=True)




        st.dataframe(csv_para_df(fii_codigo, 'informes').sort_values(by='data', ascending=False))
        st.dataframe(rendimentos)
        st.dataframe(csv_para_df(fii_codigo, 'relatorios'))




        

        


        
        texto1 = "Texto 1"
        numero1 = 10
        texto2 = "Texto 2"
        numero2 = 20




        

















if __name__ == "__main__":
    main()
