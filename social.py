from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime, timedelta, timezone
import argparse
import json
import psycopg
import socialdb

app = Flask(__name__)
app.secret_key = 'your_secret_key'
db = socialdb.DB.sqlite

@app.route('/getfeed/<uname>')
def getfeed(uname):
    conn = socialdb.getConnection(db)

    maxPosts = 10
    # Open a cursor to perform database operations
    cur = conn.cursor()
    if db == socialdb.DB.sqlite:
        qy = "SELECT author, content, post_time_utc FROM posts WHERE author IN " + \
            f" (SELECT sub_to FROM subs WHERE username='{uname}')" + \
            f" ORDER BY post_time_utc DESC LIMIT {maxPosts} "
        cur.execute(qy)
    elif db == socialdb.DB.postgres:
        qy = "SELECT author, content, post_time_utc::varchar FROM posts WHERE author IN " + \
            " (SELECT sub_to FROM subs WHERE username=%s)" + \
            " ORDER BY post_time_utc DESC LIMIT %s "
        cur.execute(qy, (uname, maxPosts))
    
    feed = cur.fetchall()
    subsPosts = {'posts' : feed}
    return json.dumps(subsPosts)

@app.route('/postmessage/<uname>', methods=['POST'])
def postmessage(uname):
    content = request.form['content']
    t1 = datetime.now(timezone.utc)
    tstamp = t1.strftime("%Y-%m-%d %H:%M:%S")
    tstamp = tstamp + "." + str(t1.microsecond // 1000).zfill(3)

    conn = socialdb.getConnection(db)
    # Open a cursor to perform database operations
    cur = conn.cursor()
    if db == socialdb.DB.sqlite:
        qy = f"INSERT INTO posts (author, content, post_time_utc) VALUES ('{uname}', '{posttxt}',"
        qy += f" strftime('{tstamp}', '%F %R-%f'))"
        cur.execute(qy)
    elif db == socialdb.DB.postgres:
        cur.execute(
                "INSERT INTO posts (author, content, post_time) VALUES (%s, %s, TO_TIMESTAMP(%s, 'YYYY-MM-DD HH24:MI:SS.MS')::timestamp WITH TIME ZONE AT TIME ZONE 'UTC')",
                (uname, content, tstamp))
    return redirect(url_for('getfeed', uname=uname))

if __name__ == '__main__':
    defaultHost = '127.0.0.1'
    defaultPort = 5000
    parser = argparse.ArgumentParser(
                    prog='hello.py',
                    description='Test server for Flask.  Returns "hello world" response',
                    epilog='T')
    parser.add_argument('-o', '--host', default=defaultHost) 
    parser.add_argument('-p', '--port', default=defaultPort) 
    parser.add_argument('-b', '--debug', default=False, action='store_true') 
    parser.add_argument('-d', '--database', default='sqlite') 
    args = parser.parse_args()
    db = socialdb.supportedDBs[args.database]

    app.run(host=args.host, port=args.port, debug=args.debug)