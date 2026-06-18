import datetime
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from ..models import db, Message, Group, GroupMember, User, ReadStatus

chat_bp = Blueprint('chat', __name__)


# login check korar jonno ekta function
def get_current_user():
    username = session.get('username')
    return username


# room er last message ber kora
def get_last_message(room):
    last_msg = Message.query.filter_by(receiver=room).order_by(Message.id.desc()).first()
    return last_msg


# time ke "10:30 PM" format e dekhanor jonno
def format_time(time_value):
    if time_value is None:
        return ""

    return time_value.strftime("%I:%M %p")


# kono room e koyta notun (na dekha) message ache ta gona
def get_unread_count(username, room):
    read_status = ReadStatus.query.filter_by(username=username, room=room).first()

    if read_status is None:
        count = Message.query.filter_by(receiver=room).filter(Message.sender != username).count()
        return count

    count = Message.query.filter_by(receiver=room).filter(Message.sender != username).filter(Message.timestamp > read_status.last_read).count()
    return count


# room ke "read" mark kora - last_read time update kora hocche
def mark_room_read(username, room):
    read_status = ReadStatus.query.filter_by(username=username, room=room).first()

    if read_status is None:
        read_status = ReadStatus(username=username, room=room, last_read=datetime.datetime.utcnow())
        db.session.add(read_status)
    else:
        read_status.last_read = datetime.datetime.utcnow()

    db.session.commit()


# chat list sort korar jonno - shobcheye notun message wala chat upore thakbe
def get_chat_sort_key(chat_item):
    return chat_item['last_timestamp']


# user er joto group ache shei list ber kora (sidebar er jonno)
def get_my_groups(username):
    my_groups = []
    memberships = GroupMember.query.filter_by(username=username).all()

    for member in memberships:
        group = Group.query.get(member.group_id)

        if group is not None:
            room_name = "group_" + str(group.id)
            last_msg = get_last_message(room_name)

            group_info = {}
            group_info['id'] = group.id
            group_info['name'] = group.name
            group_info['unread'] = get_unread_count(username, room_name)
            group_info['room'] = room_name

            if last_msg is not None:
                group_info['last_text'] = last_msg.content
                group_info['last_time'] = format_time(last_msg.timestamp)
                group_info['last_timestamp'] = last_msg.timestamp
            else:
                group_info['last_text'] = ""
                group_info['last_time'] = ""
                group_info['last_timestamp'] = datetime.datetime.min

            my_groups.append(group_info)

    my_groups.sort(key=get_chat_sort_key, reverse=True)

    return my_groups


# /groups page er jonno - user er group, member count, non-member list shoho
def get_group_details(username):
    details = []
    memberships = GroupMember.query.filter_by(username=username).all()

    for member in memberships:
        group = Group.query.get(member.group_id)

        if group is None:
            continue

        all_members = GroupMember.query.filter_by(group_id=group.id).all()
        member_usernames = []

        for m in all_members:
            member_usernames.append(m.username)

        non_members = []
        all_user_objects = User.query.all()

        for user in all_user_objects:
            if user.username not in member_usernames:
                non_members.append(user)

        info = {}
        info['id'] = group.id
        info['name'] = group.name
        info['creator'] = group.creator
        info['member_count'] = len(member_usernames)
        info['non_members'] = non_members

        details.append(info)

    return details


