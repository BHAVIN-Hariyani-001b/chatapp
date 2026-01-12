from flask import Flask
from flask_pymongo import PyMongo
from flask_socketio import SocketIO
import os
from dotenv import load_dotenv

load_dotenv()



mongo = PyMongo() 
socketio = SocketIO(cors_allowed_origins="*")

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['MONGO_URI'] = os.getenv('MONGO_URL')

    mongo.init_app(app)
    socketio.init_app(app)

    from app.routes.auth import auth_bp
    from app.routes.chat import chat_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(chat_bp)

    from app.routes.socket_events import register_socket_events
    register_socket_events(socketio)
    
    return app
