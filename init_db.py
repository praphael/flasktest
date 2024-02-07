import argparse
from datetime import datetime, timedelta, timezone
import psycopg

if __name__ != "__main__":
    print("init_db.py must be run from the command line")
    raise Exception()

loremIpsum = '''Lorem ipsum dolor sit amet, consectetur adipiscing elit, 
sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. '''

parser = argparse.ArgumentParser(
                    prog='init_db.py',
                    description='Initialize PostgreSQL db for social.py',
                    epilog='')

parser.add_argument('-n', '--numUsers', default=1000) 
parser.add_argument('-p', '--postsPerUser', default=100) 
parser.add_argument('-s', '--subsPerUser', default=10, action='store_true') 
args = parser.parse_args()
numUsers = args.numUsers
postsPerUser = args.postsPerUser
subsPerUser = args.subsPerUser

t1 = datetime.now(timezone.utc)

# Connect to an existing database
with psycopg.connect("host=127.0.0.1 port=5432 dbname=social user=ec2-user") as conn:
    # Open a cursor to perform database operations
    with conn.cursor() as cur:
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
                post_time timestamptz,
                PRIMARY KEY(author, post_time)
               )
            """)

        cur.execute("set time zone UTC")
        for u in range(1, numUsers):
            uname = 'user' + str(u)
            if u%100 == 0:
                print(uname)
            
            # add subscriptions
            for s in range(1, subsPerUser):
                snum = ((u + s) % numUsers) + 1
                sname = 'user' + str(snum)
                cur.execute(
                    "INSERT INTO subs (username, sub_to) VALUES (%s, %s)",
                    (uname, sname))
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
                cur.execute(
                    "INSERT INTO posts (author, content, post_time) VALUES (%s, %s, TO_TIMESTAMP(%s, 'YYYY-MM-DD HH24:MI:SS.MS')::timestamp WITH TIME ZONE AT TIME ZONE 'UTC')",
                    (uname, posttxt, tstamp))
        # Make the changes to the database persistent
        conn.commit()             

        # Query the database and obtain data as Python objects.
        #cur.execute("SELECT * FROM test")
        #cur.fetchone()
        # will return (1, 100, "abc'def")

        # You can use `cur.fetchmany()`, `cur.fetchall()` to return a list
        # of several records, or even iterate on the cursor
        #for record in cur:
         #   print(record)

        

# drop table posts;
# create table posts(author varchar(32), content text, post_time timestamptz);
# insert into posts values('foo', 'bar', clock_timestamp ( ));