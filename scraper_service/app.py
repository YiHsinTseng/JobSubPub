from flask import Flask
from flask_cors import CORS
from controllers.scraper import scraper_routes
import os

from dotenv import load_dotenv

load_dotenv()


def create_app():
    app = Flask(__name__)
    origins = os.getenv("WHITE_LIST", "").split(",")
    CORS(app, origins=origins)
    # 不想用blueprint但又想分離main.py以及路由
    scraper_routes(app)
    return app
