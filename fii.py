import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import re
import calendar


class FII:

    def __init__(self, fii_codigo, ano, mes):
        self.fii_codigo = fii_codigo
        self.ano = ano
        self.mes = mes

    def ultimo_dia(self, ano, mes):
        return calendar.monthrange(ano, mes)[1]

    def noticias(self):
        ultimo_dia = self.ultimo_dia(self.ano, self.mes)
        return f"https://sistemasweb.b3.com.br/PlantaoNoticias/Noticias/ListarTitulosNoticias?agencia=18&palavra={self.fii_codigo[:4]}&dataInicial={self.ano}-{self.mes}-01&dataFinal={self.ano}-{self.mes}-{ultimo_dia}"

    def json(self):
        response = requests.get(self.noticias())
        return response.json()
    
    def json_item(self, texto):
        json_item = []
        json_relatorios = self.json()
        for item in json_relatorios:
            headline = item['NwsMsg']['headline']
            if texto in headline:
                json_item .append(item)
        return json_item[0]
    
    def url_noticia(self, texto):
        json_item = self.json_item(texto)
        item_IdNoticia = json_item['NwsMsg']['id']
        item_IdAgencia = json_item['NwsMsg']['IdAgencia']
        item_dateTime = json_item['NwsMsg']['dateTime'].replace(' ', '%20')
        url = f'https://sistemasweb.b3.com.br/PlantaoNoticias/Noticias/Detail?idNoticia={item_IdNoticia}&agencia={item_IdAgencia}&dataNoticia={item_dateTime}'
        pattern = r'dataNoticia=(.*?)%20'
        data = re.findall(pattern, url)
        return url, data
    
    def url_documento(self, texto):
        url = self.url_noticia(texto)[0]
        response = requests.get(url)
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        pre_element = soup.find('pre', id='conteudoDetalhe')
        pre_text = pre_element.get_text()
        padrao = r'(https?://[^&]+)'
        resultado = re.search(padrao, pre_text)
        url = resultado.group(1).replace('visualizarDocumento', 'exibirDocumento').split('&')[0]
        return url
    
    def soup(self, texto):
        url = self.url_documento(texto)
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        return soup
    
    def soup_webdriver(self, texto):
        url = self.url_documento(texto)
        driver = webdriver.Chrome()
        driver.get(url)
        driver.implicitly_wait(5)
        html = driver.page_source
        driver.quit()
        return BeautifulSoup(html, 'html.parser')
    
    def html(self, texto, elementos):
        html = self.soup_webdriver(texto).find_all(elementos)
        return html
    
    def tabelas(self, texto, elementos):
        tabelas = self.html(texto, elementos)
        return tabelas
    
    def indice(self, tabela, expressao):
        indice = None
        for i, linha in enumerate(tabela):
            if expressao in linha:
                indice = i
                break
        return indice
    
    def str_para_float(self, valor):
        return float(valor.replace(".", "").replace(",", "."))
    
    def str_para_int(self, valor):
        return int(float(valor.replace(".", "").replace(",", ".")))
    
    def tabela(self, i, tabelas_fii):
            tabela = tabelas_fii[i].find_all('td')
            info = [item.text for item in tabela]
            info = [info.strip() for info in info]
            return info
    
    def fii_informe(self):
        texto = 'Informe Mensal'
        elementos = 'table'
        tabelas_fii = self.tabelas(texto, elementos)
        
        df_dados_fundos = self.tabela(0, tabelas_fii)
        df_cotistas = self.tabela(1, tabelas_fii)
        df_ativos = self.tabela(2, tabelas_fii)
        df_ativos2 = self.tabela(3, tabelas_fii)
        df_passivos = self.tabela(4, tabelas_fii)

        pattern = r'Mandato:\s*</b>(.*?)</span><span class="dado-cabecalho"><b>Segmento de Atuação:\s*</b>(.*?)</span><span class="dado-cabecalho"><b>Tipo de Gestão:\s*</b>(.*?)</span></td>'
        match = re.search(pattern, str(tabelas_fii[0]))

        df_fii = pd.DataFrame({
            'codigo_isin': [df_dados_fundos[self.indice(df_dados_fundos, 'Código ISIN')+1]],
            'cotistas': [self.str_para_int(df_cotistas[self.indice(df_cotistas, 'Número de cotista')+1])],
            'patrimonio_liquido': [self.str_para_float(df_ativos[self.indice(df_ativos, 'Patrimônio Líquido')+1])],
            'cotas_emitidas': [self.str_para_int(df_ativos[self.indice(df_ativos, 'Número de Cotas Emitidas')+1])],
            'valor_patrimonial_cota': [self.str_para_float(df_ativos[self.indice(df_ativos, 'Valor Patrimonial das Cotas')+1])],
            'valor_em_caixa': [self.str_para_float(df_ativos2[self.indice(df_ativos2, 'Total mantido para as Necessidades de Liquidez')+1])],
            'patrimonio_liquido': [self.str_para_float(df_ativos[self.indice(df_ativos, 'Patrimônio Líquido')+1])],
            'total_investido': [self.str_para_float(df_ativos2[self.indice(df_ativos2, 'Total investido')+1])],
            'passivo': [self.str_para_float(df_passivos[self.indice(df_passivos, 'Total do passivo')+1])],
            'mandato': [match.group(1).strip()],
            'seguimento': [match.group(2).strip()],
            'tipo_gestão': [match.group(3).strip()],
            'competencia': [df_dados_fundos[self.indice(df_dados_fundos, 'Competência')+1]],
            'data': [self.url_noticia(texto)[1][0]]
        })        
        return df_fii
    
    def fii_rendimento(self):
        texto = 'Aviso aos Cotistas'
        elementos = 'table'
        tabelas_fii = self.tabelas(texto, elementos)

        df_dados_fundos = self.tabela(0, tabelas_fii)
        proventos = self.tabela(1, tabelas_fii)

        df_fii = pd.DataFrame({
            'codigo_isin': [proventos[self.indice(proventos, 'Código ISIN')+1]],
            'codigo_negociacao': [proventos[self.indice(proventos, 'Código de negociação')+1]],
            'proventos': [self.str_para_float(proventos[self.indice(proventos, 'Valor do provento')+1])],
            'data_base': [proventos[self.indice(proventos, 'Data-base')+1]],
            'data_pagamento': [proventos[self.indice(proventos, 'Data do pagamento')+1]],
            'periodo': [proventos[self.indice(proventos, 'Período de referência')+1]],
        })

        return df_fii
    
    def fii_relatorios(self):
        relatorios = self.json()
        df = pd.json_normalize(relatorios)
        df['dia_hora'] = df['NwsMsg.dateTime']
        df['NwsMsg.dateTime'] = df['NwsMsg.dateTime'].str.replace(' ', '%20')
        df['link'] = 'https://sistemasweb.b3.com.br/PlantaoNoticias/Noticias/Detail?idNoticia=' + df['NwsMsg.id'].astype(str) + '&agencia=' + df['NwsMsg.IdAgencia'].astype(str) + '&dataNoticia=' + df['NwsMsg.dateTime'].astype(str)
        
        for index, row in df.iterrows():
            url = row['link']
            response = requests.get(url)
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            pre_element = soup.find('pre', id='conteudoDetalhe')
            pre_text = pre_element.get_text() if pre_element else ''
            padrao = r'(https?://[^&]+)'
            resultado = re.search(padrao, pre_text)
            if resultado:
                url_atualizada = resultado.group(1).replace('visualizarDocumento', 'exibirDocumento').split('&')[0]
                df.at[index, 'link'] = url_atualizada

        df.columns = ['IdAgencia', 'content', 'dateTime', 'headline', 'id', 'dia_hora', 'link']
        
        return df
    

