from flask import Flask
from flask_pymongo import PyMongo
from flask_socketio import SocketIO
from datetime import timedelta


mongo = PyMongo() 
socketio = SocketIO(cors_allowed_origins="*")

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = '********'
    app.config['MONGO_URI'] = "****************"
    # app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=1)

    mongo.init_app(app)
    socketio.init_app(app)

    from app.routes.auth import auth_bp
    from app.routes.chat import chat_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(chat_bp)

    from app.routes.socket_events import register_socket_events
    register_socket_events(socketio)
    
    return app
