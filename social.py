from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime, timedelta, timezone
import argparse
import json
import psycopg

app = Flask(__name__)
app.secret_key = 'your_secret_key'

conninfo = "host=127.0.0.1 port=5432 dbname=social user=ec2-user"
# Dummy database for users and posts
#users = {'user1': 'password1', 'user2': 'password2'}
#posts = { 'user1' : [], 'user2' : []}
#friends = { 'user1' : ['user2'], 'user2' : ['user2']}

@app.route('/getfeed/<uname>')
def getfeed(uname):
    maxPosts = 10
    with psycopg.connect(conninfo) as conn:
        # Open a cursor to perform database operations
        with conn.cursor() as cur:
            qy = "SELECT author, content, post_time::varchar FROM posts WHERE author IN " + \
                 " (SELECT sub_to FROM subs WHERE username=%s)" + \
                 " ORDER BY post_time DESC LIMIT %s "
            cur.execute(qy, (uname, maxPosts))
            feed = cur.fetchall()
            subsPosts = {'posts' : feed}
            return json.dumps(subsPosts)

    return json.dumps("{'error' : 'Unknown error connecting to database'}")

@app.route('/postmessage/<uname>', methods=['POST'])
def postmessage(uname):
    content = request.form['content']
    t1 = datetime.now(timezone.utc)
    tstamp = t1.strftime("%Y-%m-%d %H:%M:%S")
    tstamp = tstamp + "." + str(t1.microsecond // 1000).zfill(3)

    with psycopg.connect(conninfo) as conn:
        # Open a cursor to perform database operations
        with conn.cursor() as cur:
            cur.execute(
                    "INSERT INTO posts (author, content, post_time) VALUES (%s, %s, TO_TIMESTAMP(%s, 'YYYY-MM-DD HH24:MI:SS.MS')::timestamp WITH TIME ZONE AT TIME ZONE 'UTC')",
                    (uname, content, tstamp))
            return redirect(url_for('getfeed', uname=uname))

    return json.dumps("{'error' : 'Unknown error connecting to database'}")
    #posts[uame].append({'content': content, 'timestamp': timestamp})
    

if __name__ == '__main__':
    defaultHost = '127.0.0.1'
    defaultPort = 5000
    parser = argparse.ArgumentParser(
                    prog='hello.py',
                    description='Test server for Flask.  Returns "hello world" response',
                    epilog='T')
    parser.add_argument('-o', '--host', default=defaultHost) 
    parser.add_argument('-p', '--port', default=defaultPort) 
    parser.add_argument('-d', '--debug', default=False, action='store_true') 
    args = parser.parse_args()
    app.run(host=args.host, port=args.port, debug=args.debug)