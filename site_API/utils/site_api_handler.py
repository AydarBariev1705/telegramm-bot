from typing import Dict

import requests
import random


def _make_response(method: str, url: str, headers: Dict, timeout: int, success=200):
    response = requests.request(
        method,
        url,
        headers=headers,
        timeout=timeout
    )

    status_code = response.status_code

    if status_code == success:
        return response

    return status_code


def _get_film_by_year(method: str, url: str, headers: Dict, number: int, timeout: int, func=_make_response):
    url = "{0}/titles?year={1}".format(url, number)

    response = func(method, url, headers=headers, timeout=timeout)
    response = response.json()
    result = f'Фильмы вышедшие в {number} году:\n'
    for i in response['results']:
        result += i["titleText"]['text'] + '\n'

    return result


def _search_by_keyword(method: str, url: str, headers: Dict, keyword: str, timeout: int, func=_make_response):
    url = "{0}/titles/search/keyword/{1}".format(url, keyword)
    response = func(method, url, headers=headers, timeout=timeout)
    response = response.json()
    result = f'Список фильмов по ключевому слову "{keyword}":\n'
    for i in response['results']:
        result += i["titleText"]['text'] + '\n'

    return result


def _random_movie(headers: Dict):
    url = "https://moviesdatabase.p.rapidapi.com/titles/random"
    params = {"list": "top_rated_english_250"}
    response = requests.get(url, headers=headers, params=params)
    response = response.json()
    titles = {}
    for i in response['results']:
        titles[i["titleText"]['text']] = i['releaseYear']['year']

    temp = random.choice(list(titles))
    temp = {temp: titles[temp]}
    result = ''
    for key, value in temp.items():
        result += f'{key} ({value})'

    return result


def _upcoming_movies(headers: Dict):
    url = "https://moviesdatabase.p.rapidapi.com/titles/x/upcoming"
    response = requests.get(url, headers=headers)
    response = response.json()
    result = ''
    for i in response['results']:
        result += i["titleText"]['text']+' (' + str(i['releaseYear']['year'])+')\n'

    return result
class SiteApiInterface():

    @staticmethod
    def get_film_by_year():
        return _get_film_by_year

    @staticmethod
    def search_by_keyword():
        return _search_by_keyword

    @staticmethod
    def random_movie():
        return _random_movie

    @staticmethod
    def upcoming_movies():
        return _upcoming_movies



if __name__=="__main__":
    _make_response()
    _get_film_by_year()
    _search_by_keyword()
    _random_movie()
    _upcoming_movies()


    SiteApiInterface()
