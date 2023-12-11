import sys
import requests
from flask import Flask, request

import os
import yaml

import random

loadbalancer = Flask(__name__)

def load_config(path):
    with open(path) as file:
        config = yaml.load(file, Loader=yaml.FullLoader)

    return config

config = load_config('config.yaml')

def setupWRR(config):

    # iterate each host to determine modulo number
    for i, host in enumerate(config['hosts']):
        n = 0
        for server in host['servers']:
            n += server['weight']
        config['hosts'][i]['n'] = n
        config['hosts'][i]['curr'] = 0

    return


def chooseWRR(host_elem):
    """Based on host element, choose which server to send to based on 
    Weighted Round Robin """

    val = host_elem['curr']
    assert val >= 0 and host_elem['n'] > val

    # iterate through each server to determine which one to request 
    # to based on RR value 
    acc = 0
    for server in host_elem['servers']:
        if val < acc + server['weight']:

            # update RR iterator to next value upon request
            host_elem["curr"] = (val + 1) % host_elem['n']
            return f"{server['ip']}:{server['port']}"
        
        acc += server['weight']


@loadbalancer.route('/<service>')
def router(service):
    """Handle request to servers routed to /<path> using WRR
    Load Balancing """

    for elem in config['hosts']:
        if service == elem['host']:

            # choose server based on WRR
            response = requests.get(f'http://{chooseWRR(elem)}/{service}')
            return response.content, response.status_code
           
        
    return 'Not Found', 404

if __name__ == '__main__':

    # load and config from yaml file 
    # and setup parameters for runtime
    if len(sys.argv) > 1:
        path = sys.argv[1] 
    else:
        path = 'config.yaml' # default path
    
    config = load_config(path)
    setupWRR(config)
    print(config)

    loadbalancer.run(host='0.0.0.0', port=5000)