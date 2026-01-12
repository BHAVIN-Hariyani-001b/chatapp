# ===== app/socket_events.py =====
from flask_socketio import emit, join_room, leave_room
from flask import request,session
from app import mongo
from bson.objectid import ObjectId
from datetime import datetime,timezone

# Store active users with their socket IDs
active_users = {}  # Format: {socket_id: {user_id, username, rooms, last_seen}}
user_sockets = {}  # Format: {user_id: [socket_id1, socket_id2]} for multiple tabs

def register_socket_events(socketio):

    @socketio.on('join')
    def handle_join(data):
        # Access current_user safely here
        user_id = str(session['user_id'])
        username = session['name']

        print(f"User connected: {username} ({user_id})")

        # Add user to active_users and user_sockets
        active_users[request.sid] = {
            'user_id': user_id,
            'username': username,
            'rooms': [],
            'last_seen': datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        }

        if user_id not in user_sockets:
            user_sockets[user_id] = []
        user_sockets[user_id].append(request.sid)

        emit('connection_response', {'data': f'{username} is connected'})

    
    @socketio.on('connect')
    def handle_connect():
        print(f'Client connected: {request.sid}')
        emit('connection_response', {'data': 'Connected to server'})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        if request.sid in active_users:
            user_info = active_users[request.sid]
            user_id = user_info['user_id']
            
            # Remove this socket from user's socket list
            if user_id in user_sockets:
                if request.sid in user_sockets[user_id]:
                    user_sockets[user_id].remove(request.sid)
                
                # If user has no more active sockets, mark as offline
                if len(user_sockets[user_id]) == 0:
                    del user_sockets[user_id]
                    
                    # Update database: user is offline
                    try:
                        mongo.db.users.update_one(
                            {'_id': ObjectId(user_id)},
                            {
                                '$set': {
                                    'online': False,
                                    'last_seen': datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                                }
                            }
                        )
                        
                        # Broadcast to all users that this user went offline
                        emit('user_status_change', {
                            'user_id': user_id,
                            'username': user_info['username'],
                            'status': 'offline',
                            'last_seen': datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                        }, broadcast=True)
                        
                        print(f"User {user_info['username']} ({user_id}) is now OFFLINE")
                    except Exception as e:
                        print(f"Error updating user status: {e}")
            
            # Clean up active users
            del active_users[request.sid]
        
        print(f'Client disconnected: {request.sid}')
    
    @socketio.on('user_online')
    def handle_user_online(data):
        """Handle user coming online"""
        user_id = data.get('user_id')
        username = data.get('username')
        
        if not user_id or not username:
            print("Missing user_id or username in user_online event")
            return
        
        # Store user info with this socket
        active_users[request.sid] = {
            'user_id': user_id,
            'username': username,
            'rooms': [],
            'last_seen': datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        }
        
        # Track all sockets for this user (for multiple tabs)
        if user_id not in user_sockets:
            user_sockets[user_id] = []
        user_sockets[user_id].append(request.sid)
        
        # Update user status in database
        try:
            mongo.db.users.update_one(
                {'_id': ObjectId(user_id)},
                {
                    '$set': {
                        'online': True,
                        'last_seen': datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                    }
                }
            )
            
            # Broadcast user online status to everyone
            emit('user_status_change', {
                'user_id': user_id,
                'username': username,
                'status': 'online'
            }, broadcast=True)
            
            # Send list of currently online users to this user
            online_user_ids = list(user_sockets.keys())
            online_users_data = []
            
            for uid in online_user_ids:
                user_doc = mongo.db.users.find_one({'_id': ObjectId(uid)})
                if user_doc:
                    online_users_data.append({
                        'user_id': uid,
                        'username': user_doc.get('name', 'Unknown'),
                        'status': 'online'
                    })
            
            emit('online_users_list', {'users': online_users_data})
            
            print(f"User {username} ({user_id}) is now ONLINE (Socket: {request.sid})")
            print(f"Active sockets for user {user_id}: {len(user_sockets.get(user_id, []))}")
            print(f"Total online users: {len(user_sockets)}")
            
        except Exception as e:
            print(f"Error updating user status: {e}")
    
    @socketio.on('heartbeat')
    def handle_heartbeat(data):
        """Handle periodic heartbeat to keep user online"""
        user_id = data.get('user_id')
        
        if request.sid in active_users:
            active_users[request.sid]['last_seen'] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            
            # Update last_seen in database
            try:
                mongo.db.users.update_one(
                    {'_id': ObjectId(user_id)},
                    {'$set': {'last_seen': datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")}}
                )
            except Exception as e:
                print(f"Error updating heartbeat: {e}")
    
    # @socketio.on('check_user_status')
    # def handle_check_user_status(data):
    #     """Check if a specific user is online"""
    #     user_id = data.get('user_id')
        
    #     is_online = user_id in user_sockets and len(user_sockets[user_id]) > 0
        
    #     # Get last_seen from database
    #     try:
    #         user_doc = mongo.db.users.find_one({'_id': ObjectId(user_id)})
    #         last_seen = user_doc.get('last_seen') if user_doc else None
            
    #         emit('user_status_response', {
    #             'user_id': user_id,
    #             'online': is_online,
    #             'last_seen': last_seen.strftime('%Y-%m-%d %H:%M:%S') if last_seen else None
    #         })
    #     except Exception as e:
    #         print(f"Error checking user status: {e}")

    @socketio.on('check_user_status')
    def handle_check_user_status(data):
        """Check if a specific user is online"""
        user_id = data.get('user_id')
        
        is_online = user_id in user_sockets and len(user_sockets[user_id]) > 0
        
        # Get last_seen from database
        try:
            user_doc = mongo.db.users.find_one({'_id': ObjectId(user_id)})
            last_seen = user_doc.get('last_seen') if user_doc else None
            
            # Return the last_seen as-is (it's already a string in ISO format)
            emit('user_status_response', {
                'user_id': user_id,
                'online': is_online,
                'last_seen': last_seen  # Already a string like "2025-12-06T10:00:00.123Z"
            })
        except Exception as e:
            print(f"Error checking user status: {e}")
    
    @socketio.on('get_online_users')
    def handle_get_online_users():
        """Get list of all currently online users"""
        online_user_ids = list(user_sockets.keys())
        online_users_data = []
        
        for uid in online_user_ids:
            try:
                user_doc = mongo.db.users.find_one({'_id': ObjectId(uid)})
                if user_doc:
                    online_users_data.append({
                        'user_id': uid,
                        'username': user_doc.get('name', 'Unknown'),
                        'email': user_doc.get('email', ''),
                        'status': 'online'
                    })
            except Exception as e:
                print(f"Error getting user {uid}: {e}")
        
        emit('online_users_list', {'users': online_users_data})
    
    # @socketio.on('join_chat')
    # def handle_join_chat(data):
    #     """Join a specific chat room"""
    #     user_id = data.get('user_id')
    #     receiver_id = data.get('receiver_id')
        
    #     # Create room ID (sorted to ensure same room for both users)
    #     room = '_'.join(sorted([user_id, receiver_id]))
        
    #     join_room(room)
        
    #     if request.sid in active_users:
    #         if 'rooms' not in active_users[request.sid]:
    #             active_users[request.sid]['rooms'] = []
    #         active_users[request.sid]['rooms'].append(room)
    #         active_users[request.sid]['current_room'] = room
        
    #     print(f"User {user_id} joined room {room}")
        
    #     # Send receiver's current status
    #     receiver_online = receiver_id in user_sockets and len(user_sockets[receiver_id]) > 0
        
    #     try:
    #         receiver_doc = mongo.db.users.find_one({'_id': ObjectId(receiver_id)})
            
    #         emit('joined_room', {
    #             'room': room,
    #             'receiver_online': receiver_online,
    #             'receiver_last_seen': receiver_doc.get('last_seen').strftime('%Y-%m-%d %H:%M:%S') if receiver_doc and receiver_doc.get('last_seen') else None
    #         })
    #     except Exception as e:
    #         print(f"Error getting receiver status: {e}")
    @socketio.on('join_chat')
    def handle_join_chat(data):
        """Join a specific chat room"""
        user_id = data.get('user_id')
        receiver_id = data.get('receiver_id')
        
        # Create room ID
        room = '_'.join(sorted([user_id, receiver_id]))
        join_room(room)
        
        if request.sid in active_users:
            if 'rooms' not in active_users[request.sid]:
                active_users[request.sid]['rooms'] = []
            active_users[request.sid]['rooms'].append(room)
            active_users[request.sid]['current_room'] = room
        
        print(f"User {user_id} joined room {room}")
        
        # Send receiver's current status
        receiver_online = receiver_id in user_sockets and len(user_sockets[receiver_id]) > 0
        
        try:
            receiver_doc = mongo.db.users.find_one({'_id': ObjectId(receiver_id)})
            last_seen_value = receiver_doc.get('last_seen') if receiver_doc else None
            
            emit('joined_room', {
                'room': room,
                'receiver_online': receiver_online,
                'receiver_last_seen': last_seen_value  # Already a string
            })
        except Exception as e:
            print(f"Error getting receiver status: {e}")
    
    @socketio.on('leave_chat')
    def handle_leave_chat(data):
        """Leave a specific chat room"""
        user_id = data.get('user_id')
        receiver_id = data.get('receiver_id')
        
        room = '_'.join(sorted([user_id, receiver_id]))
        leave_room(room)
        
        if request.sid in active_users:
            if 'rooms' in active_users[request.sid] and room in active_users[request.sid]['rooms']:
                active_users[request.sid]['rooms'].remove(room)
            if 'current_room' in active_users[request.sid]:
                del active_users[request.sid]['current_room']
        
        print(f"User {user_id} left room {room}")
    
    @socketio.on('send_message')
    def handle_send_message(data):
        """Handle real-time message sending"""
        sender_id = data.get('sender_id')
        receiver_id = data.get('receiver_id')
        message_text = data.get('message')
        
        if not sender_id or not receiver_id or not message_text:
            emit('error', {'message': 'Invalid message data'})
            return
        
        try:
            # Save message to database
            message_data = {
                'sender_id': ObjectId(sender_id),
                'receiver_id': ObjectId(receiver_id),
                'message': message_text.strip(),
                'timestamp': datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                'is_read': False
            }
            
            result = mongo.db.messages.insert_one(message_data)
            message_id = str(result.inserted_id)
            
            # Update or create conversation
            from app.routes.chat import conversations_create
            conversation_id = conversations_create(mongo.db, sender_id, receiver_id, message_id)
            
            # Get sender info
            sender = mongo.db.users.find_one({'_id': ObjectId(sender_id)})
            
            # Create room ID
            room = '_'.join(sorted([sender_id, receiver_id]))
            
            # Prepare message response
            message_response = {
                'message_id': message_id,
                'sender_id': sender_id,
                'receiver_id': receiver_id,
                'sender_name': sender.get('name', 'Unknown'),
                'message': message_text.strip(),
                'timestamp': datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                'is_read': False
            }
            
            # Emit to room (both sender and receiver if in room)
            emit('receive_message', message_response, room=room)
            
            print(f"Message sent from {sender_id} to {receiver_id}")
            
        except Exception as e:
            print(f"Error sending message: {e}")
            emit('error', {'message': 'Failed to send message'})
    
    @socketio.on('typing')
    def handle_typing(data):
        """Handle typing indicator"""
        sender_id = data.get('sender_id')
        receiver_id = data.get('receiver_id')
        
        room = '_'.join(sorted([sender_id, receiver_id]))
        
        emit('user_typing', {
            'user_id': sender_id
        }, room=room, include_self=False)
    
    @socketio.on('stop_typing')
    def handle_stop_typing(data):
        """Handle stop typing indicator"""
        sender_id = data.get('sender_id')
        receiver_id = data.get('receiver_id')
        
        room = '_'.join(sorted([sender_id, receiver_id]))
        
        emit('user_stop_typing', {
            'user_id': sender_id
        }, room=room, include_self=False)
    
    @socketio.on('mark_as_read')
    def handle_mark_as_read(data):
        """Mark messages as read"""
        sender_id = data.get('sender_id')
        receiver_id = data.get('receiver_id')
        
        try:
            # Mark all messages from sender to receiver as read
            mongo.db.messages.update_many(
                {
                    'sender_id': ObjectId(sender_id),
                    'receiver_id': ObjectId(receiver_id),
                    'is_read': False
                },
                {
                    '$set': {'is_read': True}
                }
            )
            
            # Notify sender that messages were read
            room = '_'.join(sorted([sender_id, receiver_id]))
            emit('messages_read', {
                'reader_id': receiver_id
            }, room=room)
            
        except Exception as e:
            print(f"Error marking messages as read: {e}")

