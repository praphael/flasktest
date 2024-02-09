import argparse
from datetime import datetime, timedelta, timezone
import socialdb

if __name__ != "__main__":
    print("init_db.py must be run from the command line")
    raise Exception()

loremIpsum = '''Lorem ipsum dolor sit amet, consectetur adipiscing elit, 
sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. '''

parser = argparse.ArgumentParser(
                    prog='init_db.py',
                    description='Initialize database for social.py.  Supported databases include Postgres and sqlite3.',
                    epilog='')

parser.add_argument('-n', '--numUsers', type=int, default=1000) 
parser.add_argument('-p', '--postsPerUser', type=int, default=100) 
parser.add_argument('-s', '--subsPerUser', type=int, default=10) 
parser.add_argument('-d', '--database', default='sqlite') 
args = parser.parse_args()
numUsers = args.numUsers
postsPerUser = args.postsPerUser
subsPerUser = args.subsPerUser

t1 = datetime.now(timezone.utc)

db = socialdb.supportedDBs[args.database]
conn = socialdb.getConnection(db)

# Open a cursor to perform database operations
cur = conn.cursor()

# drop tables
try:
    cur.execute("DROP TABLE posts")
except:
    pass
try:    
    cur.execute("DROP TABLE subs")
except:
    pass    
conn.commit()

cur.execute("""
    CREATE TABLE subs (
        username varchar(32),
        sub_to varchar(32)
        )
    """)

cur.execute("""
    CREATE TABLE posts (
        author varchar(32),
        content text,
        post_time_utc timestamptz,
        PRIMARY KEY(author, post_time_utc)
        )
    """)

# cur.execute("set time zone UTC")
for u in range(1, numUsers):
    uname = 'user' + str(u)
    if u%100 == 0:
        print(uname)
    
    # add subscriptions
    for s in range(1, subsPerUser):
        snum = ((u + s) % numUsers) + 1
        sname = 'user' + str(snum)
        cur.execute(f"INSERT INTO subs (username, sub_to) VALUES ('{uname}', '{sname}')")
    # add posts
    for p in range(postsPerUser):
        pnum = postsPerUser*u + p
        dt = timedelta(hours=p)
        posttxt = 'post' + str(pnum) + ' ' + loremIpsum
        t2 = t1-dt
        tstamp = t2.strftime("%Y-%m-%d %H:%M:%S")
        tstamp = tstamp + "." + str(t2.microsecond // 1000).zfill(3)
        
        # Pass data to fill a query placeholders and let Psycopg perform
        # the correct conversion (no SQL injections!)
        qy = f"INSERT INTO posts (author, content, post_time_utc) VALUES ('{uname}', '{posttxt}',"
        if db == socialdb.DB.sqlite:
            qy += f" strftime('{tstamp}', '%F %R-%f'))"
        elif db == socialdb.DB.postgres:
            qy += f" TO_TIMESTAMP('{tstamp}', 'YYYY-MM-DD HH24:MI:SS.MS')::timestamp)"

        cur.execute(qy)
# Make the changes to the database persistent
conn.commit()