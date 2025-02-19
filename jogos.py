from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import os

def capturar_jogos():
    try:
        # Configurar o ChromeDriver
        chrome_driver_path = "./chromedriver-win64/chromedriver.exe"
        service = Service(chrome_driver_path)
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        driver = webdriver.Chrome(service=service, options=options)

        # URL do site de apostas
        url = "https://superbet.bet.br/apostas/futebol/hoje"
        driver.get(url)

        # Aguardar a página carregar completamente
        wait = WebDriverWait(driver, 10)

        # Nome do arquivo CSV
        arquivo_csv = "jogos_selecionados.csv"

        # Verificar se o arquivo CSV já existe, senão criar
        if not os.path.exists(arquivo_csv):
            df_existente = pd.DataFrame(columns=["Horário", "Campeonato", "Time Casa", "Time Fora", "Odd Casa", "Odd Empate", "Odd Fora", "Mercados", "URL"])
            df_existente.to_csv(arquivo_csv, index=False, encoding="utf-8")

        # Fechar pop-ups
        try:
            botao_cookies = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Aceitar todos os cookies')]")))
            botao_cookies.click()
            time.sleep(1)
        except Exception:
            pass

        try:
            botao_fechar_popup = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'close')]")))
            botao_fechar_popup.click()
            time.sleep(1)
        except Exception:
            pass

        # Clicar no botão +12h
        botao_12h = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@class='quick-filter']//button[contains(text(), '+12h')]")))
        botao_12h.click()
        time.sleep(2)

        # Função para rolar a página até o final
        def scroll_ate_fim():
            last_height = driver.execute_script("return document.body.scrollHeight")
            while True:
                driver.execute_script("window.scrollBy(0, window.innerHeight);")
                time.sleep(2)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

        # Função para capturar e salvar os jogos
        def capturar_e_salvar_dados():
            elementos = driver.find_elements(By.CLASS_NAME, "group-header__wrapper")
            novos_dados = []

            for elemento in elementos:
                try:
                    titulo = elemento.find_element(By.CLASS_NAME, "group-header__details-title-text").text
                    eventos = elemento.find_elements(By.CLASS_NAME, "event-card")

                    for evento in eventos:
                        try:
                            times = evento.find_elements(By.CLASS_NAME, "event-competitor__name")
                            odds = evento.find_elements(By.CLASS_NAME, "odd-button__odd-value-new")
                            horario_elemento = evento.find_element(By.CLASS_NAME, "event-card-label")
                            mercado_btn = evento.find_element(By.CLASS_NAME, "odd-offer__more-odds-button").text
                            link_elemento = evento.find_element(By.TAG_NAME, "a")
                            jogo_url = link_elemento.get_attribute("href")

                            if len(times) == 2 and len(odds) == 3:
                                mercados = int(mercado_btn.replace("+", "").strip())
                                if mercados >= 230:
                                    jogo = (
                                        horario_elemento.text.strip(),
                                        titulo,
                                        times[0].text.strip(),
                                        times[1].text.strip(),
                                        odds[0].text.strip(),
                                        odds[1].text.strip(),
                                        odds[2].text.strip(),
                                        mercado_btn.strip(),
                                        jogo_url
                                    )
                                    novos_dados.append(jogo)
                        except Exception:
                            continue
                except Exception:
                    continue

            if novos_dados:
                df_novos = pd.DataFrame(novos_dados, columns=["Horário", "Campeonato", "Time Casa", "Time Fora", "Odd Casa", "Odd Empate", "Odd Fora", "Mercados", "URL"])
                df_novos.to_csv(arquivo_csv, mode='a', header=not os.path.exists(arquivo_csv), index=False, encoding="utf-8")

        # Iniciar processo de coleta
        scroll_ate_fim()
        capturar_e_salvar_dados()

        driver.quit()
        df = pd.read_csv(arquivo_csv)
        df.drop_duplicates(inplace=True)
        df.to_csv(arquivo_csv, index=False, encoding="utf-8")

        return arquivo_csv

    except Exception as e:
        return f"Erro: {e}"