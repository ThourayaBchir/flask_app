from flask import render_template, flash, redirect, url_for, session, request
from app import app
from app.forms import LoginForm, RegistrationForm
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug import secure_filename
import os
from sympy import isprime
from flask import request, redirect
import requests
from .users import User


@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html', title='Home')


@app.route('/login',  methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.get_user(None, username, password)
        if user is None:
            return redirect(url_for('login'))

        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))

    return render_template('login.html', form=form, title='Sign In')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        r = User.insert_new_user(None, form.username.data, form.email.data, form.password.data)
        print(r)
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/profile/')
def redirect_to_home():
    return redirect(url_for('index'))


@app.route('/profile/<username>', methods=['GET', 'POST'])
@login_required
def user(username):
    if current_user.is_authenticated and current_user.username == username:
        user = User.get_by_username(None, username)

        #Display prime numbers
        number = 20
        if request.method == 'POST':
            number = int(request.form['limit'])
        primes_list = get_primes(number)
        primes_distance_list = get_primes_distance(primes_list)

        #Display ip data
        if 'X-Forwarded-For' in request.headers.keys() and '.' in request.headers['X-Forwarded-For']:
            user_ip = request.headers['X-Forwarded-For']
        else:
            user_ip = request.remote_addr
        ip_data = get_ip_infos(user_ip)

        # Display uploaded files
        files_list = user.get_uploaded_files(username)
        return render_template('user.html', user=user, primes_list=primes_list,
                               primes_distance_list=primes_distance_list, ip_data=ip_data, files_list=files_list)
    else:
        return redirect(url_for('login'))


@app.route('/profile/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files['user_file']
        if file:
            filename = secure_filename(file.filename)
            dirname, _ = os.path.split(os.path.abspath(__file__))
            save_path = dirname + app.config['UPLOAD_FOLDER']
            file.save(os.path.join(save_path, filename))

            # put filename in db
            user = User.get_by_username(None, current_user.username)
            user.log_filename(current_user.username, filename)

    return redirect(url_for('user', username=current_user.username))


def get_primes(n):
    primes_list = []
    for i in range(n):
        if isprime(i):
            primes_list.append(i)
    return primes_list


def get_primes_distance(primes_list):
    primes_distance_list = []
    for i in range(len(primes_list)):
        if i == 0:
            d = primes_list[i+1] - primes_list[i]/primes_list[i]
        elif i == len(primes_list)-1:
            d = primes_list[i] - primes_list[i-1]/primes_list[i]
        else:
            d = primes_list[i + 1] - primes_list[i-1]/primes_list[i]
        primes_distance_list.append(d)
    return primes_distance_list


def get_ip_infos(user_ip):
    api_token = app.config['API_TOKEN']
    base_url = 'http://api.ipstack.com/'
    api_url = base_url + user_ip + '?access_key=' + api_token
    r = requests.get(api_url)

    if r.status_code == 200:
        return r.json()
    else:
        return None
