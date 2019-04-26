from flask import Flask, request
import logging
import json
import random
import requests
import sys


app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

cities2 = {
    'париж': '2.351556,48.856663',
    'москва': '37.617635,55.755814',
    'санкт-петербург': '30.315868,59.939095',
    'нью-йорк': '-73.099544,40.853544',
    'вашингтон': '-77.036527,38.899513',
    'лондон': '81.231489,42.988897',
    'пекин': '116.391433,39.901843',
    'токио': '139.753137,35.682272',
    'лос-анджелес': '-118.252957,34.048408',
    'сан-франциско': '-122.446904,37.759351',
    'мехико': '99.133296,19.432605',
    'шанхай': '121.469645,31.231781',
    'сеул': '126.976937,37.570705',
    'киев': '30.523550,50.450441',
    'бейрут': '35.507268,33.892813',
    'дели': '76.922522,29.006405',
    'прага': '14.428983,50.080293',
    'берлин': '13.407338,52.519881',
    'минск': '27.561481,53.902496',
    'даллас': '-96.726655,32.819644',
    'самара': '50.101783,53.195538',
    'казань': '49.108795,55.796289',
    'ульяновск': '48.395568,54.298448',
    'саратов': '46.034158,51.533103',
    'саранск': '45.183938,54.187433'
}
countries = {
    'москва': 'россия',
    'париж': 'франция',
    'нью-йорк': 'сша',
}

sessionStorage = {}


@app.route('/post', methods=['POST'])
def main():
    logging.info('Request: %r', request.json)
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog(response, request.json)
    logging.info('Response: %r', response)
    return json.dumps(response)


def handle_dialog(res, req):
    user_id = req['session']['user_id']
    if req['session']['new']:
        res['response']['text'] = 'Привет! Назови своё имя!'
        sessionStorage[user_id] = {
            'first_name': None,
            'game_started': False
        }
        return


    if sessionStorage[user_id]['first_name'] is None:
        if req['request']['original_utterance'].lower() == 'помощь':
            res['response']['text'] = "Помощь"
            return
        first_name = get_first_name(req)
        if first_name is None:
            res['response']['text'] = 'Не расслышала имя. Повтори, пожалуйста!'
        else:
            sessionStorage[user_id]['first_name'] = first_name
            sessionStorage[user_id]['guessed_cities'] = []
            res['response']['text'] = f'Приятно познакомиться, {first_name.title()}. Я Алиса. Отгадаешь город по фото?'
            res['response']['buttons'] = [
                {
                    'title': 'Да',
                    'hide': True
                },
                {
                    'title': 'Нет',
                    'hide': True
                },
                {
                    'title': 'ПОМОЩЬ',
                    'hide': True
                }
            ]
    else:
        if not sessionStorage[user_id]['game_started']:
            if 'да' in req['request']['nlu']['tokens']:

                if len(sessionStorage[user_id]['guessed_cities']) == 20:
                    res['response']['text'] = 'Ты отгадал все города!'
                    res['end_session'] = True
                else:
                    sessionStorage[user_id]['game_started'] = True
                    sessionStorage[user_id]['attempt'] = 1
                    play_game(res, req)
            elif 'нет' in req['request']['nlu']['tokens']:
                res['response']['text'] = 'Ну и ладно!'
                res['end_session'] = True
            elif req['request']['original_utterance'].lower() == 'помощь':
                res['response']['text'] = "Помощь"
                return
            else:
                res['response']['text'] = 'Не поняла ответа! Так да или нет?'
                res['response']['buttons'] = [
                    {
                        'title': 'Да',
                        'hide': True
                    },
                    {
                        'title': 'Нет',
                        'hide': True
                    },
                    {
                        'title': 'ПОМОЩЬ',
                        'hide': True
                    }
                ]
        else:
            play_game(res, req)


