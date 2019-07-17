import json
import datetime
from flask import Flask, flash, g, redirect, render_template, request, url_for, request
from werkzeug.exceptions import abort
from flask_restful import Resource, Api

from api.db import list_tp_to_list_dict, tp_to_dict, get_conn_db
from api.utils import json_response, JSON_MIME_TYPE

# Надо АПИ и обЪявление и добавдение ресурса или не надо, пока не понятно!!!!
app = Flask(__name__)


def convert_dt(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()


@app.route("/api/posts/")
def get_posts():
    '''
        Возвращает все записи базы на запром к УРЛу "/"
        в json.damp изменена выдача datetime на строчное представлние
        заменой default метода на свой в виде вызова строчного
        представлние объекта! Гениальное решение! Надеюсь
        :return: json со всеми записями
    '''
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


@app.route("/api/posts/<int:id>")
def get_post_id():
    '''
        Возвращает пост на запром к УРЛу "/posts/<int:id>"
        в json.damp
        :return: json с одной записью
    '''
    conn = get_conn_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT post.id, title, body, created, author_id, username"
        " FROM post  JOIN author ON post.author_id = author.id"
        " WHERE post.id = %s",
        (id,),
    )
    cur_post = cur.fetchone()
    post = tp_to_dict(cur_post, cur)
    cur.close()
    conn.commit()
    conn.close()

    return json_response(json.dumps(post, default=convert_dt))


@app.route("/api/posts/", methods=['POST'])
def create_post():
    '''

    '''
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


@app.route("/api/author/<int:user_id>")
def get_author_id(user_id):
    '''
    По запросу GET с user_id автора найти его в базе и вернуть словарь с данными
    :param user_id:
    :return:
    '''
    conn = get_conn_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM author WHERE id = %s", (user_id,))
    auth_cur = cur.fetchone()
    author_dic = tp_to_dict(auth_cur, cur)
    cur.close()
    conn.close()
    return json_response(json.dumps(author_dic))


@app.route("/api/author/<name>")
def get_author_name(name):
    '''
    По запросу GET с username автора найти его в базе и вернуть словарь с данными
    :param name
    :return:
    '''
    conn = get_conn_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM author WHERE username = %s", (name,))
    auth_cur = cur.fetchone()
    if auth_cur is not None:
        author_dic = tp_to_dict(auth_cur, cur)
        return json_response(json.dumps(author_dic))
    cur.close()
    conn.commit()
    conn.close()
    return json_response(json.dumps({"username": "Not_Found"}))


@app.route("/api/author/", methods=['POST'])
def create_author():
    '''
        Запросом POST принимаем параметры для нового пользователя
        из request.json и добавляем его в базу
    '''
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





# def get_post(id, check_author=True):
#     """Get a post and its author by id.
#
#     Checks that the id exists and optionally that the current user is
#     the author.
#
#     :param id: id of post to get
#     :param check_author: require the current user to be the author
#     :return: the post with author information
#     :raise 404: if a post with the given id doesn't exist
#     :raise 403: if the current user isn't the author
#     """
#     conn = get_conn_db()
#     cur = conn.cursor()
#     cur.execute(
#             "SELECT post.id, title, body, created, author_id, username"
#             " FROM post  JOIN author ON post.author_id = author.id"
#             " WHERE post.id = %s",
#             (id,),
#         )
#     cur_post = cur.fetchone()
#     post = tp_to_dict(cur_post, cur)
#     cur.close()
#     conn.commit()
#     conn.close()
#
#     if post is None:
#         abort(404, "Post id {0} doesn't exist.".format(id))
#
#     if check_author and post["author_id"] != g.user["id"]:
#         abort(403)
#
#     return post
#
#
# @bp.route("/create", methods=("GET", "POST"))
# @login_required
# def create():
#     """Create a new post for the current user."""
#     if request.method == "POST":
#         title = request.form["title"]
#         body = request.form["body"]
#         error = None
#
#         if not title:
#             error = "Title is required."
#
#         if error is not None:
#             flash(error)
#         else:
#             conn = get_conn_db()
#             cur = conn.cursor()
#             cur.execute(
#                 "INSERT INTO post (title, body, author_id)" " VALUES (%s, %s, %s)",
#                 (title, body, g.user["id"]),
#             )
#             cur.close()
#             conn.commit()
#             conn.close()
#
#             return redirect(url_for("blog.index"))
#
#     return render_template("blog/create.html")
#
#
# @bp.route("/<int:id>/update", methods=("GET", "POST"))
# @login_required
# def update(id):
#     """Update a post if the current user is the author."""
#     post = get_post(id)
#
#     if request.method == "POST":
#         title = request.form["title"]
#         body = request.form["body"]
#         error = None
#
#         if not title:
#             error = "Title is required."
#
#         if error is not None:
#             flash(error)
#         else:
#             conn = get_conn_db()
#             cur = conn.cursor()
#             cur.execute(
#                 "UPDATE post SET title = %s, body = %s WHERE id = %s", (title, body, id)
#             )
#             cur.close()
#             conn.commit()
#             conn.close()
#
#             return redirect(url_for("blog.index"))
#
#     return render_template("blog/update.html", post=post)
#
#
# @bp.route("/<int:id>/delete", methods=("POST",))
# @login_required
# def delete(id):
#     """Delete a post.
#
#     Ensures that the post exists and that the logged in user is the
#     author of the post.
#     """
#     conn = get_conn_db()
#     cur = conn.cursor()
#     cur.execute(
#         "DELETE FROM post WHERE id = %s", (id,)
#     )
#     cur.close()
#     conn.commit()
#     conn.close()
#     return redirect(url_for("blog.index"))
