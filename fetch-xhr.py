import csv
from playwright.sync_api import sync_playwright
import pandas as pd

#fundos = pd.read_csv('./fundosListados.csv', delimiter=';', encoding='iso-8859-1')
#fiis = (fundos['Segmento']+'11').tolist()

fiis = ['XPML', 'HSML']

fundo_info = []

def extract_response(response, fii):
    if "https://sistemaswebb3-listados.b3.com.br/fundsProxy/fundsCall/" in response.url:
        fundo_info.append({"FII": fii, "URL": response.url})

for fii in fiis:
    url = f"https://sistemaswebb3-listados.b3.com.br/fundsPage/main/0/{fii}/0/about"
    print(f'Ativo: {fii}')

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        page.on("response", lambda response: extract_response(response, fii))
        page.goto(url, wait_until="networkidle", timeout=30000)

        page.context.close()
        browser.close()

df = pd.DataFrame(fundo_info).drop_duplicates()

csv_file_path = "fundos.csv"
df.to_csv(csv_file_path, index=False)

print(f"Dados salvos em {csv_file_path}")