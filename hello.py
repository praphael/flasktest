from flask import Flask
import argparse

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!  I am Flask</p>"

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