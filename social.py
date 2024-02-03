from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
import argparse

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Dummy database for users and posts
users = {'user1': 'password1', 'user2': 'password2'}
posts = []

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('home'))
    return render_template('index.html')

@app.route('/home')
def home():
    if 'username' not in session:
        return redirect(url_for('index'))
    return render_template('home.html', username=session['username'], posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:
            session['username'] = username
            return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username not in users:
            users[username] = password
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/post', methods=['POST'])
def post():
    if 'username' not in session:
        return redirect(url_for('login'))
    content = request.form['content']
    username = session['username']
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    posts.append({'username': username, 'content': content, 'timestamp': timestamp})
    return redirect(url_for('home'))

if __name__ == '__main__':
    defaultHost = '127.0.0.1'
    defaultPort = 5000
    parser = argparse.ArgumentParser(
                    prog='hello.py',
                    description='Test server for Flask.  Returns "hello world" response',
                    epilog='T')
    parser.add_argument('-o', '--host', default=defaultHost) 
    parser.add_argument('-p', '--port', default=defaultPort) 
    args = parser.parse_args()
    app.run(host=args.host, port=args.port)