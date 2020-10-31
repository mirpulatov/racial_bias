from flask import Flask

import os

path = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)

app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
app.config['UPLOAD_PATH'] = f'{path}/static/uploads'

from app import views