from flask import Blueprint, jsonify, request, session, url_for, redirect, render_template
from app import mongo
from bson.objectid import ObjectId
from datetime import datetime, timezone
from pymongo.errors import PyMongoError,DuplicateKeyError,NetworkTimeout,OperationFailure
from bson.errors import InvalidId



chat_bp = Blueprint('chat', __name__)

def get_user_by_email(db, email):
    """Retrieve a user by email."""
    try:
        if not email:
            print("❌ Error: Email cannot be empty")
            return None

        users_collection = db.users
        email_normalized = email.strip().lower()
        user = users_collection.find_one({'email': email_normalized})
        
        return user
    
    except NetworkTimeout as e:
        print(f"❌ Network Timeout Error: {e}")
        return None
    
    except OperationFailure as e:
        print(f"❌ Database Operation Failed: {e}")
        return None
    
    except PyMongoError as e:
        print(f"❌ MongoDB Error: {e}")
        return None
    
    except Exception as e:
        print(f"❌ Unexpected Error: {type(e).__name__} - {e}")
        return None

def get_all(db):
    """Get all users with online status"""
    try:
        users = db.users.find()
        result = []
        for user in users:
            user["_id"] = str(user["_id"])
            # Include online status in user data
            user["online"] = user.get("online", False)
            user["last_seen"] = user.get("last_seen")
            result.append(user)
        return result
    except NetworkTimeout as e:
        print(f"❌ Network Timeout Error: {e}")
        return []
    
    except OperationFailure as e:
        print(f"❌ Database Operation Failed: {e}")
        return []
    
    except PyMongoError as e:
        print(f"❌ MongoDB Error: {e}")
        return []
    
    except Exception as e:
        print(f"❌ Unexpected Error: {type(e).__name__} - {e}")
        return []


def get_user_online_status(db, user_id):
    """Get specific user's online status"""
    try:
        if not user_id:
            print("❌ Error: user_id cannot be empty")
            return {'online': False, 'last_seen': None}
        try:
            user_oid =  ObjectId(user_id)
        except InvalidId as e:
            print(f"❌ Invalid ObjectId format: {e}")
            return {'online': False, 'last_seen': None}

        user = db.users.find_one({'_id':user_oid})
        if user:
            return {
                'online': user.get('online', False),
                'last_seen': user.get('last_seen')
            }
        return {'online': False, 'last_seen': None}
    
    except InvalidId as e:
        print(f"❌ Invalid ObjectId Error: {e}")
        return {'online': False, 'last_seen': None}
    
    except NetworkTimeout as e:
        print(f"❌ Network Timeout Error: {e}")
        return {'online': False, 'last_seen': None}
    
    except OperationFailure as e:
        print(f"❌ Database Operation Failed: {e}")
        return {'online': False, 'last_seen': None}
    
    except PyMongoError as e:
        print(f"❌ MongoDB Error: {e}")
        return {'online': False, 'last_seen': None}
    
    except Exception as e:
        print(f"❌ Unexpected Error: {type(e).__name__} - {e}")
        return {'online': False, 'last_seen': None} 

