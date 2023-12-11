# Project Description and Goals
In this project, we created a Network Load Balancing System using the real-time network simulation software `gns3`. We created a topology that includes 2 clients, 3 servers, and 1 load balancer. Each server is responsible for hosting different services. We created the load balancer, the client and server services using Python and the Flask package. The load balanacer is a weighted round robin, with each service having a specific weight assigned to it in each server. That means, for a service, if server1 has weight 1 and server2 has weight 2, server2 should recieve twice as many requests. The load balancer can easily be configured for any number of servers or services using a `config.yaml` file. This could, in real life, account for different servers with different capabilities and different services to handle.
# Contribution of Each Team Member
## Renat Hossain
- Installing gns3 and the Debian, Cisco 7200 router appliances.
- Creating the gns3 topology with 2 clients, 3 servers, and 1 load balancer.
- Configuring the router: setting the ip addresses of the interfaces, configuring the NAT to get Internet access inside the Debian VMs.
- Configuring each Debian VM: setting the ip address, gateway and dns server, then installing the necessary python packages and cloning the code.
- Writing the documentation and recording the video.
- Tested the code in the VMs.
## Anis Saha
- Implemented load balancer, client and server Python code in flask.
- Set up yaml files for loadbalancer to map to gns3 topology.
- Implemented service dependant weighted round robin algorithm in python.
- Wrote tests to test round robin, error 404 cases, and server permssions.
- Recording the video.
- Tested the code in the VMs.
# How to Run and Test the Implementation
- Open the topology in gns3.
- Click on Start all nodes.
- Open the terminals of all the clients, the load balancer and all the servers.
- Login on all VMs with credentials: username: debian, password: debian.
- Go to project folder on all VMs: `cd network_load_balancer` (Clone the folder from github if does not exist).
- Start all of the following services (on their respective machines, in this order):
```bash
# Server1
python3 server.py server1 config2.yaml

# Server2
python3 server.py server2 config2.yaml

# Server3
python3 server.py server3 config2.yaml

# LoadBalancer
python3 balancer.py config2.yaml

# RenatClient
python3 client.py 20 service1 12
python3 client.py 20 service3 3

# AnisClient
python3 client.py 20 service2 6

# Command meanings
python3 server.py [SERVER_NAME] [CONFIG_PATH]
python3 balancer.py [CONFIG_PATH]
python3 client.py [REQUEST_RATE_PER_MIN] [SERVICE_NAME] [NUMBER_OF_REQUESTS]
```
- Observe the output on each of the machines, and on the servers to match the ratio specified in `config2.yaml`. Results are discussed in the `Discussion and Results` section.
# Implementation Details and Documentation
## Setup the gns3 Topology
- Install the Cisco 7200 router and the Debian appliances.
- Place 6 Debian appliances called RenatClient, AnisClient, LoadBalancer, Server1, Server2, Server3.
- Place 1 switch called Switch and 1 router called Router.
- Connect RenatClient, AnisClient, LoadBalancer, Server1, Server2, Server3 to Switch.
- Connect Router to Switch using port g0/0 on the Router.
- Place 1 NAT called NAT, and connect it to Router using port g1/0 on the Router.
## Configuration
- Configuration of Router (10.0.0.1 for g0/0) (dhcp for g1/0):
```bash
# set the ip addresses
Router> enable
Router# configure terminal
Router(config)# interface g1/0
Router(config-if)# ip address dhcp
Router(config-if)# no shutdown
Router(config-if)# exit
Router(config)# ip routing
Router(config)# interface g0/0
Router(config-if)# ip address 10.0.0.1 255.255.255.0
Router(config-if)# no shutdown
Router(config-if)# exit
Router(config)# ip routing
Router(config)# exit

# Test the Internet connection
Router# ping 8.8.8.8

# Getting Internet access to the VMs
Router# configure terminal
Router(config)# interface g1/0
Router(config-if)# ip nat outside
Router(config-if)# exit
Router(config)# interface g0/0
Router(config-if)# ip nat inside
Router(config-if)# exit
Router(config)# ip nat inside source list 1 interface g1/0 overload
Router(config)# access-list 1 permit any
Router(config)# ip domain-lookup
Router(config)# exit

# See the configuration, test and save
Router# sh ip interface brief
Router# ping google.com
Router# wr mem
```