def play_game(res, req):
    user_id = req['session']['user_id']
    attempt = sessionStorage[user_id]['attempt']
    if attempt == 1:
        key = list(cities2.keys())
        random_city = random.choice(key)
        s = cities2[random_city].split(',')
        x = s[0]
        y = s[1]
        city = random_city
        while city in sessionStorage[user_id]['guessed_cities']:
            key = list(cities2.keys())
            random_city = random.choice(key)
            s = cities2[random_city].split(',')
            x = s[0]
            y = s[1]
            city = random_city
        sessionStorage[user_id]['city'] = city
        res['response']['card'] = {}
        res['response']['card']['type'] = 'BigImage'
        res['response']['card']['title'] = 'Что это за город?'
        map_request = "http://static-maps.yandex.ru/1.x/?ll={x},{y}&z=13&l=sat".format(x=x, y=y)
        response = requests.get(map_request)
        files = {'file': response.content}
        header = {'Authorization': "OAuth AQAAAAASLQ_BAAT7oxJ8XquaA0hgnjMir0q7Io0"}
        r = requests.post("https://dialogs.yandex.net/api/v1/skills/4c1bb4af-fc41-4cca-9978-92999b7f17cf/images",
                          files=files, headers=header)
        logging.warning(r.json())
        buf_r = r.json()["image"]["id"]
        res['response']["card"]['image_id'] = buf_r
        res['response']['text'] = 'Тогда сыграем!'
        res['response']['buttons'] = [
                {
                    'title': 'Да',
                    'hide': True
                },
                {
                    'title': 'Нет',
                    'hide': True
                },
                {
                    'title': 'Показать город на карте',
                    'url': 'https://yandex.ru/maps/?mode=search&text=' + city,
                    'hide': True
                }]
    else:
        city = sessionStorage[user_id]['city']
        if req['request']['original_utterance'].lower() == 'помощь':
            res['response']['text'] = "Помощь"
            return
        if get_city(req) == city:
            res['response']['text'] = 'Правильно! Угадай следующий город'
            sessionStorage[user_id]['guessed_cities'].append(city)
            sessionStorage[user_id]['game_started'] = False
            res['response']['buttons'] = [
                {
                    'title': 'Да',
                    'hide': True
                },
                {
                    'title': 'Нет',
                    'hide': True
                },
                {
                    'title': 'Показать город на карте',
                    'url': 'https://yandex.ru/maps/?mode=search&text=' + city,
                    'hide': True
                }]
            return
        else:
            # если нет
            if attempt == 3:
                res['response']['text'] = f'Вы пытались. Это {city.title()}. Сыграем ещё?'
                sessionStorage[user_id]['game_started'] = False
                sessionStorage[user_id]['guessed_cities'].append(city)
                return
            else:
                # иначе показываем следующую картинку
                logging.warning('ХУЙХУЙХУЙХУЙХУЙХ')
                res['response']['card'] = {}
                res['response']['card']['type'] = 'BigImage'
                res['response']['card']['title'] = 'Неправильно. Угадай ещё раз'
                s = cities2[city].split(',')
                x = s[0]
                y = s[1]
                map_request = "http://static-maps.yandex.ru/1.x/?ll={x},{y}&z=15&l=sat".format(x=x, y=y)
                response = requests.get(map_request)
                files = {'file': response.content}
                header = {'Authorization': "OAuth AQAAAAASLQ_BAAT7oxJ8XquaA0hgnjMir0q7Io0"}
                r = requests.post(
                    "https://dialogs.yandex.net/api/v1/skills/4c1bb4af-fc41-4cca-9978-92999b7f17cf/images",
                    files=files, headers=header)
                logging.warning(r.json())
                buf_r = r.json()["image"]["id"]
                res['response']["card"]['image_id'] = buf_r
                res['response']['text'] = 'А вот и не угадал!'
    sessionStorage[user_id]['attempt'] += 1


def get_city(req):
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.GEO':
            return entity['value'].get('city', None)


def get_first_name(req):
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.FIO':
            return entity['value'].get('first_name', None)


if __name__ == '__main__':
    app.run()