def conversations_create(db, sender_id, receiver_id, message_id):
    """conversations between two users and store information"""
    try:
    
        conversations_collection = db.conversations

        # Check if conversation already exists between both users
        existing_conversation = conversations_collection.find_one({
            "type": "private",
            "participants": {"$all": [ObjectId(sender_id), ObjectId(receiver_id)]}
        })

        # If conversation exists → just append the message ID
        if existing_conversation:
            conversations_collection.update_one(
                {"_id": existing_conversation["_id"]},
                {
                    "$push": {"messages": ObjectId(message_id)},
                    "$set": {"updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")}
                }
            )
            return str(existing_conversation["_id"])

        # If not exists → create a new one
        conversation_data = {
            "type": "private",
            "participants": [
                ObjectId(sender_id),
                ObjectId(receiver_id)
            ],
            "messages": [ObjectId(message_id)],
            "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        }

        result = conversations_collection.insert_one(conversation_data)
        return str(result.inserted_id)
    except InvalidId:
        print("❌ Invalid ObjectId format")
        return None
    except DuplicateKeyError:
        print("❌ Duplicate conversation already exists")
        return None
    except NetworkTimeout:
        print("❌ Database connection timeout")
        return None
    except PyMongoError as e:
        print(f"❌ Database error: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None


def insert_message(db, message, user_id, receiver_id):
    """user message store in db and call to conversations function"""
    try:
        message_collection = db.messages
        user_message_data = {
            'sender_id': ObjectId(user_id),
            'receiver_id': ObjectId(receiver_id),
            'message': message.strip(),
            'timestamp': datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            'is_read': False
        }

        message_id = message_collection.insert_one(user_message_data)

        message_id = message_id.inserted_id
        conversation_id = conversations_create(db, user_id, receiver_id, message_id)
    
        return str(message_id), conversation_id
    
    except NetworkTimeout as e:
        print(f"Network Error : {e}")
        return None,None
    except PyMongoError as e:
        print(f"Mongodb error : {e} ")
        return None,None
    except Exception as e:
        print("error: ", e)
        return None, None


# @chat_bp.route('/message/<receiver_id>', methods=['POST'])
# def message(receiver_id):
#     """user send message get and redirect to chat"""
#     if 'email' not in session:
#         return redirect(url_for('auth.login'))

#     message_text = request.form.get('message', '').strip()

#     user = get_user_by_email(mongo.db, session['email'])
#     sender_id = str(user['_id'])

#     insert_message(mongo.db, message_text, sender_id, receiver_id)

#     return redirect(url_for('chat.chat', user_id=receiver_id))


def updateProfile(db,name,about):
    """Update profile"""
    try:
        users_collection = db.users

        user = get_user_by_email(mongo.db, session['email'])
        id = str(user['_id'])
        users_collection.update_one(
            {"_id":ObjectId(id)},
            {"$set": {"name": name, "about": about}}
        )
    except Exception as e:
        return
    

@chat_bp.route('/editProfile',methods=['POST'])
def editProfile():
    if 'email' not in session:
        return redirect(url_for('auth.login'))

    name = request.form.get('name')
    about = request.form.get('about')

    updateProfile(mongo.db,name,about)

    if name and about:
        session['name'] = name
        session['about'] = about

    users = get_all(mongo.db)
    users_followed = get_user_by_email(mongo.db,session['email'])
 
    data = users if users else []

    return render_template('index.html',user_list=data,users_followed=users_followed)


@chat_bp.route('/api/chat/<chat_id>',methods=['GET'])
def message(chat_id):
    if 'email' not in session:
        return redirect(url_for('auth.login'))

    try:
        db = mongo.db
        current_user_id = session.get('user_id')

        # Find existing conversation between the two users
        conversation = db.conversations.find_one({
            "participants": {"$all": [ObjectId(current_user_id), ObjectId(chat_id)]}
        })

        messages = []
        if conversation:
            # Load all message documents by their IDs
            messages_cursor = db.messages.find({"_id": {"$in": conversation["messages"]}})
            messages = list(messages_cursor)
            # Sort messages by timestamp
            messages.sort(key=lambda x: x["timestamp"])

        return jsonify({
            "status":"success",
            "messages":messages
        })
    except Exception as e:
        return jsonify({
            "status":"failed",
            "messages":[],
            "error":e
        })


# @chat_bp.route('/chat/<user_id>', methods=['GET'])
# def chat(user_id):
#     """chat route is process to chat send and store in db"""
#     if 'email' not in session:
#         return redirect(url_for('auth.login'))

#     db = mongo.db
#     current_user = get_user_by_email(db, session['email'])
#     current_user_id = str(current_user['_id'])

#     try:
#         chat_user = db.users.find_one({"_id": ObjectId(user_id)})
#     except:
#         chat_user = None

#     # Find existing conversation between the two users
#     conversation = db.conversations.find_one({
#         "participants": {"$all": [ObjectId(current_user_id), ObjectId(user_id)]}
#     })

#     messages = []
#     if conversation:
#         # Load all message documents by their IDs
#         messages_cursor = db.messages.find({"_id": {"$in": conversation["messages"]}})
#         messages = list(messages_cursor)
#         # Sort messages by timestamp
#         messages.sort(key=lambda x: x["timestamp"])

#     # Get all users for sidebar with online status
#     users = get_all(db)
#     users_followed = get_user_by_email(db, session['email'])

#     return render_template(
#         'index.html',
#         user_list=users,
#         users_followed=users_followed,
#         user=chat_user,
#         messages=messages,
#         current_user_id=current_user_id
#     )

@chat_bp.route('/search_chat', methods=['POST'])
def search():
    """search route is user search and follow and unfollow user status update/change"""
    data = request.get_json()
    query = data.get("query", "").strip()

    if not query:
        return jsonify({"result": []})
    
    user_cursor = mongo.db.users.find({"name": {"$regex": query, "$options": "i"}})

    user_follow = get_user_by_email(mongo.db, session['email'])

    result = []
    for user in user_cursor:
        user_data = {
            "_id": str(user['_id']),
            "name": user['name'],
            "email": user['email'],
            "online": user.get('online', False),  # Include online status
            "last_seen": user.get('last_seen') 
        }
        
        if str(user['_id']) in user_follow['following'] and user_follow['email'] != user['email']:
            user_data['status'] = 'Unfollow'
            result.append(user_data)
        elif user_follow['email'] != user['email']:
            user_data['status'] = 'Follow'
            result.append(user_data)

    return jsonify({"result": result})


@chat_bp.route('/follow_user', methods=['POST'])
def follow():
    """follow route is follow and unfollow process"""
    data = request.get_json()
    user_to_follow_id = data.get('user_id')

    current_user = mongo.db.users.find_one({'email': session['email'].strip().lower()})
    
    if str(current_user["_id"]) != user_to_follow_id:
        if user_to_follow_id in current_user['following']:
            # Unfollow
            mongo.db.users.update_one(
                {"_id": current_user["_id"]},
                {"$pull": {"following": user_to_follow_id}}
            )
            mongo.db.users.update_one(
                {"_id": ObjectId(user_to_follow_id)},
                {"$pull": {"followers": str(current_user["_id"])}}
            )
            return jsonify({"message": "User unfollowed successfully", "status": "unfollowed"})
        else:
            # Follow
            mongo.db.users.update_one(
                {"_id": current_user["_id"]},
                {"$addToSet": {"following": user_to_follow_id}}
            )
            mongo.db.users.update_one(
                {"_id": ObjectId(user_to_follow_id)},
                {"$addToSet": {"followers": str(current_user["_id"])}}
            )
            return jsonify({"message": "User followed successfully", "status": "followed"})

    return jsonify({"message": "Cannot follow yourself"})


# ===== NEW ROUTES FOR ONLINE STATUS =====

@chat_bp.route('/api/user_status/<user_id>', methods=['GET'])
def api_user_status(user_id):
    """REST API endpoint to check user online status"""
    if 'email' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        status = get_user_online_status(mongo.db, user_id)
        
        return jsonify({
            'user_id': user_id,
            'online': status['online'],
            'last_seen': status['last_seen'].strftime('%Y-%m-%d %H:%M:%S') if status['last_seen'] else None
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@chat_bp.route('/api/online_users', methods=['GET'])
def api_online_users():
    """Get list of all currently online users"""
    if 'email' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        # Find all users where online is True
        online_users = mongo.db.users.find({'online': True})
        
        result = []
        for user in online_users:
            result.append({
                'user_id': str(user['_id']),
                'name': user.get('name', 'Unknown'),
                'email': user.get('email', ''),
                'online': True
            })
        
        return jsonify({'users': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@chat_bp.route('/api/update_online_status', methods=['POST'])
def api_update_online_status():
    """Update user's online status manually (backup method)"""
    if 'email' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        online = data.get('online', False)
        
        user = get_user_by_email(mongo.db, session['email'])
        
        mongo.db.users.update_one(
            {'_id': user['_id']},
            {
                '$set': {
                    'online': online,
                    'last_seen': datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                }
            }
        )
        
        return jsonify({
            'message': 'Status updated successfully',
            'online': online
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ===== MIGRATION FUNCTION (Run once to add online fields to existing users) =====
@chat_bp.route('/migrate_online_status', methods=['GET'])
def migrate_online_status():
    """Add online and last_seen fields to all existing users - Run once"""
    if 'email' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        # Update all users to include online status fields if they don't have them
        result = mongo.db.users.update_many(
            {
                '$or': [
                    {'online': {'$exists': False}},
                    {'last_seen': {'$exists': False}}
                ]
            },
            {
                '$set': {
                    'online': False,
                    'last_seen': datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                }
            }
        )
        
        return jsonify({
            'message': 'Migration completed successfully',
            'modified_count': result.modified_count
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500