- Configuration of RenatClient (gets 10.0.0.2):
```bash
sudo nano /etc/network/interfaces

# Uncomment or add these lines, save and exit
auto ens4
iface ens4 inet static
    address 10.0.0.2 # <- assign ip
    netmask 255.255.255.0
    gateway 10.0.0.1 # <- router ip
		dns-nameservers 8.8.8.8 # <- Google DNS

# Continue in terminal
sudo service networking restart

# test ping
ping 10.0.0.2
ping 8.8.8.8
ping google.com

# Install needed packages
sudo apt update
sudo apt install pip
sudo apt install python3-flask
sudo apt install python3-pytest

# Clone and change folder
git clone https://github.com/renathossain/network_load_balancer.git

# shutdown properly to save the state
sudo shutdown -h now
```

- Do the same for
	- AnisClient gets 10.0.0.3
	- LoadBalancer gets 10.0.0.4
	- Server1 gets 10.0.0.5
	- Server2 gets 10.0.0.6
	- Server3 gets 10.0.0.7
## Python Flask Implementation
The Python Implementation for the load-balancer uses the flask library to make backend requests between client, load-balancer and servers. The topology of the load-balancer network is encoded in the yaml config file \[See Next Section], and read into the balancer.py and server.py scripts. 
### balancer.py
Specification:  `python3 balancer.py [CONFIG_PATH]`
If no argument is provided, will default to 'config.yaml'

This python script implements the load balancer, which is run on the 'LoadBalancer' node in the gns3 (ip=10.0.0.4). A server is run which listens for client requests to specific services e.g. "http://10.0.0.4:5000/service1" would be a request for 'service1'. 

The Balancer uses Weighted Round Robin algorithm (WRR) for each service, using weights for the allocated servers based on the specified config file. WRR distributes requests between allocated servers in a repeated order such that each server receives its weight in requests per repetition. For example, suppose that server 1 uses all 3 servers with the following weights:
```
  - host: service1
    servers:
      - port: 5000
        ip: 10.0.0.5
        weight: 1
      - port: 5000
        ip: 10.0.0.6
        weight: 2
      - port: 5000
        ip: 10.0.0.7
        weight: 3
```
(as specified in config2.yaml)

In this case, the round robin would iterate every 1 + 2 + 3 = 6 requests. An iterator would keep track of the the current position of the round robin (resetting to 0 after every 6th request), and its value would determine the requested server, as such:

- Request 1: 10.0.0.5
- Request 2: 10.0.0.6
- Request 3: 10.0.0.6
- Request 4: 10.0.0.7
- Request 5: 10.0.0.7
- Request 6: 10.0.0.7

The load balancer redirects the request to the server, and relays the reply back to the approrpiate client.
### server.py
Specification: `python3 server.py [SERVER_NAME] [CONFIG_PATH]` 

This script handles the implementation of the server, and can be run from any of the server gns nodes (10.0.0.5, 10.0.0.6, 10.0.0.7). It will accept requests python3 server.py [SERVER_NAME] [CONFIG_PATH] only from the load balancer (will 404 for any other sender) and perform service requests based on the services provided in the config file.
### client.py
Specification: `python3 client.py [REQUEST_RATE_PER_MIN] [SERVICE_NAME] [NUMBER_OF_REQUESTS]`

Run from the client nodes in gns3, will randomly make requests to the load balancer based on the specified SERVICE_NAME, and follows a Poisson Distribution, will continue to request NUMBER_OF_REQUESTS times.
## Config file
We used 3 files for testing:
- config.yaml file
Includes 1 service hosted by server1(weight 1), and server2(weight2)
- config2.yaml file
Includes 3 services:
	- service1 hosted by server1(weight 1), server2(weight2), server3(weight3)
	- service2 hosted by server1(weight 1), server2(weight2)
	- service3 hosted by server1(weight 1)
- config3.yaml
Includes 3 services each in their separate server (no load balancing advantage).

