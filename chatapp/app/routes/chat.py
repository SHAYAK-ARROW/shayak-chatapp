from flask import Blueprint, render_template, request, redirect, url_for, session
from ..models import db, Message, Group, GroupMember

chat_bp = Blueprint('chat', __name__)


# login check korar jonno ekta function
def get_current_user():
    username = session.get('username')
    return username


# home page - 4 part dekhabe
@chat_bp.route('/')
def home():
    username = get_current_user()
    if username is None:
        return redirect(url_for('auth.login'))

    name = session.get('name')
    return render_template('home.html', username=username, name=name)


# 1. open chat - sobar jonno
@chat_bp.route('/open-chat')
def open_field():
    username = get_current_user()
    if username is None:
        return redirect(url_for('auth.login'))

    all_messages = Message.query.filter_by(receiver='General').all()
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
    return render_template('personal_chat.html', messages=all_messages, username=username,
                            other_username=other_username, room=room_name)


# 3. group list + create
@chat_bp.route('/groups', methods=['GET', 'POST'])
def groups():
    username = get_current_user()
    if username is None:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        group_name = request.form.get('group_name')

        new_group = Group(name=group_name, creator=username)
        db.session.add(new_group)
        db.session.commit()

        # creator ke group er member kore dilam
        member = GroupMember(group_id=new_group.id, username=username)
        db.session.add(member)
        db.session.commit()

        return redirect(url_for('chat.groups'))

    # joto group ache shob dekhano
    all_groups = Group.query.all()
    return render_template('groups.html', groups=all_groups, username=username)


# group e join kora
@chat_bp.route('/group/join/<int:group_id>')
def join_group(group_id):
    username = get_current_user()
    if username is None:
        return redirect(url_for('auth.login'))

    existing_member = GroupMember.query.filter_by(group_id=group_id, username=username).first()
    if existing_member is None:
        member = GroupMember(group_id=group_id, username=username)
        db.session.add(member)
        db.session.commit()

    return redirect(url_for('chat.group_chat', group_id=group_id))


# group chat page
@chat_bp.route('/group/<int:group_id>')
def group_chat(group_id):
    username = get_current_user()
    if username is None:
        return redirect(url_for('auth.login'))

    group = Group.query.get(group_id)
    if group is None:
        return redirect(url_for('chat.groups'))

    room_name = "group_" + str(group_id)
    all_messages = Message.query.filter_by(receiver=room_name).all()

    return render_template('group.html', messages=all_messages, username=username,
                            group=group, room=room_name)


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
