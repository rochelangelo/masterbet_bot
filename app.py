import requests
from time import sleep

last_update_id = None

while True:
    sleep(1)
    token = '7764658414:AAFgcOnbE0NGLe-58UX8_NH79zNwjtkB7CQ'

    data = requests.get(f'https://api.telegram.org/bot{token}/getUpdates?timeout=100')

    if len(data.json()['result']) > 0:
        update_id = data.json()['result'][-1]['update_id']
        if last_update_id != update_id:
            chat_id = data.json()['result'][-1]['message']['chat']['id']
            mensagem = data.json()['result'][-1]['message']['text']

            if mensagem in ('selecione os jogos', 'jogos', 'jogos para hoje'):
                mensagem_aguarde = 'Analisando aguarde, MasterBeteiro!'
                requests.get(f'https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={mensagem_aguarde}')

            last_update_id = update_id