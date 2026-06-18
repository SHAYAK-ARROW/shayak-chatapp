from flask import request
from flask_socketio import emit, join_room, leave_room
from .. import socketio, db
from ..models import Message


# time ke "10:30 PM" format e dekhanor jonno
def format_time(time_value):
    return time_value.strftime("%I:%M %p")


# live room er active user track korar jonno ekta dictionary
# format: { "room_id" : ["user1", "user2", ...] }
live_room_users = {}

# kon socket connection kon username er - ekta dictionary
# format: { "socket_id" : "username" }
online_users_by_sid = {}

# kon username koyta tab/device theke connected - ekta dictionary
# format: { "username" : count }
online_user_counts = {}


# normal chat (open / personal / group) er jonno
@socketio.on('send_message')
def handle_message(data):
    message = data.get('message')
    sender = data.get('sender')
    room = data.get('receiver')

    # database e save kora hocche
    new_message = Message(sender=sender, receiver=room, content=message)
    db.session.add(new_message)
    db.session.commit()

    # message id ar time o pathano hocche jate real time e dekhano jay
    data['id'] = new_message.id
    data['time_str'] = format_time(new_message.timestamp)

    # ei room er sobai ke message pathano hocche
    emit('receive_message', data, to=room)


# nijer pathano message edit kora
@socketio.on('edit_message')
def handle_edit_message(data):
    message_id = data.get('message_id')
    room = data.get('room')
    username = data.get('username')
    new_content = data.get('new_content')

    msg = Message.query.get(message_id)

    if msg is not None:
        if msg.sender == username:
            msg.content = new_content
            db.session.commit()
            emit('message_edited', {'message_id': message_id, 'new_content': new_content}, to=room)


# nijer pathano message delete kora
@socketio.on('delete_message')
def handle_delete_message(data):
    message_id = data.get('message_id')
    room = data.get('room')
    username = data.get('username')

    msg = Message.query.get(message_id)

    if msg is not None:
        if msg.sender == username:
            db.session.delete(msg)
            db.session.commit()
            emit('message_deleted', {'message_id': message_id}, to=room)


# user typing korle
@socketio.on('typing')
def handle_typing(data):
    room = data.get('room')
    username = data.get('username')

    emit('user_typing', {'username': username}, to=room, include_self=False)


# user typing thamle
@socketio.on('stop_typing')
def handle_stop_typing(data):
    room = data.get('room')
    username = data.get('username')

    emit('user_stop_typing', {'username': username}, to=room, include_self=False)


# user kono room e join korle
@socketio.on('join')
def handle_join(data):
    room = data.get('room')
    username = data.get('username')

    join_room(room)
    print(username + " joined room " + room)


# user room theke chole gele
@socketio.on('leave')
def handle_leave(data):
    room = data.get('room')
    username = data.get('username')

    leave_room(room)
    print(username + " left room " + room)


# ============ LIVE ROOM (Meet/WhatsApp video call type) ============

# user live room e join korle
@socketio.on('live_join')
def handle_live_join(data):
    room_id = data.get('room_id')
    username = data.get('username')

    join_room(room_id)

    # room jodi age na thake list te toiri kora hocche
    if room_id not in live_room_users:
        live_room_users[room_id] = []

    # user ke list e add kora hocche jodi already na thake
    if username not in live_room_users[room_id]:
        live_room_users[room_id].append(username)

    # sobai ke notun user list pathano hocche
    emit('live_user_list', {'users': live_room_users[room_id]}, to=room_id)

    # sobai ke janano hocche notun user ashche
    emit('live_user_joined', {'username': username}, to=room_id)


# live room theke message
@socketio.on('live_message')
def handle_live_message(data):
    room_id = data.get('room_id')
    emit('live_message', data, to=room_id)


# user live room theke chole gele
@socketio.on('live_leave')
def handle_live_leave(data):
    room_id = data.get('room_id')
    username = data.get('username')

    leave_room(room_id)

    if room_id in live_room_users:
        if username in live_room_users[room_id]:
            live_room_users[room_id].remove(username)

        # sobai ke notun user list pathano hocche
        emit('live_user_list', {'users': live_room_users[room_id]}, to=room_id)
        emit('live_user_left', {'username': username}, to=room_id)

        # room e keu na thakle room delete kore deya hocche
        if len(live_room_users[room_id]) == 0:
            del live_room_users[room_id]
            print("Room " + room_id + " is now empty and deleted")


# ============ ONLINE STATUS ============

# user app e dhukle (sidebar load hole) eta call hoy
@socketio.on('user_connected')
def handle_user_connected(data):
    username = data.get('username')
    sid = request.sid

    online_users_by_sid[sid] = username

    if username in online_user_counts:
        online_user_counts[username] = online_user_counts[username] + 1
    else:
        online_user_counts[username] = 1

    online_list = list(online_user_counts.keys())
    emit('online_users_update', {'online_users': online_list}, broadcast=True)


# user disconnect hole (browser/tab close)
@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid

    if sid in online_users_by_sid:
        username = online_users_by_sid[sid]
        del online_users_by_sid[sid]

        if username in online_user_counts:
            online_user_counts[username] = online_user_counts[username] - 1

            if online_user_counts[username] <= 0:
                del online_user_counts[username]

        online_list = list(online_user_counts.keys())
        emit('online_users_update', {'online_users': online_list}, broadcast=True)

    print("A user disconnected")
