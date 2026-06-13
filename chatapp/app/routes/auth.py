from flask import Blueprint, render_template, request, redirect, url_for, session
from ..models import db, User

auth_bp = Blueprint('auth', __name__)


# signup page
@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')

        # check username age thekei ache ki na
        existing_user = User.query.filter_by(username=username).first()
        if existing_user is not None:
            return render_template('signup.html', error="Username already taken")

        new_user = User(name=name, username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        # signup hole ekhane auto login kore dichi
        session['username'] = username
        session['name'] = name

        return redirect(url_for('chat.home'))

    return render_template('signup.html')


# login page
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username, password=password).first()

        if user is None:
            return render_template('login.html', error="Invalid username or password")

        session['username'] = user.username
        session['name'] = user.name

        return redirect(url_for('chat.home'))

    return render_template('login.html')


# logout
@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
