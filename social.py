from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime, timedelta
import argparse
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Dummy database for users and posts
users = {'user1': 'password1', 'user2': 'password2'}
posts = { 'user1' : [], 'user2' : []}
friends = { 'user1' : ['user2'], 'user2' : ['user2']}

loremIpsum = '''Lorem ipsum dolor sit amet, consectetur adipiscing elit, 
sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. '''

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('home'))
    return render_template('index.html')

@app.route('/home')
def home():
    if 'username' not in session:
        return redirect(url_for('index'))
    uname=session['username']
    friendPosts = []
    for f in friends[uname]:
        friendPosts = friendPosts + posts[f]
    return render_template('home.html', username=uname, posts=friendPosts)

@app.route('/getfeed/<uname>')
def getfeed(uname):
    maxPosts = 10
    feed = []
    
    for f in friends[uname]:
        for p in posts[f]:
            t = p['timestamp']
            if len(feed) >= maxPosts:
                if(feed[-1]['timestamp'] > t):
                    continue
                        
            feed_p = {'user': f, 'content': p['content'], 'timestamp': t}
            feed.append(feed_p)
            feed.sort(key=lambda x: x['timestamp'])
            
    friendPosts = {'posts' : feed}
    return json.dumps(friendPosts)

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
            posts[username] = []
            friends[username] = []
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/post', methods=['POST'])
def post():
    if 'username' not in session:
        return redirect(url_for('login'))
    content = request.form['content']
    username = session['username']
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    posts[username].append({'content': content, 'timestamp': timestamp})
    return redirect(url_for('home'))

def addTestData(numUsers=1000, postsPerUser=100, friendsPerUser=10):
    t1 = datetime.now()
    
    for u in range(3, numUsers):
        uname = 'user' + str(u)
        if u%100 == 0:
            print(uname)
        users[uname] = 'password'
        friends[uname] = []
        posts[uname] = []
        # add friends
        for f in range(1, friendsPerUser):
            fnum = ((u + f) % numUsers) + 1
            fname = 'user' + str(fnum)
            friends[uname].append(fname)
        # add posts
        for p in range(postsPerUser):
            pnum = postsPerUser*u + p
            dt = timedelta(hours=p)
            posttxt = 'post' + str(pnum) + ' ' + loremIpsum
            tstamp = (t1-dt).strftime("%Y-%m-%d %H:%M:%S")
            posts[uname].append({'content': posttxt, 'timestamp': tstamp})

if __name__ == '__main__':
    defaultHost = '127.0.0.1'
    defaultPort = 5000
    parser = argparse.ArgumentParser(
                    prog='hello.py',
                    description='Test server for Flask.  Returns "hello world" response',
                    epilog='T')
    parser.add_argument('-o', '--host', default=defaultHost) 
    parser.add_argument('-p', '--port', default=defaultPort) 
    parser.add_argument('-t', '--testdata', default=defaultPort, action='store_true') 
    args = parser.parse_args()
    if args.testdata:
        addTestData()
    app.run(host=args.host, port=args.port)