# user kar kar sathe personal chat korechi shei list ber kora
def get_personal_chats(username):
    other_users = []
    all_messages = Message.query.all()

    for msg in all_messages:
        room = msg.receiver

        if room == "General":
            continue

        if room.startswith("group_"):
            continue

        if "_" not in room:
            continue

        parts = room.split("_")

        if len(parts) != 2:
            continue

        other_user = None

        if parts[0] == username and parts[1] != username:
            other_user = parts[1]

        if parts[1] == username and parts[0] != username:
            other_user = parts[0]

        if other_user is not None:
            if other_user not in other_users:
                other_users.append(other_user)

    chat_list = []

    for other_user in other_users:
        names = [username, other_user]
        names.sort()
        room_name = names[0] + "_" + names[1]

        last_msg = get_last_message(room_name)

        chat_info = {}
        chat_info['username'] = other_user
        chat_info['unread'] = get_unread_count(username, room_name)
        chat_info['room'] = room_name

        if last_msg is not None:
            chat_info['last_text'] = last_msg.content
            chat_info['last_time'] = format_time(last_msg.timestamp)
            chat_info['last_timestamp'] = last_msg.timestamp
        else:
            chat_info['last_text'] = ""
            chat_info['last_time'] = ""
            chat_info['last_timestamp'] = datetime.datetime.min

        chat_list.append(chat_info)

    chat_list.sort(key=get_chat_sort_key, reverse=True)

    return chat_list


# home page - sidebar + chat area dekhabe
@chat_bp.route('/')
def home():
    username = get_current_user()
    if username is None:
        return redirect(url_for('auth.login'))

    name = session.get('name')
    my_groups = get_my_groups(username)
    personal_chats = get_personal_chats(username)

    # open chat (General) er last message ar unread count
    open_chat = {}
    last_msg = get_last_message("General")
    open_chat['unread'] = get_unread_count(username, "General")

    if last_msg is not None:
        open_chat['last_text'] = last_msg.content
        open_chat['last_time'] = format_time(last_msg.timestamp)
    else:
        open_chat['last_text'] = ""
        open_chat['last_time'] = ""

    # sidebar theke notification er jonno - user er shob room er naam ekta list e
    all_rooms = ["General"]

    for group in my_groups:
        all_rooms.append(group['room'])

    for chat in personal_chats:
        all_rooms.append(chat['room'])

    return render_template('home.html', username=username, name=name,
                            my_groups=my_groups, personal_chats=personal_chats,
                            open_chat=open_chat, all_rooms=all_rooms)


# kono room "read" hoye gele ei route call hobe (fetch theke)
@chat_bp.route('/mark-read/<path:room>', methods=['POST'])
def mark_read(room):
    username = get_current_user()
    if username is None:
        return jsonify({'status': 'error'}), 401

    mark_room_read(username, room)
    return jsonify({'status': 'ok'})


# 1. open chat - sobar jonno
@chat_bp.route('/open-chat')
def open_field():
    username = get_current_user()
    if username is None:
        return redirect(url_for('auth.login'))

    all_messages = Message.query.filter_by(receiver='General').all()

    for msg in all_messages:
        msg.time_str = format_time(msg.timestamp)

    return render_template('open_fild.html', messages=all_messages, username=username)


# 2. personal chat - 1 to 1
@chat_bp.route('/personal/<other_username>')
def personal_chat(other_username):
    username = get_current_user()
    if username is None:
        return redirect(url_for('auth.login'))

    # room name banano holo - duijon er username sort kore jor lagano
    names = [username, other_username]
    names.sort()
    room_name = names[0] + "_" + names[1]

    all_messages = Message.query.filter_by(receiver=room_name).all()

    for msg in all_messages:
        msg.time_str = format_time(msg.timestamp)

    return render_template('personal_chat.html', messages=all_messages, username=username,
                            other_username=other_username, room=room_name)