This is a very flexible program, custom configs can be written for different number of services and servers that offer them.
## Results From Running the Commands
Server1:
```
debian@debian:~/network_load_balancer$ python3 server.py server1 config2.yaml
10.0.0.5
['10.0.0.5', '10.0.0.6', '10.0.0.7']
['10.0.0.5', '10.0.0.6']
['10.0.0.5']
Hi, I'm server1, I handle ['service1', 'service2', 'service3'], awaiting load_balancer 10.0.0.4
 * Serving Flask app 'server'
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://10.0.0.5:5000
Press CTRL+C to quit
10.0.0.4 - - [11/Dec/2023 00:30:14] "GET /service1 HTTP/1.1" 200 -
10.0.0.4 - - [11/Dec/2023 00:30:17] "GET /service2 HTTP/1.1" 200 -
10.0.0.4 - - [11/Dec/2023 00:30:25] "GET /service2 HTTP/1.1" 200 -
10.0.0.4 - - [11/Dec/2023 00:30:34] "GET /service1 HTTP/1.1" 200 -
10.0.0.4 - - [11/Dec/2023 00:34:15] "GET /service3 HTTP/1.1" 200 -
10.0.0.4 - - [11/Dec/2023 00:34:16] "GET /service3 HTTP/1.1" 200 -
10.0.0.4 - - [11/Dec/2023 00:34:17] "GET /service3 HTTP/1.1" 200 -
```
Server2:
```
debian@debian:~/network_load_balancer$ python3 server.py server2 config2.yaml
10.0.0.6
['10.0.0.5', '10.0.0.6', '10.0.0.7']
['10.0.0.5', '10.0.0.6']
['10.0.0.5']
Hi, I'm server2, I handle ['service1', 'service2'], awaiting load_balancer 10.0.0.4
 * Serving Flask app 'server'
 * Debug mode: off, which configures 3 services.
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://10.0.0.6:5000
Press CTRL+C to quit
10.0.0.4 - - [11/Dec/2023 00:30:15] "GET /service1 HTTP/1.1" 200 -
10.0.0.4 - - [11/Dec/2023 00:30:18] "GET /service2 HTTP/1.1" 200 -
10.0.0.4 - - [11/Dec/2023 00:30:19] "GET /service1 HTTP/1.1" 200 -
10.0.0.4 - - [11/Dec/2023 00:30:24] "GET /service2 HTTP/1.1" 200 -
10.0.0.4 - - [11/Dec/2023 00:30:27] "GET /service2 HTTP/1.1" 200 -
10.0.0.4 - - [11/Dec/2023 00:30:31] "GET /service2 HTTP/1.1" 200 -
10.0.0.4 - - [11/Dec/2023 00:30:44] "GET /service1 HTTP/1.1" 200 -
10.0.0.4 - - [11/Dec/2023 00:30:49] "GET /service1 HTTP/1.1" 200 -
```
Server3:
```
debian@debian:~/network_load_balancer$ python3 server.py server3 config2.yaml
10.0.0.7
['10.0.0.5', '10.0.0.6', '10.0.0.7']
['10.0.0.5', '10.0.0.6']
['10.0.0.5']
Hi, I'm server3, I handle ['service1'], awaiting load_balancer 10.0.0.4
 * Serving Flask app 'server'
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://10.0.0.7:5000
Press CTRL+C to quit
10.0.0.4 - - [11/Dec/2023 00:30:20] "GET /service1 HTTP/1.1" 200 -
10.0.0.4 - - [11/Dec/2023 00:30:28] "GET /service1 HTTP/1.1" 200 -
10.0.0.4 - - [11/Dec/2023 00:30:33] "GET /service1 HTTP/1.1" 200 -
10.0.0.4 - - [11/Dec/2023 00:30:51] "GET /service1 HTTP/1.1" 200 -
10.0.0.4 - - [11/Dec/2023 00:30:52] "GET /service1 HTTP/1.1" 200 -
10.0.0.4 - - [11/Dec/2023 00:31:00] "GET /service1 HTTP/1.1" 200 -
```
LoadBalancer:
```
debian@debian:~/network_load_balancer$ python3 balancer.py config2.yaml
{'hosts': [{'host': 'service1', 'servers': [{'port': 5000, 'ip': '10.0.0.5', 'weight': 1}, {'port': 5000, 'ip': '10.0.0.6', 'weight': 2}, {'port': 5000, 'ip': '10.0.0.7', 'weight': 3}], 'n': 6, 'curr': 0}, {'host': 'service2', 'servers': [{'port': 5000, 'ip': '10.0.0.5', 'weight': 1}, {'port': 5000, 'ip': '10.0.0.6', 'weight': 2}], 'n': 3, 'curr': 0}, {'host': 'service3', 'servers': [{'port': 5000, 'ip': '10.0.0.5', 'weight': 1}], 'n': 1, 'curr': 0}]}
 * Serving Flask app 'balancer'
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://10.0.0.4:5000
Press CTRL+C to quit
10.0.0.2 - - [11/Dec/2023 00:30:14] "GET /service1 HTTP/1.1" 200 -
10.0.0.2 - - [11/Dec/2023 00:30:15] "GET /service1 HTTP/1.1" 200 -
10.0.0.3 - - [11/Dec/2023 00:30:17] "GET /service2 HTTP/1.1" 200 -
10.0.0.3 - - [11/Dec/2023 00:30:18] "GET /service2 HTTP/1.1" 200 -
10.0.0.2 - - [11/Dec/2023 00:30:19] "GET /service1 HTTP/1.1" 200 -
10.0.0.2 - - [11/Dec/2023 00:30:20] "GET /service1 HTTP/1.1" 200 -
10.0.0.3 - - [11/Dec/2023 00:30:24] "GET /service2 HTTP/1.1" 200 -
10.0.0.3 - - [11/Dec/2023 00:30:25] "GET /service2 HTTP/1.1" 200 -
10.0.0.3 - - [11/Dec/2023 00:30:27] "GET /service2 HTTP/1.1" 200 -
10.0.0.2 - - [11/Dec/2023 00:30:28] "GET /service1 HTTP/1.1" 200 -
10.0.0.3 - - [11/Dec/2023 00:30:31] "GET /service2 HTTP/1.1" 200 -
10.0.0.2 - - [11/Dec/2023 00:30:33] "GET /service1 HTTP/1.1" 200 -
10.0.0.2 - - [11/Dec/2023 00:30:34] "GET /service1 HTTP/1.1" 200 -
10.0.0.2 - - [11/Dec/2023 00:30:44] "GET /service1 HTTP/1.1" 200 -
10.0.0.2 - - [11/Dec/2023 00:30:49] "GET /service1 HTTP/1.1" 200 -
10.0.0.2 - - [11/Dec/2023 00:30:51] "GET /service1 HTTP/1.1" 200 -
10.0.0.2 - - [11/Dec/2023 00:30:52] "GET /service1 HTTP/1.1" 200 -
10.0.0.2 - - [11/Dec/2023 00:31:00] "GET /service1 HTTP/1.1" 200 -
10.0.0.2 - - [11/Dec/2023 00:34:15] "GET /service3 HTTP/1.1" 200 -
10.0.0.2 - - [11/Dec/2023 00:34:16] "GET /service3 HTTP/1.1" 200 -
10.0.0.2 - - [11/Dec/2023 00:34:17] "GET /service3 HTTP/1.1" 200 -
```
RenatClient:
```
debian@debian:~/network_load_balancer$ python3 client.py 20 service1 12
<Response [200]>
<Response [200]>
<Response [200]>
<Response [200]>
<Response [200]>
<Response [200]>
<Response [200]>
<Response [200]>
<Response [200]>
<Response [200]>
<Response [200]>
<Response [200]>
debian@debian:~/network_load_balancer$ python3 client.py 20 service3 3
<Response [200]>
<Response [200]>
<Response [200]>
```
AnisClient:
```
debian@debian:~/network_load_balancer$ pveryython3 client.py 20 service2 6
<Response [200]>
<Response [200]>
<Response [200]>
<Response [200]>
<Response [200]>
<Response [200]>
```
## Discussion
From the code above, we let RenatClient request service1 12 times and service3 3 times, and we let AnisClient request service2 6 times. We let the servers and load balancer use the config2.yaml file, which results in this assignment of requests:
- service1's 12 requests will be distributed:
    - 2 for server1
    - 4 for server2
	- 6 for server3
- service2's 6 requests will be distributed:
	- 2 for server1
	- 4 for server2
- service3's 3 requests will be distributed:
	- 3 for server1


So in total there are 18 requests with this distribution: 
- server1 should get `2 + 2 + 3 = 7` requests.
- server2 should get `4 + 4 = 8` requests.
- server3 should get `6` requests.

This is fairly balanced and matches the number of lines `10.0.0.4 - - [11/Dec/2023 00:30:14] "GET /service HTTP/1.1" 200 -` that are printed for the each of the servers in the results above.

Without load balancing, if we had serviceN simply assigned to serverN. Server1 would get 12 requests, server2 would get 6 and server3 would get 3 requests. Server1 would be overutilized and server3 would be underutilized.
# Conclusion and Lesson
In conclusion, we have achieved our goal of creating a flexible network load balancer in gns3, that uses a round robin algorithm implemented in Python using the Flask library. We have learned a lot about configuring topologies in gns3 using custom appliances (Debian and Cisco Routers). We were able to achieve the results that we wanted. Future improvements to this project can include making real services (for example, transactions, multiplayer games, etc.) as well as better and more dynamic load balancing algorithms other than round robin.