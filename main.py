from os import getenv
from textwrap import dedent
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
            lesson_review_details = response.json()

            if lesson_review_details['status'] == 'timeout':
                timestamp = lesson_review_details.get('timestamp_to_request')

            elif lesson_review_details['status'] == 'found':
                timestamp = lesson_review_details.get('timestamp_to_request')
                attempts = lesson_review_details['new_attempts']
                for attempt in attempts:
                    lesson_title = attempt['lesson_title']
                    lesson_url = attempt['lesson_url']
                    text = f'''
                                У вас проверили работу {lesson_title},
                                вот ссылка на неё: {lesson_url}. 
                                К сожалению, в работе нашлись ошибки.'''
                    if attempt['is_negative']:
                        bot.send_message(
                            chat_id=chat_id,
                            text=dedent(text)
                        )
                    else:
                        text = f'''
                                    У вас проверили работу {lesson_title},
                                    вот ссылка на неё {lesson_url}. 
                                    Преподавателю всё понравилось.  
                                    Можно приступать к следующему уроку.'''

                        bot.send_message(
                            chat_id=chat_id,
                            text=dedent(text)
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