# 3. group list + create
@chat_bp.route('/groups', methods=['GET', 'POST'])
def groups():
    username = get_current_user()
    if username is None:
        return redirect(url_for('auth.login'))

    error = None

    if request.method == 'POST':
        group_name = request.form.get('group_name')
        selected_members = request.form.getlist('members')

        # ekই name e age theke group thakle notun group banano hobe na
        existing_group = Group.query.filter_by(name=group_name, creator=username).first()

        if existing_group is not None:
            error = "Tumi already ei naam e ekta group baniyecho"
        else:
            new_group = Group(name=group_name, creator=username)
            db.session.add(new_group)
            db.session.commit()

            # creator ke group er member kore dilam
            creator_member = GroupMember(group_id=new_group.id, username=username)
            db.session.add(creator_member)

            # selected member der add kora hocche
            for other_username in selected_members:
                if other_username != username:
                    new_member = GroupMember(group_id=new_group.id, username=other_username)
                    db.session.add(new_member)

            db.session.commit()

            return redirect(url_for('chat.groups'))

    # checkbox e dekhanor jonno shob user (nijeke chara)
    all_user_objects = User.query.all()
    other_users = []

    for user in all_user_objects:
        if user.username != username:
            other_users.append(user)

    my_groups = get_group_details(username)

    return render_template('groups.html', username=username, all_users=other_users,
                            my_groups=my_groups, error=error)


# group e notun member add kora
@chat_bp.route('/group/<int:group_id>/add-member', methods=['POST'])
def add_member(group_id):
    username = get_current_user()
    if username is None:
        return redirect(url_for('auth.login'))

    # je add korche shei o ei group er member kina check
    is_member = GroupMember.query.filter_by(group_id=group_id, username=username).first()
    if is_member is None:
        return redirect(url_for('chat.groups'))

    new_username = request.form.get('username')

    if new_username:
        existing = GroupMember.query.filter_by(group_id=group_id, username=new_username).first()
        if existing is None:
            new_member = GroupMember(group_id=group_id, username=new_username)
            db.session.add(new_member)
            db.session.commit()

    return redirect(url_for('chat.groups'))


# group delete kora (shudhu creator korte parbe)
@chat_bp.route('/group/<int:group_id>/delete')
def delete_group(group_id):
    username = get_current_user()
    if username is None:
        return redirect(url_for('auth.login'))

    group = Group.query.get(group_id)

    if group is None:
        return redirect(url_for('chat.groups'))

    if group.creator != username:
        return redirect(url_for('chat.groups'))

    room_name = "group_" + str(group_id)

    # ei group er shob message, member, read status delete kora hocche
    Message.query.filter_by(receiver=room_name).delete()
    GroupMember.query.filter_by(group_id=group_id).delete()
    ReadStatus.query.filter_by(room=room_name).delete()

    db.session.delete(group)
    db.session.commit()

    return redirect(url_for('chat.groups'))


# group chat page
@chat_bp.route('/group/<int:group_id>')
def group_chat(group_id):
    username = get_current_user()
    if username is None:
        return redirect(url_for('auth.login'))

    group = Group.query.get(group_id)
    if group is None:
        return redirect(url_for('chat.groups'))

    # shudhu member ra ei group e dhukte parbe
    is_member = GroupMember.query.filter_by(group_id=group_id, username=username).first()
    if is_member is None:
        return redirect(url_for('chat.groups'))

    room_name = "group_" + str(group_id)
    all_messages = Message.query.filter_by(receiver=room_name).all()

    for msg in all_messages:
        msg.time_str = format_time(msg.timestamp)

    return render_template('group.html', messages=all_messages, username=username,
                            group=group, room=room_name)


# 5. shob user er list - notun user khujte
@chat_bp.route('/users')
def all_users():
    username = get_current_user()
    if username is None:
        return redirect(url_for('auth.login'))

    all_user_objects = User.query.all()
    user_list = []

    for user in all_user_objects:
        if user.username != username:
            user_list.append(user)

    return render_template('users.html', users=user_list, username=username)


# 4. live room - meet er moto
@chat_bp.route('/live-room', methods=['GET', 'POST'])
def live_room_home():
    username = get_current_user()
    if username is None:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        room_id = request.form.get('room_id')
        return redirect(url_for('chat.live_room', room_id=room_id))

    return render_template('live_room_home.html', username=username)


@chat_bp.route('/live-room/<room_id>')
def live_room(room_id):
    username = get_current_user()
    if username is None:
        return redirect(url_for('auth.login'))

    return render_template('live_room.html', room_id=room_id, username=username)
