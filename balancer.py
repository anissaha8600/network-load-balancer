
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

def setupWRR(config):

    # iterate each host to determine modulo number
    for i, elem in enumerate(config):
        n = 0
        for server in elem:
            n += server['weight']
        config[i]['n'] = n
        config[i]['curr'] = 0
    
    print(config)
    return


def chooseWRR(host_elem):
    """Based on host element, choose which server to send to based on 
    Weighted Round Robin """

    val = host_elem['curr']
    assert val >= 0 and host_elem['n']

    # iterate through each server to determine which one to request 
    # to based on RR value 
    acc = 0
    for server in host_elem:
        if val < acc + server['weight']:

            # update RR iterator to next value upon request
            host_elem["curr"] = (val + 1) % host_elem['n']
            return server['port']
        
        acc += server['weight']


# load and config from yaml file 
# and setup parameters for runtime
config = load_config('config.yaml')
setupWRR(config)


@loadbalancer.route('/<path>')
def router(path):
    """Handle request to servers routed to /<path> using WRR
    Load Balancing """

    for elem in config['hosts']:
        if path == elem['host']:

            # choose server based on WRR
            response = requests.get(f'http://{chooseWRR(elem)}')
            return response.content, response.status_code
           
        
    return 'Not Found', 404
