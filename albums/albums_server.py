from bottle import route
from bottle import run
from bottle import HTTPError
from bottle import request
import re

import album

def check_in(strng, expression='\w+'):
    """
    Функция проверки корректности исходных данных регулярками, strng - проверяемая строка, expression - выражение, которому строка должна соответствовать
    """
    strng = strng
    #проверка на пустую строку
    if strng:
        if not re.match(expression, strng): strng = None
    return strng

@route("/albums/<artist>")
def albums(artist):
    """
    Функция поиска артиста по БД, принимает GET
    """
    #ищем артиста
    albums_list = album.find(artist)
    #не нашли
    if not albums_list:
        message = "Альбомов {} не найдено".format(artist)
        result = HTTPError(404, message)
    #нашли
    else:
        #получаем количество альбомов, названия и склеиваем через <br>
        album_quant = len(albums_list)
        album_names = [album.album for album in albums_list]
        result = "Найдено {} альбомов исполнителя {}: <br>".format(album_quant, artist)
        result += "<br>".join(album_names)
    return result

@route("/albums", method="POST")
def albums_add():
    """
    Функция добавления артиста в БД, принимает POST
    """
    #получаем все поля
    incoming = {
        'year' : check_in(request.forms.get("year"), r'^\d{4}$'),
        'artist' : check_in(request.forms.get("artist")),
        'genre' : check_in(request.forms.get("genre"), r'^[a-zA-Zа-яА-Я]+$'),
        'album' : check_in(request.forms.get("album"))
    }
    #проверяем входные данные на корректность, если None, то данные не корректны
    for k,v in incoming.items():
        if v == None: return HTTPError(400, 'Не верно введен параметр {}'.format(k))
    #смотрим, если в БД уже есть такой альбом данного артиста
    albums_list = album.find(incoming['artist'])
    if albums_list:
        if incoming['album'] in [album.album for album in albums_list]:
            return HTTPError(409, 'Альбом {} уже есть в базе данных'.format(incoming['album']))
    #если все хорошо, значит добавляем в БД. Подсовываем все поля в класс и отправляем его в функцию добавления dump_album
    print('Добавление нового альбома')
    new_alb = album.Album(
        year=int(incoming['year']),
        artist=incoming['artist'],
        genre=incoming['genre'],
        album=incoming['album']
        )
    return album.dump_album(new_alb)

if __name__ == "__main__":
    run(host="localhost", port=8080, debug=True)