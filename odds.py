import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Nome do arquivo CSV gerado na primeira etapa
arquivo_csv = "jogos_selecionados.csv"

# Nome do novo arquivo para armazenar os mercados estatísticos
arquivo_saida = "odds_jogos.csv"

# Configurar o ChromeDriver
chrome_driver_path = "./chromedriver-win64/chromedriver.exe"
service = Service(chrome_driver_path)
options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")  # Evita detecção de bot
driver = webdriver.Chrome(service=service, options=options)

# Ler os jogos do arquivo CSV
df = pd.read_csv(arquivo_csv)

# Criar lista para armazenar os dados de estatísticas
dados_estatisticas = []

# 🔹 Função para capturar os mercados estatísticos
def capturar_mercados_estatisticas():
    try:
        mercados = {
            "Total de Chutes no Gol": [],
            "Finalizações Totais": [],
            "Total de Chutes no Gol da Equipe": [],
            "Total de Finalizações da Equipe": []
        }

        # Percorrer cada mercado desejado
        for mercado_nome in mercados.keys():
            try:
                mercado_elemento = driver.find_element(By.XPATH, f"//div[contains(@data-id, '{mercado_nome}')]")
                linhas = mercado_elemento.find_elements(By.CLASS_NAME, "market-layout-card__row")

                for linha in linhas[1:]:  # Ignorar cabeçalho
                    try:
                        valor = linha.find_element(By.CLASS_NAME, "market-layout-card__row-specifier").text.strip()
                        mais = linha.find_elements(By.CLASS_NAME, "odd-button__odd-value")[0].text.strip()
                        menos = linha.find_elements(By.CLASS_NAME, "odd-button__odd-value")[1].text.strip()
                        mercados[mercado_nome].append(f"{valor} (Mais: {mais}, Menos: {menos})")
                    except:
                        continue
            except:
                mercados[mercado_nome].append("N/A")

        return mercados
    except Exception as e:
        print(f"⚠️ Erro ao capturar estatísticas: {e}")
        return None

# 🔹 Iterar sobre os jogos para acessar suas páginas individuais
for index, row in df.iterrows():
    try:
        campeonato = row["Campeonato"]
        time_casa = row["Time Casa"]
        time_fora = row["Time Fora"]

        # Construir URL do jogo (Ajuste caso necessário)
        url_jogo = f"https://superbet.bet.br/evento/{time_casa.lower()}-{time_fora.lower()}"

        print(f"🔍 Acessando {url_jogo}")
        driver.get(url_jogo)
        time.sleep(2)  # Espera o jogo carregar

        # Clicar na aba "Estatísticas"
        try:
            aba_estatisticas = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Estatísticas')]"))
            )
            aba_estatisticas.click()
            time.sleep(2)
        except Exception as e:
            print(f"⚠️ Não foi possível acessar a aba 'Estatísticas' para {time_casa} x {time_fora}: {e}")
            continue

        # Capturar odds dos mercados de estatísticas
        estatisticas = capturar_mercados_estatisticas()

        if estatisticas:
            dados_estatisticas.append({
                "Campeonato": campeonato,
                "Time Casa": time_casa,
                "Time Fora": time_fora,
                "Total de Chutes no Gol": ", ".join(estatisticas["Total de Chutes no Gol"]),
                "Finalizações Totais": ", ".join(estatisticas["Finalizações Totais"]),
                "Total de Chutes no Gol da Equipe": ", ".join(estatisticas["Total de Chutes no Gol da Equipe"]),
                "Total de Finalizações da Equipe": ", ".join(estatisticas["Total de Finalizações da Equipe"])
            })

    except Exception as e:
        print(f"⚠️ Erro ao processar o jogo {time_casa} x {time_fora}: {e}")
        continue

# 🔹 Salvar os dados capturados no novo CSV
df_estatisticas = pd.DataFrame(dados_estatisticas)
df_estatisticas.to_csv(arquivo_saida, index=False, encoding="utf-8")
print(f"✅ Dados salvos em '{arquivo_saida}'")

# Fechar o navegador
driver.quit()
