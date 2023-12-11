import time
import requests
import sys
import random

LOAD_BALANCER_IP = '10.0.0.4:5000'

def getPoissant(lambda_val: float):
    u = random.random()
    return -lambda_val * (random._log(u))



limit = None
if __name__ == '__main__':

    assert len(sys.argv) > 2, "Not enough arguments. Usage: client.py CONFIG_PATH REQUESTS_PER_MIN SERVICE NUM_REQUESTS"
    req_per_min = sys.argv[1]
    service = sys.argv[2]

    if len(sys.argv) > 3:
        limit = int(sys.argv[3])
    



    lambda_val = 60. / float(req_per_min)

    while(limit == None or limit > 0):
        response = ""
        try:
            response = requests.get(f'http://{LOAD_BALANCER_IP}/{service}', timeout=4)
        except: 
            print("Timeout..")

        print(response)
        time.sleep(getPoissant(lambda_val))
        
        limit -= 1


        
    
