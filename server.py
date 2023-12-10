from flask import Flask, request
import yaml
import sys
import socket

app = Flask(__name__)
LOAD_BALANCER_IP = '10.0.0.4'
SELF_IP = socket.gethostbyname_ex(socket.gethostname())[2][0]
print(SELF_IP)

def handleService(name):
    return f'Hi, this is server1, thank you for using {name}'

# load config yaml file
def load_config(path):
    with open(path) as file:
        config = yaml.load(file, Loader=yaml.FullLoader)

    return config

# determine which services are to be handled by the server based on
# config file
def add_services(config):
    for host_elem in config['hosts']:
        ips = [server['ip'] for server in host_elem['servers']]
        if SELF_IP in ips:
            services.append(host_elem['host'])



config = load_config('config.yaml')
services = []


@app.route('/<service>')
def router(service):

    # ensure that the client for this server is the load balancer
    sender = request.remote_addr
    if sender != LOAD_BALANCER_IP:
        print(f'unrecognized sender: {sender}')
        return 'Not Found', 404
    
    # iterate through valid services handled by this server 
    for s in services:
        if service == s:
            return handleService(service)
    
    return 'Hello, this is Server1!'

if __name__ == '__main__':
    assert len(sys.argv) == 3, "Incorrect usage, python server.py [SERVERNAME] [CONFIGPATH]"

    name = sys.argv[1]
    conf_path = sys.argv[2]

    config = load_config(conf_path)
    add_services(config)

    app.run(host='0.0.0.0', port=5000)