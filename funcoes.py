from yahoo_fin import stock_info
import yfinance as yf
import plotly.graph_objects as go
import locale

def csv_para_df(fii_codigo, tipo):
    import glob
    import pandas as pd

    diretorio = './csv/'
    padrao = diretorio + f'/{fii_codigo}_rendimentos_*.csv'
    padrao = diretorio + f'/{fii_codigo}_{tipo}_*.csv'
    dataframes = []

    for arquivo in glob.glob(padrao):
        df = pd.read_csv(arquivo, sep=';')
        dataframes.append(df)

    resultado = pd.concat(dataframes, ignore_index=True)

    return resultado


def fii_preco(fii_codigo):
    ticker = fii_codigo+'.SA'
    atual = stock_info.get_live_price(ticker)

    hist = yf.download(ticker, period="52wk")["Close"]
    menor = hist.min()
    maior = hist.max()
    preco12meses = hist.iloc[0]
    variacao12meses = "{:.2f}%".format(100*(atual - preco12meses)/preco12meses)

    return atual, menor, maior, variacao12meses

def grafico_preco(fii_codigo):
    ticker = fii_codigo+'.SA'

    hist = yf.download(ticker, period="52wk")
    atual = hist['Close'].iloc[-1]

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'], mode='lines', name='Preço de Fechamento'))

    fig.add_trace(go.Scatter(x=[hist.index[-1]], y=[atual], mode='markers', marker=dict(color='red'), name='Preço Atual'))

    fig.update_layout(title=f'Cotação do {fii_codigo}',
                    xaxis_title='Data',
                    yaxis_title='Preço (R$)',
                    #width=width,
                    height=500,
                    showlegend=False)

    return fig

def formato_dinheiro(valor):
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    return locale.currency(valor, grouping=True), locale.format_string("%d", valor, grouping=True)

