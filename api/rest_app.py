import json
import datetime
from flask import Flask, request
from api.db import list_tp_to_list_dict, tp_to_dict, get_conn_db
from api.utils import json_response

app = Flask(__name__)


def convert_dt(o):
    """
    Выдает строковое представление даты из типа datetime.datetime
    :param o:
    :return: строка с датой
    """
    if isinstance(o, datetime.datetime):
        return o.__str__()


@app.route('/')
def index_page():
    title_dic = {"title_text": "REST-Full API для WEB блога на Flask"}
    return '''
        <html>
            <head>
                <title>''' + title_dic["title_text"] + '''</title>
            <style>
               #cmd {
                    font-family: 'Times New Roman', Times, serif; 
                    font-size: 110%;
                    font-style: italic; 
                    color: navy;
               }
            </style>

            </head>
            <body>
                <h2>
                    REST-Full Flask API доступа к БД Postgres для WEB блога на Flask <br>
                    Используются следующие URL:</h2><br>
                    <h3><a href="https://pg-flask-rest.herokuapp.com/api/posts/">/api/posts/</a>
                    - возвращает все посты всех авторов </h3><br>
                    <h3>/api/posts/post_id - возвращает пост с номером post_id</h3><br>
                    <h3>/api/posts/ methods 'POST' - добавляет в БД новый пост текущего автора</h3><br>
                    <h3>/api/posts/post_id methods 'PUT' - обновляет пост с номером post_id</h3><br>
                    <h3>/api/posts/post_id  methods DELETE - удаляет пост с номером post_id</h3><br>
                    <h3>/api/author/author_id - возвращает данные атора с номером author_id</h3><br>
                    <h3>/api/author/name - возвращает данные автора с именем name</h3><br>
                    <h3>/api/author/ methods POST - создает нового автора</h3><br> 
                    
                    <h3> <a href="https://github.com/kv2709/pg-flask-rest.git" target="_blank"> Исходнки на GitHub </a></h3><br> 
                              
            </body> 
        </html>'''


@app.route("/api/posts/")
def get_posts():
    """
    Возвращает все записи базы на запром к УРЛу "/"
    в json.damp изменена выдача datetime на строчное представлние
    заменой default метода на свой в виде вызова строчного
    представлние объекта! Гениальное решение! Надеюсь
    :return: json со всеми записями.
    """
    conn = get_conn_db()
    cur = conn.cursor()

    cur.execute('''
            SELECT post.id, title, body, created, author_id, username
            FROM post JOIN author ON post.author_id = author.id
            ORDER BY created DESC;
            ''')

    post_cur = cur.fetchall()
    tp_bd = list_tp_to_list_dict(post_cur, cur)
    cur.close()
    conn.commit()
    conn.close()
    return json_response(json.dumps(tp_bd, default=convert_dt))


@app.route("/api/posts/<int:post_id>")
def get_post_id(post_id):
    """
    Возвращает пост на GET запрос к URL "/posts/<int:post_id>"
    :param post_id:
    :return: json с одной записью
    """
    conn = get_conn_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT post.id, title, body, created, author_id, username"
        " FROM post  JOIN author ON post.author_id = author.id"
        " WHERE post.id = %s",
        (post_id,),
    )
    cur_post = cur.fetchone()
    post = tp_to_dict(cur_post, cur)
    cur.close()
    conn.commit()
    conn.close()

    return json_response(json.dumps(post, default=convert_dt))


@app.route("/api/posts/", methods=['POST'])
def create_post():
    """
    Добавляет новый пост в БД, с содержанием, полученным в теле запроса
        title
        body
        author_id
    :return: dictionary {"code_error": "Created_new_post"}
    """
    req = request.json
    title = req["title"]
    body = req["body"]
    author_id = req["author_id"]
    conn = get_conn_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO post (title, body, author_id)" " VALUES (%s, %s, %s)",
        (title, body, author_id),
    )
    cur.close()
    conn.commit()
    conn.close()

    return json_response(json.dumps({"code_error": "Created_new_post"}))


@app.route("/api/posts/<int:post_id>", methods=['PUT'])
def update_post(post_id):
    """
    Записывает в БД измененный  пост с номером post_id
    :param post_id:
    :return:
    """

    req = request.get_json()
    title = req["title"]
    body = req["body"]

    conn = get_conn_db()
    cur = conn.cursor()
    cur.execute(
        "UPDATE post SET title = %s, body = %s WHERE id = %s", (title, body, post_id)
    )
    cur.close()
    conn.commit()
    conn.close()

    return json_response(json.dumps({"code_error": "Updated_post"}))


@app.route("/api/posts/<int:post_id>", methods=['DELETE'])
def delete_post(post_id):
    """
    Удаляет в БД открытый на редактирование пост с номером post_id
    :param post_id:
    :return: Словарь {"code_error": "Deleted_post"}
    """
    conn = get_conn_db()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM post WHERE id = %s", (post_id,)
    )
    cur.close()
    conn.commit()
    conn.close()

    return json_response(json.dumps({"code_error": "Deleted_post"}))


@app.route("/api/author/<int:author_id>")
def get_author_id(author_id):
    """
    По запросу GET с author_id автора найти его в базе и вернуть словарь с данными
    :param author_id:
    :return: Dictionary author_dic
    """
    conn = get_conn_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM author WHERE id = %s", (author_id,))
    auth_cur = cur.fetchone()
    if auth_cur is not None:
        author_dic = tp_to_dict(auth_cur, cur)
        return json_response(json.dumps(author_dic))
    cur.close()
    conn.close()
    return json_response(json.dumps({"author_id": "Not_Found"}))


@app.route("/api/author/<name>")
def get_author_name(name):
    """
    По запросу GET с username автора найти его в базе и вернуть
    словарь с данными
    :param name
    :return: Dictionary author_dic
    """
    conn = get_conn_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM author WHERE username = %s", (name,))
    auth_cur = cur.fetchone()
    if auth_cur is not None:
        author_dic = tp_to_dict(auth_cur, cur)
        return json_response(json.dumps(author_dic))
    cur.close()
    conn.close()
    return json_response(json.dumps({"username": "Not_Found"}))


@app.route("/api/author/", methods=['POST'])
def create_author():
    """
        Запросом POST принимаем параметры для нового пользователя
        из request.json и добавляем его в базу
    """
    req = request.json
    username = req["username"]
    password_hash = req["password_hash"]
    conn = get_conn_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO author (username, password) VALUES (%s, %s)",
        (username, password_hash),
    )
    cur.close()
    conn.commit()
    conn.close()

    return json_response(json.dumps({"code_error": "Created_new_author"}))

# List of URL resource
# "/api/posts/"
# "/api/posts/<int:post_id>"
# "/api/posts/", methods=['POST']
# "/api/posts/<int:post_id>", methods=['PUT']
# "/api/posts/<int:post_id>", methods=['DELETE']
# "/api/author/<int:author_id>"
# "/api/author/<name>"
# "/api/author/", methods=['POST']
