from config import *
import requests
from datetime import datetime
import time
import csv
from twilio.rest import Client

# config.py contains definitions for these variables:
    # key
    # url
    # origin
    # destination
    # waypoints_list
    # account_sid
    # auth_token
    # to_number
    # from_number


def request_route(waypoints):
    params = {'origin':origin, 'destination':destination, 'waypoints':waypoints, 'alternatives':'false','departure_time':'now', 'key': key}
    response = requests.request("GET", url, params=params)
    response = response.json()
    return response

def parse_response(response):
    return [response['routes'][0]['summary'], response['routes'][0]['legs'][0]['duration']['value'], response['routes'][0]['legs'][0]['duration_in_traffic']['value'], response['routes'][0]['legs'][0]['distance']['value']]
    
def get_responses(waypoints_list):
    return {v : parse_response(request_route(waypoints_list[v])) for i,v in enumerate(waypoints_list)}

def log_routes(current_routes):
    with open('routes_log.csv', 'a') as csvfile:
        writer = csv.writer(csvfile)
        current_datetime = str(datetime.now())
        for i,v in enumerate(current_routes):
            writer.writerow([current_datetime, v, current_routes[v][0], current_routes[v][1],current_routes[v][2]])

def make_recommendation(current_routes):
    if  current_routes['left then freeway'][2] > current_routes['right to backroads'][2]:
        return True, 'take backroads'
    elif current_routes['right then freeway'][2] < current_routes['left then freeway'][2]:
        return True, 'go right to freeway'
    else:
        return False, 'go left to freeway'

def send_alert(recommendation):
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        to=to_number, 
        from_=from_number,
        body=recommendation)

starttime=time.time()
while time.strftime('%H',time.localtime()) == '23' or time.strftime('%H',time.localtime()) == '00':
    current_routes = get_responses(waypoints_list)
    log_routes(current_routes)
    recommendation = make_recommendation(current_routes)
    if recommendation[0] == True:
        send_alert(recommendation[1])
        break

    time.sleep(300.0 - ((time.time() - starttime) % 300.0))


