from flask_socketio import emit, join_room, leave_room
from .. import socketio, db
from ..models import Message

# live room er active user track korar jonno ekta dictionary
# format: { "room_id" : ["user1", "user2", ...] }
live_room_users = {}


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

    # ei room er sobai ke message pathano hocche
    emit('receive_message', data, to=room)


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


# user disconnect hole (browser/tab close)
@socketio.on('disconnect')
def handle_disconnect():
    print("A user disconnected")
