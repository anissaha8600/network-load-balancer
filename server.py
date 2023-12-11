from flask import Flask, request
import yaml
import sys
import socket

app = Flask(__name__)
LOAD_BALANCER_IP = '10.0.0.4'


# for server to know who it is in the config
def get_local_ip():
    try:
        # Create a socket to get local IP address
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(('8.8.8.8', 80))  # Connect to a known external server
        local_ip = sock.getsockname()[0]
        return local_ip
    except socket.error:
        return 'Unknown'

SELF_IP = get_local_ip()
print(SELF_IP)

# dummy code for handling a service
def handleService(name, service):
    return f'Hi, this is {name}, thank you for using {service}'

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
        print(ips)
        if SELF_IP.strip() in ips.strip():
            services.append(host_elem['host'])


config = load_config('config.yaml')             # specification for load balancing
services = []                                   # list of services this server is responsible for


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
            return handleService(name, service)
    
    print(f"I don't handle {service}....")
    return 'Not Found', 404
    

if __name__ == '__main__':
    assert len(sys.argv) == 3, "Incorrect usage, python server.py [SERVERNAME] [CONFIGPATH]"

    name = sys.argv[1]
    conf_path = sys.argv[2]

    print(f"Hi, I'm {name}, I handle {services}, awaiting load_balancer {LOAD_BALANCER_IP}")

    config = load_config(conf_path)
    add_services(config)

    app.run(host='0.0.0.0', port=5000)