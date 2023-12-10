from flask import Flask, request

app = Flask(__name__)
LOAD_BALANCER_IP = '10.0.0.4'

@app.route('/')
def hello():
    sender = request.remote_addr
    if sender != LOAD_BALANCER_IP:
        print(f'unrecognized sender: {sender}')
        return 'Not Found', 404
    

    return 'Hello, this is Server2!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)