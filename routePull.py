
import requests

def routeGet():

    url = "https://datamall2.mytransport.sg/ltaodataservice/BusRoutes?$skip=8500"

    payload = {}
    headers = {
    'AccountKey': 'nGsExLUQTqOhMSxoCHam8g=='
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    data = response.json()['value']

    # print(type(response.text))

    route_190 = [r for r in data if r["ServiceNo"] == "190" and r['Direction'] == 2]

    route_190.sort(key=lambda r: (r["StopSequence"]))

    for i in range(len(route_190)):
        route_190[i]['StopSequence'] = i

    return route_190

