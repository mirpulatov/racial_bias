from app import app, utils
from flask import Flask, render_template, request, redirect, url_for

import os
import logging


@app.errorhandler(413)
def too_large(e):
    return utils.message_by_code(413), 413

@app.route("/", methods=["GET"])
def index():
    # Обрабатываем ответы через URL params
    message = ""
    code = request.args.get('code', type = int)
    if code:
        message = utils.message_by_code(code)
    
    # Возвращаем главную страницу
    return render_template("index.html",
        title = 'Home page',
        app_name = utils.get_app_name(),
        message = message)

@app.route("/", methods=["POST"])
def upload():
    # Запускаем функцию обработки файлов
    result = utils.proccess_files(request.files, app.config['UPLOAD_PATH'])
    logging.warning(result)

    if result['status']:
        # Тут вызываем процедуру нейронки
        # В которую передаем result['result']
        pass

    return redirect(url_for('index', code=result['code']))