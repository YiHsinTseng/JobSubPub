from prometheus_client import start_http_server

from scheduler import run_scheduler

from flask import Flask
from routes.test_controller import init_routes

import threading

def run_monitor():
    start_http_server(8001)

test_controller_app = Flask(__name__)
init_routes(test_controller_app)

def run_test_controller_app():
    test_controller_app.run(host='0.0.0.0', port=5060) 

if __name__ == "__main__":
    threading.Thread(target=run_monitor, daemon=True).start()
    threading.Thread(target=run_scheduler, daemon=True).start()
    run_test_controller_app()