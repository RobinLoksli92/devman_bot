from os import getenv
from time import sleep

from dotenv import load_dotenv
import telegram
import requests


def main():
    load_dotenv()
    devman_token = getenv('DEVMAN_TOKEN')
    tg_bot_token = getenv('TELEGRAM_BOT_TOKEN')
    chat_id = getenv('TELEGRAM_CHAT_ID')

    bot = telegram.Bot(tg_bot_token)

    url = 'https://dvmn.org/api/long_polling/'
    headers = {
        'Authorization': f'Token {devman_token}'
    }
    timestamp = None
    params = {
        'timestamp': timestamp
    }

    while True:
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            server_message = response.json()

            if server_message['status'] == 'timeout':
                timestamp = server_message.get('timestamp_to_request')

            elif server_message['status'] == 'found':
                timestamp = server_message.get('timestamp_to_request')
                attempts = server_message['new_attempts']
                for attempt in attempts:
                    lesson_title = attempt['lesson_title']
                    lesson_url = attempt['lesson_url']
                    if attempt['is_negative']:
                        bot.send_message(
                            chat_id=chat_id,
                            text=f'У вас проверили работу {lesson_title}, \
                                    вот ссылка на неё {lesson_url}. \
                                    К сожаению, в работе нашлись ошибки.'
                        )
                    else:
                        bot.send_message(
                            chat_id=chat_id,
                            text=f'У вас проверили работу {lesson_title}, \
                                    вот ссылка на неё {lesson_url} \
                                    Преподавателю всё понравилось. \
                                    Можно приступать к следующему уроку.'
                        )

        except requests.exceptions.ReadTimeout:
            print('Истекло время ожидания ответа от сервера!')
            continue

        except requests.exceptions.ConnectionError:
            print('Проверьте подключение к интернету')
            sleep(90)
            continue


if __name__ == '__main__':
    main()
