from flask import Blueprint,jsonify,request,session,url_for,redirect,render_template
from app import mongo
from bson.objectid import ObjectId
from app import socketio

chat_bp = Blueprint('chat',__name__)

def get_user_by_email(db, email):
    """Retrieve a user by email."""

    users_collection = db.users
    return users_collection.find_one({'email': email.strip().lower()})


def get_all(db):
    users = db.users.find()
    result = []
    for user in users:
        user["_id"] = str(user["_id"]) 
        result.append(user)
    return result

@chat_bp.route('/chat/<user_id>',methods=['GET'])
def chat(user_id):
    try:    
        user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    except:
        user = None

    users = get_all(mongo.db)
    users_followed = get_user_by_email(mongo.db,session['email'])
 
    data = users if users else []

    return render_template('index.html',user_list=data,users_followed=users_followed,user=user)

@chat_bp.route('/search_chat',methods=['POST'])
def search():
    data = request.get_json()
    query = data.get("query","").strip()

    if not query:
        return jsonify({"result":[]})
    
    user_cursor = mongo.db.users.find({"name":{"$regex": query, "$options": "i"}})

    user_follow = get_user_by_email(mongo.db,session['email'])

    result = []
    for user in user_cursor:
        if str(user['_id']) in user_follow['following'] and user_follow['email'] != user['email']:
            result.append({
                "_id":str(user['_id']),
                "name":user['name'],
                "email":user['email'],
                'status':'Unfollow'
            })
        elif user_follow['email'] != user['email']:
            result.append({
                "_id":str(user['_id']),
                "name":user['name'],
                "email":user['email'],
                'status':'Follow'
            })

    return jsonify({"result":result})


@chat_bp.route('/follow_user',methods=['POST'])
def follow():
    data = request.get_json()
    user_to_follow_id = data.get('user_id')

    current_user = mongo.db.users.find_one({'email': session['email'].strip().lower()})
    print(user_to_follow_id)
    print(current_user)
    if current_user == user_to_follow_id:
        return jsonify({"message": "You cannot follow yourself!"}), 400
    
    
    if str(current_user["_id"]) != user_to_follow_id:
        if user_to_follow_id in current_user['following']:
            
            mongo.db.users.update_one(
                {"_id": current_user["_id"]},
                {"$pull": {"following": user_to_follow_id}}
            )
            mongo.db.users.update_one(
                {"_id": ObjectId(user_to_follow_id)},
                {"$pull": {"followers": current_user["_id"]}}
            )
            return jsonify({"message": "User unfollowed successfully", "status": "unfollowed"})
        else:
            # Follow (add)
            mongo.db.users.update_one(
                {"_id": current_user["_id"]},
                {"$addToSet": {"following": user_to_follow_id}}
            )
            mongo.db.users.update_one(
                {"_id": ObjectId(user_to_follow_id)},
                {"$addToSet": {"followers": current_user["_id"]}}
            )
            return jsonify({"message": "User followed successfully", "status": "followed"})

    return jsonify({"message": "User followed successfully"})

