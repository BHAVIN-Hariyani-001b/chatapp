from flask import Flask
from flask_pymongo import PyMongo
from datetime import timedelta
from flask_socketio import SocketIO,join_room,leave_room,emit

mongo = PyMongo() 
socketio = SocketIO()

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'Bhavin'
    app.config['MONGO_URI'] = "mongodb+srv://bhavin:bhavin@bhavin.eo9mktg.mongodb.net/chatapp?retryWrites=true&w=majority"
    # app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

    mongo.init_app(app)
    socketio.init_app(app)

    from app.routes.auth import auth_bp
    from app.routes.chat import chat_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(chat_bp)
    
    return app
