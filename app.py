import requests
from time import sleep
from jogos import capturar_jogos

last_update_id = None
token = '7764658414:AAFgcOnbE0NGLe-58UX8_NH79zNwjtkB7CQ'

def enviar_mensagem(chat_id, texto):
    requests.get(f'https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={texto}')

while True:
    sleep(1)

    data = requests.get(f'https://api.telegram.org/bot{token}/getUpdates?timeout=100')

    if len(data.json()['result']) > 0:
        update = data.json()['result'][-1]  # Última atualização recebida
        update_id = update['update_id']

        if last_update_id != update_id:
            if 'message' in update and 'text' in update['message']:
                chat_id = data.json()['result'][-1]['message']['chat']['id']
                mensagem = data.json()['result'][-1]['message']['text'].lower().strip()  # Converter para minúsculas e remover espaços extras

                comandos_obter_jogos = ('Selecione os jogos', 'Jogos', 'Jogos para hoje', 'selecione os jogos', 'jogos', 'jogos para hoje')

                if mensagem in comandos_obter_jogos:
                    enviar_mensagem(chat_id, "🔍 Analisando jogos, aguarde um momento...")

                    # Chamar a função para capturar jogos
                    resultado = capturar_jogos()

                    # Verificar se ocorreu um erro
                    if "Erro" in resultado:
                        enviar_mensagem(chat_id, f"⚠️ Ocorreu um erro: {resultado}")
                    else:
                        enviar_mensagem(chat_id, "✅ Jogos analisados com sucesso! Enviando arquivo...")

                        # Enviar o arquivo CSV
                        with open(resultado, 'rb') as arquivo:
                            requests.post(f'https://api.telegram.org/bot{token}/sendDocument',
                                        data={'chat_id': chat_id},
                                        files={'document': arquivo})
                else:
                    # Mensagem padrão para instruções
                    instrucoes = (
                        "🤖 *Bem-vindo ao MasterBeteiro Bot!* 🎲⚽\n\n"
                        "Use os seguintes comandos para receber o arquivos com os jogos:\n"
                        "✅ *'selecione os jogos'/'Selecione os jogos'*\n"
                        "✅ *'jogos'/'Jogos'*\n"
                        "✅ *'jogos para hoje'/'Jogos para hoje'*\n\n"
                        # "❓ Caso tenha dúvidas, basta enviar uma mensagem!"
                    )

                    enviar_mensagem(chat_id, instrucoes)

            last_update_id = update_id