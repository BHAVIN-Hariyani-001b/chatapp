from flask import Blueprint, jsonify, request, session, url_for, redirect, render_template
from app import mongo
from bson.objectid import ObjectId
import datetime

chat_bp = Blueprint('chat', __name__)

def get_user_by_email(db, email):
    """Retrieve a user by email."""
    users_collection = db.users
    return users_collection.find_one({'email': email.strip().lower()})


def get_all(db):
    """Get all users with online status"""
    users = db.users.find()
    result = []
    for user in users:
        user["_id"] = str(user["_id"])
        # Include online status in user data
        user["online"] = user.get("online", False)
        user["last_seen"] = user.get("last_seen")
        result.append(user)
    return result


def get_user_online_status(db, user_id):
    """Get specific user's online status"""
    try:
        user = db.users.find_one({'_id': ObjectId(user_id)})
        if user:
            return {
                'online': user.get('online', False),
                'last_seen': user.get('last_seen')
            }
        return {'online': False, 'last_seen': None}
    except Exception as e:
        print(f"Error getting user status: {e}")
        return {'online': False, 'last_seen': None}


def conversations_create(db, sender_id, receiver_id, message_id):
    """conversations between two users and store information"""
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
                "$set": {"updated_at": datetime.datetime.now()}
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
        "created_at": datetime.datetime.now(),
        "updated_at": datetime.datetime.now()
    }

    result = conversations_collection.insert_one(conversation_data)
    return str(result.inserted_id)


def insert_message(db, message, user_id, receiver_id):
    """user message store in db and call to conversations function"""
    message_collection = db.messages
    try:
        user_message_data = {
            'sender_id': ObjectId(user_id),
            'receiver_id': ObjectId(receiver_id),
            'message': message.strip(),
            'timestamp': datetime.datetime.now(),
            'is_read': False
        }

        message_id = message_collection.insert_one(user_message_data)
        message_id = message_id.inserted_id
        conversation_id = conversations_create(db, user_id, receiver_id, message_id)
    
        return str(message_id), conversation_id

    except Exception as e:
        print("error: ", e)
        return None, None


@chat_bp.route('/message/<receiver_id>', methods=['POST'])
def message(receiver_id):
    """user send message get and redirect to chat"""
    if 'email' not in session:
        return redirect(url_for('auth.login'))

    message_text = request.form.get('message', '').strip()

    user = get_user_by_email(mongo.db, session['email'])
    sender_id = str(user['_id'])

    insert_message(mongo.db, message_text, sender_id, receiver_id)

    return redirect(url_for('chat.chat', user_id=receiver_id))

@chat_bp.route('/chat/<user_id>', methods=['GET'])
def chat(user_id):
    """chat route is process to chat send and store in db"""
    if 'email' not in session:
        return redirect(url_for('auth.login'))

    db = mongo.db
    current_user = get_user_by_email(db, session['email'])
    current_user_id = str(current_user['_id'])

    try:
        chat_user = db.users.find_one({"_id": ObjectId(user_id)})
    except:
        chat_user = None

    # Find existing conversation between the two users
    conversation = db.conversations.find_one({
        "participants": {"$all": [ObjectId(current_user_id), ObjectId(user_id)]}
    })

    messages = []
    if conversation:
        # Load all message documents by their IDs
        messages_cursor = db.messages.find({"_id": {"$in": conversation["messages"]}})
        messages = list(messages_cursor)
        # Sort messages by timestamp
        messages.sort(key=lambda x: x["timestamp"])

    # Get all users for sidebar with online status
    users = get_all(db)
    users_followed = get_user_by_email(db, session['email'])

    return render_template(
        'index.html',
        user_list=users,
        users_followed=users_followed,
        user=chat_user,
        messages=messages,
        current_user_id=current_user_id
    )

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
            "last_seen": user.get('last_seen').strftime('%Y-%m-%d %H:%M:%S') if user.get('last_seen') else None
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
                    'last_seen': datetime.datetime.now()
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
                    'last_seen': datetime.datetime.now()
                }
            }
        )
        
        return jsonify({
            'message': 'Migration completed successfully',
            'modified_count': result.modified_count
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500