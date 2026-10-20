import os
import sys
import signal
import logging
from flask import Flask
from app.config import Config
from app.db import db
import app.models
from app.services.task_pool import shutdown_task_pool
from app.routes import all_blueprints

logging.basicConfig(level=logging.INFO,format='[%(asctime)s] %(levelname)s: %(message)s')

def create_app():
    app=Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    
    for bp in all_blueprints:
        app.register_blueprint(bp)
        logging.info(f"Successfully registered routing engine Blueprint: '{bp.name}'")
    
    with app.app_context():
        db.create_all()
        print("Flask-SQLAlchemy schema initialized inside PostgreSQL successfully.")
    
    def handle_graceful_shutdown(signum,frame):
        logging.info(f"Received signal ({signum}). Starting graceful shutdown sequence...")
        shutdown_task_pool()
        
        logging.info("System cleanup complete. Exiting cleanly.")
        sys.exit(0)
        
    
    signal.signal(signal.SIGTERM,handle_graceful_shutdown)
    signal.signal(signal.SIGINT,handle_graceful_shutdown)
        
    return app

